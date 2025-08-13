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
MAX_CACHE_SIZE = 1500
TEMP_FILE_PREFIX = "temp_"
MAX_RETRIES = 3

# ===== GLOBALS ===== #
processed_files = set()
media_processor = None

# ===== FILE ID UTILITIES ===== #
def unpack_new_file_id(file_id: str) -> Tuple[str, Optional[bytes]]:
    """Modern Pyrogram file ID unpacking"""
    try:
        decoded = FileId.decode(file_id)
        # New Pyrogram versions use different attribute names
        if hasattr(decoded, 'file_id'):  # Older versions
            return decoded.file_id, decoded.file_reference
        elif hasattr(decoded, 'media_id'):  # Newer versions
            return str(decoded.media_id), decoded.file_reference
        else:
            raise ValueError("Unsupported FileId structure")
    except Exception as e:
        raise ValueError(f"Failed to decode file ID: {str(e)}")

# ===== MEDIA PROCESSOR ===== #
class MediaProcessor:
    async def process_thumbnail(self, client: Client, thumb: object) -> Optional[str]:
        """Reliable thumbnail processing"""
        for attempt in range(MAX_RETRIES):
            try:
                thumb_path = f"{TEMP_FILE_PREFIX}{hashlib.md5(thumb.file_id.encode()).hexdigest()[:8]}.jpg"
                if os.path.exists(thumb_path):
                    return thumb_path
                    
                await client.download_media(
                    thumb.file_id,
                    file_name=thumb_path
                )
                return thumb_path
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                if attempt == MAX_RETRIES - 1:
                    return None
                await asyncio.sleep(1)

# ===== MAIN HANDLER ===== #
media_processor = MediaProcessor()

async def process_media(client: Client, message: Message):
    """Robust media processing with enhanced error handling"""
    try:
        # Media detection with fallbacks
        media = (
            message.document or 
            message.video or 
            message.audio or 
            message.photo
        )
        if not media:
            return

        # Memory management
        if len(processed_files) > MAX_CACHE_SIZE:
            processed_files.clear()

        # Duplicate prevention
        file_hash = hashlib.sha256(media.file_id.encode()).hexdigest()
        if file_hash in processed_files:
            return
        processed_files.add(file_hash)

        # Metadata extraction
        file_name = re.sub(r'[^\w\s\-\.]', '', getattr(media, "file_name", "Unnamed"))
        file_size = humanbytes(getattr(media, "file_size", 0))
        duration = time_formatter(getattr(media, "duration", 0))

        # File ID processing with retries
        file_id = None
        for attempt in range(MAX_RETRIES):
            try:
                file_id, _ = unpack_new_file_id(media.file_id)
                break
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise
                await asyncio.sleep(1)

        # Thumbnail handling
        thumb_path = None
        if hasattr(media, "thumbs") and media.thumbs:
            thumb_path = await media_processor.process_thumbnail(client, media.thumbs[0])

        # Content delivery
        buttons = [[
            InlineKeyboardButton("📥 Download", 
            url=f"https://t.me/{temp.U_NAME}?start={file_id}")
        ]]

        if thumb_path:
            await client.send_photo(
                chat_id=UPDATE_CHANNEL,
                photo=thumb_path,
                caption=build_caption(media, file_name, file_size, duration),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        else:
            await client.copy_message(
                chat_id=UPDATE_CHANNEL,
                from_chat_id=message.chat.id,
                message_id=message.id,
                caption=build_caption(media, file_name, file_size, duration),
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    except FloodWait as e:
        await asyncio.sleep(e.value + 2)
    except Exception as e:
        await log_error(client, f"Error processing {file_name or 'unknown file'}", e)
    finally:
        if thumb_path and os.path.exists(thumb_path):
            try:
                os.remove(thumb_path)
            except:
                pass

# ===== HELPER FUNCTIONS ===== #
def build_caption(media, file_name, file_size, duration) -> str:
    """Dynamic caption builder"""
    media_type = (
        "Video" if message.video else
        "Audio" if message.audio else
        "Document" if message.document else
        "Photo" if message.photo else "Media"
    )
    return (
        f"✨ **New {media_type} Upload** ✨\n\n"
        f"📌 **Name:** `{file_name}`\n"
        f"📦 **Size:** `{file_size}`\n"
        f"⏱️ **Duration:** `{duration}`\n\n"
        f"⬇️ **Download Below** ⬇️"
    )

async def log_error(client: Client, context: str, error: Exception):
    """Enhanced error logging"""
    error_msg = (
        f"🚨 **Error**: {context}\n\n"
        f"• **Type**: `{type(error).__name__}`\n"
        f"• **Message**: `{str(error)[:500]}`\n\n"
        f"⚠️ **Traceback**:\n```{traceback.format_exc()[:3000]}```"
    )
    await client.send_message(LOG_CHANNEL, error_msg)

# ===== HANDLERS ===== #
@Client.on_message(filters.chat(CHANNELS) & (
    filters.document | 
    filters.video | 
    filters.audio |
    filters.photo
))
async def media_handler(client: Client, message: Message):
    await process_media(client, message)

if __name__ == "__main__":
    print("✅ Bot utilities initialized")
