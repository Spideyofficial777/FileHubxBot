#!/usr/bin/env python3
import os
import re
import time
import hashlib
import asyncio
import aiofiles
import traceback
from datetime import datetime
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from config import *

# Memory management
MAX_CACHE_SIZE = 1000
processed_files = set()

class MediaUtils:
    @staticmethod
    def humanbytes(size: int) -> str:
        """Convert bytes to human-readable format"""
        for unit in ["", "K", "M", "G", "T"]:
            if size < 1024:
                return f"{size:.2f}{unit}B"
            size /= 1024
        return f"{size:.2f}PB"

    @staticmethod
    def time_formatter(seconds: int) -> str:
        """Convert seconds to H:M:S format"""
        return time.strftime('%H:%M:%S', time.gmtime(seconds)) if seconds else "N/A"

    @staticmethod
    async def generate_file_hash(file_id: str) -> str:
        """Generate unique file hash"""
        return hashlib.md5(file_id.encode()).hexdigest()

    @staticmethod
    def detect_quality(filename: str) -> str:
        """Detect media quality from filename"""
        quality_map = {
            "4K": ["4k", "2160p", "uhd"],
            "1080p": ["1080p", "fullhd"],
            "720p": ["720p", "hd"],
            "480p": ["480p", "sd"]
        }
        lower_name = filename.lower()
        return next((q for q, terms in quality_map.items() if any(t in lower_name for t in terms)), "Unknown")

async def process_media(client: Client, message: Message):
    """Process media message and forward to channel"""
    try:
        start_time = time.time()
        
        # Get the correct media attribute
        if message.document:
            media = message.document
            media_type = "Document"
        elif message.video:
            media = message.video
            media_type = "Video"
        elif message.audio:
            media = message.audio
            media_type = "Audio"
        else:
            return

        # Memory management
        if len(processed_files) > MAX_CACHE_SIZE:
            processed_files.clear()

        file_hash = await MediaUtils.generate_file_hash(media.file_id)
        if file_hash in processed_files:
            return
        processed_files.add(file_hash)

        # Extract metadata
        file_name = re.sub(r'[^\w\s\-\.]', '', getattr(media, "file_name", "Unnamed"))
        file_size = MediaUtils.humanbytes(getattr(media, "file_size", 0))
        duration = MediaUtils.time_formatter(getattr(media, "duration", 0))
        quality = MediaUtils.detect_quality(file_name)

        # Prepare caption
        caption = (
            f"✨ **New {media_type} Upload** ✨\n\n"
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

        # Forward to channel
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

        # Log processing time
        proc_time = time.time() - start_time
        await db.log_processing(file_id, proc_time, media.file_size)

    except FloodWait as e:
        await asyncio.sleep(e.value + 2)
    except Exception as e:
        error_msg = f"🚨 Error processing media:\n{str(e)[:2000]}"
        await client.send_message(LOG_CHANNEL, error_msg)

# Message handlers
@Client.on_message(filters.chat(CHANNELS) & filters.document)
@Client.on_message(filters.chat(CHANNELS) & filters.video)
@Client.on_message(filters.chat(CHANNELS) & filters.audio)
async def media_handler(client: Client, message: Message):
    await process_media(client, message)

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
