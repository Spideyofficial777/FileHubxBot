#!/usr/bin/env python3
import os
import re
import time
import hashlib
import asyncio
import aiofiles
import traceback
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from config import *

# ===== CONSTANTS ===== #
MAX_CACHE_SIZE = 1500  # Increased cache size
MAX_THUMB_SIZE = (1024, 1024)  # Thumbnail resolution limit
TEMP_FILE_PREFIX = "temp_"

# ===== GLOBALS ===== #
processed_files = set()
last_cleanup = time.time()

# ===== CORE UTILITIES ===== #
class MediaUtils:
    @staticmethod
    def humanbytes(size: int) -> str:
        """Optimized byte size formatter"""
        for unit in ["", "K", "M", "G", "T"]:
            if size < 1024:
                return f"{size:.2f}{unit}B"
            size /= 1024
        return f"{size:.2f}PB"

    @staticmethod
    def time_formatter(seconds: int) -> str:
        """Efficient time formatting"""
        return time.strftime('%H:%M:%S', time.gmtime(seconds)) if seconds else "N/A"

    @staticmethod
    async def generate_file_hash(file_id: str) -> str:
        """Fast file hashing with collision protection"""
        return hashlib.sha256(file_id.encode()).hexdigest()

    @staticmethod
    def detect_quality(filename: str) -> str:
        """Enhanced quality detection with more formats"""
        quality_map = {
            "8K": ["8k", "4320p", "uhd2"],
            "4K": ["4k", "2160p", "uhd"],
            "QHD": ["1440p", "qhd"],
            "1080p": ["1080p", "fullhd", "fhd"],
            "720p": ["720p", "hd"],
            "480p": ["480p", "sd"],
            "360p": ["360p"],
            "240p": ["240p"]
        }
        lower_name = filename.lower()
        return next((q for q, terms in quality_map.items() if any(t in lower_name for t in terms)), "Unknown")

    @staticmethod
    def clean_filename(filename: str) -> str:
        """Advanced filename cleaning"""
        if not filename:
            return "Unnamed"
        return re.sub(r'[^\w\s\-\.\(\)\[\]]', '', filename).strip()

# ===== FILE HANDLING ===== #
def unpack_new_file_id(file_id: str) -> Tuple[str, bytes]:
    """Robust file ID unpacking with error handling"""
    try:
        decoded = FileId.decode(file_id)
        return decoded.file_id, decoded.file_reference
    except Exception as e:
        raise ValueError(f"Invalid file ID: {str(e)}")

async def cleanup_temp_files():
    """Periodic cleanup of temporary files"""
    global last_cleanup
    if time.time() - last_cleanup > 3600:  # Every hour
        for file in Path(".").glob(f"{TEMP_FILE_PREFIX}*"):
            try:
                file.unlink()
            except:
                pass
        last_cleanup = time.time()

# ===== MEDIA PROCESSOR ===== #
class MediaProcessor:
    def __init__(self):
        self.thumbnail_cache = {}

    async def process_thumbnail(self, client: Client, thumb: object) -> Optional[str]:
        """Optimized thumbnail processing with caching"""
        thumb_hash = hashlib.md5(thumb.file_id.encode()).hexdigest()
        
        if thumb_hash in self.thumbnail_cache:
            cached_path = self.thumbnail_cache[thumb_hash]
            if os.path.exists(cached_path):
                return cached_path

        try:
            thumb_path = await client.download_media(
                thumb.file_id,
                file_name=f"{TEMP_FILE_PREFIX}{thumb_hash[:8]}.jpg"
            )
            
            # Basic validation
            if os.path.getsize(thumb_path) > 5 * 1024 * 1024:  # 5MB limit
                os.remove(thumb_path)
                return None
                
            self.thumbnail_cache[thumb_hash] = thumb_path
            return thumb_path
            
        except Exception as e:
            print(f"Thumbnail processing error: {e}")
            return None

# ===== MAIN HANDLER ===== #
media_processor = MediaProcessor()

async def process_media(client: Client, message: Message):
    """Enhanced media processing pipeline"""
    try:
        await cleanup_temp_files()
        start_time = time.time()
        
        # Media type detection
        media = None
        if message.document:
            media = message.document
            media_type = "Document"
        elif message.video:
            media = message.video
            media_type = "Video"
        elif message.audio:
            media = message.audio
            media_type = "Audio"
        
        if not media:
            return

        # Memory management
        if len(processed_files) > MAX_CACHE_SIZE:
            processed_files.clear()

        # Duplicate prevention
        file_hash = await MediaUtils.generate_file_hash(media.file_id)
        if file_hash in processed_files:
            return
        processed_files.add(file_hash)

        # Metadata extraction
        file_name = MediaUtils.clean_filename(getattr(media, "file_name", ""))
        file_size = MediaUtils.humanbytes(getattr(media, "file_size", 0))
        duration = MediaUtils.time_formatter(getattr(media, "duration", 0))
        quality = MediaUtils.detect_quality(file_name)

        # Prepare content
        caption = (
            f"✨ **New {media_type} Upload** ✨\n\n"
            f"📌 **Name:** `{file_name}`\n"
            f"📦 **Size:** `{file_size}`\n"
            f"⏱️ **Duration:** `{duration}`\n"
            f"🖼️ **Quality:** `{quality}`\n\n"
            f"⬇️ **Download Below** ⬇️"
        )

        # Thumbnail handling
        thumb_path = None
        if hasattr(media, "thumbs") and media.thumbs:
            thumb_path = await media_processor.process_thumbnail(client, media.thumbs[0])

        # File ID processing
        try:
            file_id, file_ref = unpack_new_file_id(media.file_id)
            buttons = [[
                InlineKeyboardButton("📥 Direct Download", 
                url=f"https://t.me/{temp.U_NAME}?start={file_id}")
            ]]
            
            # Content delivery
            if thumb_path:
                await client.send_photo(
                    chat_id=UPDATE_CHANNEL,
                    photo=thumb_path,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            else:
                await client.copy_message(
                    chat_id=UPDATE_CHANNEL,
                    from_chat_id=message.chat.id,
                    message_id=message.id,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

            # Logging
            proc_time = time.time() - start_time
            await db.log_processing(file_id, proc_time, media.file_size)

        except Exception as e:
            raise e
        finally:
            # Always clean up
            if thumb_path and os.path.exists(thumb_path):
                try:
                    os.remove(thumb_path)
                except:
                    pass

    except FloodWait as e:
        await asyncio.sleep(e.value + 2)
    except Exception as e:
        error_msg = (f"🚨 **Processing Error**\n\n"
                    f"• File: `{file_name or 'Unknown'}`\n"
                    f"• Error: `{str(e)[:1000]}`\n\n"
                    f"⚠️ Check logs for details")
        await client.send_message(LOG_CHANNEL, error_msg)
        traceback.print_exc()

# ===== HANDLERS ===== #
@Client.on_message(filters.chat(CHANNELS) & (filters.document | filters.video | filters.audio))
async def media_handler(client: Client, message: Message):
    await process_media(client, message)

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def show_stats(client: Client, message: Message):
    """Enhanced stats command with more metrics"""
    stats = await db.get_performance_stats()
    response = (
        "📊 **Bot Performance Report**\n\n"
        f"• **Files Processed:** `{stats['total']:,}`\n"
        f"• **Processing Speed:** `{stats['avg_speed']:.2f}s/file`\n"
        f"• **Active Cache:** `{len(processed_files):,}/{MAX_CACHE_SIZE}`\n"
        f"• **Memory Usage:** `{stats.get('memory', 'N/A')}`\n"
        f"• **Uptime:** `{MediaUtils.time_formatter(stats['uptime'])}`\n\n"
        f"🔄 **Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await message.reply(response)

# ===== STARTUP ===== #
async def startup_cleanup():
    """Initial cleanup and checks"""
    print("🚀 Starting up...")
    await cleanup_temp_files()
    processed_files.clear()
    print("✅ Cleanup complete")

if __name__ == "__main__":
    asyncio.run(startup_cleanup())
