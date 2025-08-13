#!/usr/bin/env python3
import os
import re
import time
import hashlib
import asyncio
import aiofiles
import traceback
from datetime import datetime, timedelta
from typing import Dict, Optional
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from config import *

# Memory management
MAX_CACHE_SIZE = 1000
processed_files = set()

# ==================== CORE UTILITIES ==================== #
class MediaUtils:
    @staticmethod
    def humanbytes(size: int) -> str:
        """Optimized byte converter"""
        for unit in ["", "K", "M", "G", "T"]:
            if size < 1024:
                return f"{size:.2f}{unit}B"
            size /= 1024
        return f"{size:.2f}PB"

    @staticmethod
    def time_formatter(seconds: int) -> str:
        """Fast time formatting"""
        return time.strftime('%H:%M:%S', time.gmtime(seconds)) if seconds else "N/A"

    @classmethod
    async def generate_file_hash(cls, file_id: str) -> str:
        """Memory-efficient hashing"""
        return hashlib.md5(file_id.encode()).hexdigest()  # Using md5 for speed

    @classmethod
    def detect_quality(cls, filename: str) -> str:
        """Enhanced quality detection"""
        quality_rules = {
            "8K": ["8k", "4320p", "uhd2"],
            "4K": ["4k", "2160p", "uhd"],
            "1080p": ["1080p", "fullhd"],
            "720p": ["720p", "hd"],
            "480p": ["480p", "sd"]
        }
        lower_name = filename.lower()
        return next((q for q, terms in quality_rules.items() if any(t in lower_name for t in terms)), "Unknown")

# ==================== MEDIA PROCESSOR ==================== #
class MediaProcessor:
    def __init__(self):
        self.thumbnail_cache = {}
        self.last_cleanup = time.time()

    async def process_thumbnail(self, thumb_path: str) -> Optional[str]:
        """Optimized thumbnail processor with cache"""
        if thumb_path in self.thumbnail_cache:
            return self.thumbnail_cache[thumb_path]

        try:
            async with aiofiles.open(thumb_path, 'rb') as f:
                content = await f.read()
            
            # Simple watermark adding without PIL
            watermarked = self._add_watermark(content)
            output_path = f"thumb_{os.path.basename(thumb_path)}"
            
            async with aiofiles.open(output_path, 'wb') as f:
                await f.write(watermarked)
            
            self.thumbnail_cache[thumb_path] = output_path
            return output_path
        except Exception:
            return None

    def _add_watermark(self, image_data: bytes) -> bytes:
        """Lightweight watermarking (placeholder)"""
        return image_data  # Implement your watermark logic here

    async def cleanup(self):
        """Regular cache cleanup"""
        if time.time() - self.last_cleanup > 3600:  # Every hour
            self.thumbnail_cache.clear()
            self.last_cleanup = time.time()

# ==================== MAIN HANDLER ==================== #
media_processor = MediaProcessor()

@Client.on_message(filters.chat(CHANNELS) & (filters.document | filters.video | filters.audio))
async def handle_media(client: Client, message: Message):
    try:
        start_time = time.time()
        media = getattr(message, message.media.value)
        
        # Memory management
        if len(processed_files) > MAX_CACHE_SIZE:
            processed_files.clear()

        # Generate unique hash
        file_hash = await MediaUtils.generate_file_hash(media.file_id)
        if file_hash in processed_files:
            return
        
        processed_files.add(file_hash)

        # Extract metadata
        file_name = re.sub(r'[^\w\s\-\.]', '', getattr(media, "file_name", "Unnamed"))
        file_size = MediaUtils.humanbytes(getattr(media, "file_size", 0))
        duration = MediaUtils.time_formatter(getattr(media, "duration", 0))
        quality = MediaUtils.detect_quality(file_name)

        # Prepare message
        caption = (
            f"✨ **New {media.media.value.capitalize()}** ✨\n\n"
            f"📌 **Name:** `{file_name}`\n"
            f"📦 **Size:** `{file_size}`\n"
            f"⏱️ **Duration:** `{duration}`\n"
            f"🖼️ **Quality:** `{quality}`\n\n"
            f"⬇️ **Download Below** ⬇️"
        )

        # Handle thumbnail
        thumb_path = None
        if hasattr(media, "thumbs") and media.thumbs:
            thumb_path = await client.download_media(
                media.thumbs[0].file_id,
                file_name=f"temp_{file_hash[:8]}.jpg"
            )
            thumb_path = await media_processor.process_thumbnail(thumb_path)

        # Send to channel
        try:
            file_id, _ = unpack_new_file_id(media.file_id)
            buttons = [[InlineKeyboardButton("📥 Download", url=f"https://t.me/{temp.U_NAME}?start={file_id}")]]
            
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
        finally:
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)
                
        # Log performance
        proc_time = time.time() - start_time
        await db.log_processing(file_id, proc_time, media.file_size)

    except FloodWait as e:
        await asyncio.sleep(e.value + 2)
    except Exception as e:
        error_msg = f"🚨 Error processing {getattr(media, 'file_name', 'unknown')}:\n{str(e)[:2000]}"
        await client.send_message(LOG_CHANNEL, error_msg)

# ==================== COMMANDS ==================== #
@Client.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def show_stats(client, message):
    stats = await db.get_performance_stats()
    await message.reply(
        "📊 **Bot Statistics**\n\n"
        f"• Files Processed: `{stats['total']}`\n"
        f"• Avg Speed: `{stats['avg_speed']:.2f}s/file`\n"
        f"• Cache Size: `{len(processed_files)}`\n"
        f"• Uptime: `{MediaUtils.time_formatter(stats['uptime'])}`"
    )
