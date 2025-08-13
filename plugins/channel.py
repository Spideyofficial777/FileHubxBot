#!/usr/bin/env python3
import os
import re
import time
import hashlib
import asyncio
import aiofiles
import traceback
from datetime import datetime
from typing import Optional, Tuple, Union
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from config import *

# ===== CONSTANTS ===== #
MAX_CACHE_SIZE = 2000
TEMP_FILE_PREFIX = "temp_"
MAX_RETRIES = 3
CACHE_CLEAN_INTERVAL = 3600  # 1 hour

# ===== UTILITY FUNCTIONS (DEFINED FIRST) ===== #
def humanbytes(size: Union[int, float]) -> str:
    """Convert bytes to human-readable format"""
    for unit in ["", "K", "M", "G", "T"]:
        if abs(size) < 1024.0:
            return f"{size:.2f}{unit}B"
        size /= 1024.0
    return f"{size:.2f}PB"

def time_formatter(seconds: Union[int, float]) -> str:
    """Convert seconds to H:M:S format"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"

def clean_filename(filename: str) -> str:
    """Sanitize filename for safe use"""
    if not filename:
        return "Unnamed_File"
    return re.sub(r'[^\w\s\-\.]', '', filename).strip()[:128]

async def generate_file_hash(file_id: str) -> str:
    """Generate SHA-256 hash of file ID"""
    return hashlib.sha256(file_id.encode()).hexdigest()

# ===== FILE HANDLING ===== #
async def unpack_file_id(file_id: str) -> Tuple[str, Optional[bytes]]:
    """Universal file ID unpacker"""
    try:
        if hasattr(FileId, 'decode'):
            decoded = FileId.decode(file_id)
            file_unique_id = getattr(decoded, 'file_unique_id', None) or getattr(decoded, 'media_id', None)
            file_ref = getattr(decoded, 'file_reference', None)
            if file_unique_id:
                return str(file_unique_id), file_ref
        return file_id, None
    except Exception as e:
        raise ValueError(f"File ID decoding failed: {str(e)}")

# ===== MEDIA PROCESSOR CLASS ===== #
class MediaProcessor:
    def __init__(self):
        self.thumbnail_cache = {}
        self.last_cleanup = time.time()

    async def process_thumbnail(self, client: Client, thumb_obj) -> Optional[str]:
        """Download and cache thumbnails"""
        try:
            thumb_hash = hashlib.md5(thumb_obj.file_id.encode()).hexdigest()
            
            if thumb_hash in self.thumbnail_cache:
                cached_path = self.thumbnail_cache[thumb_hash]
                if os.path.exists(cached_path):
                    return cached_path

            thumb_path = f"{TEMP_FILE_PREFIX}{thumb_hash[:8]}.jpg"
            await client.download_media(thumb_obj.file_id, file_name=thumb_path)
            
            if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
                self.thumbnail_cache[thumb_hash] = thumb_path
                return thumb_path
            return None
            
        except Exception:
            return None

    async def cleanup(self):
        """Periodic cache cleanup"""
        if time.time() - self.last_cleanup > CACHE_CLEAN_INTERVAL:
            for path in list(self.thumbnail_cache.values()):
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except:
                    pass
            self.thumbnail_cache.clear()
            self.last_cleanup = time.time()

# ===== CORE FUNCTIONALITY ===== #
media_processor = MediaProcessor()
processed_files = set()

async def process_media(client: Client, message: Message):
    """Main media processing pipeline"""
    thumb_path = None
    file_name = "Unknown_File"
    
    try:
        await media_processor.cleanup()
        start_time = time.time()

        # Determine media type
        media = None
        media_type = "File"
        for attr in ['document', 'video', 'audio', 'photo']:
            if getattr(message, attr, None):
                media = getattr(message, attr)
                media_type = attr.capitalize()
                break
        
        if not media:
            return

        # Memory management
        if len(processed_files) > MAX_CACHE_SIZE:
            processed_files.clear()

        # Duplicate prevention
        file_hash = await generate_file_hash(media.file_id)
        if file_hash in processed_files:
            return
        processed_files.add(file_hash)

        # Extract metadata
        file_name = clean_filename(getattr(media, "file_name", ""))
        file_size = humanbytes(getattr(media, "file_size", 0))
        duration = time_formatter(getattr(media, "duration", 0))

        # Get file ID
        file_id, file_ref = await unpack_file_id(media.file_id)

        # Process thumbnail
        if hasattr(media, "thumbs") and media.thumbs:
            thumb_path = await media_processor.process_thumbnail(client, media.thumbs[0])

        # Prepare message
        caption = (
            f"✨ **New {media_type} Upload** ✨\n\n"
            f"📌 **Name:** `{file_name}`\n"
            f"📦 **Size:** `{file_size}`\n"
            f"⏱️ **Duration:** `{duration}`\n\n"
            f"⬇️ **Download Below** ⬇️"
        )
        
        buttons = [[
            InlineKeyboardButton("📥 Download", url=f"https://t.me/{temp.U_NAME}?start={file_id}")
        ]]

        # Deliver content
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

        # Log processing
        proc_time = time.time() - start_time
        await db.log_processing(file_id, proc_time, getattr(media, "file_size", 0))

    except FloodWait as e:
        await asyncio.sleep(e.value + 2)
    except Exception as e:
        await log_error(client, f"Processing {file_name}", e)
    finally:
        if thumb_path and os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except:
                pass

async def log_error(client: Client, context: str, error: Exception):
    """Error logging with traceback"""
    error_msg = (
        f"🚨 **Error**: {context}\n\n"
        f"• **Type**: `{type(error).__name__}`\n"
        f"• **Message**: `{str(error)[:500]}`\n\n"
        f"⚠️ **Traceback**:\n```{traceback.format_exc()[:3000]}```"
    )
    try:
        await client.send_message(LOG_CHANNEL, error_msg)
    except:
        pass

# ===== HANDLERS ===== #
@Client.on_message(filters.chat(CHANNELS) & (
    filters.document | 
    filters.video | 
    filters.audio |
    filters.photo
))
async def media_handler(client: Client, message: Message):
    await process_media(client, message)

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def show_stats(client: Client, message: Message):
    stats = await db.get_performance_stats()
    await message.reply(
        "📊 **Bot Performance**\n\n"
        f"• Files Processed: `{stats['total']:,}`\n"
        f"• Avg Speed: `{stats['avg_speed']:.2f}s/file`\n"
        f"• Cache Size: `{len(processed_files):,}`\n"
        f"• Uptime: `{time_formatter(stats['uptime'])}`"
    )

# ===== INITIALIZATION ===== #
async def initialize():
    """Startup tasks"""
    print("🚀 Starting media processor...")
    processed_files.clear()
    print("✅ System ready")

if __name__ == "__main__":
    asyncio.run(initialize())
