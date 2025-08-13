import os
import re
import time
import hashlib
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict
from PIL import Image, ImageDraw, ImageFont

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from config import *

# Memory optimization
processed_files = set()
MAX_MEMORY_USAGE = 500  # MB
last_mem_check = time.time()

# ===== Lightweight NSFW Detection ===== #
async def detect_nsfw_content(filename: str) -> bool:
    """Lightweight NSFW detection without heavy AI"""
    nsfw_keywords = {"xxx", "porn", "adult", "18+", "nsfw"}
    return any(kw in filename.lower() for kw in nsfw_keywords)

# ===== Memory Management ===== #
def check_memory_usage():
    """Check and clear memory if needed"""
    global last_mem_check
    if time.time() - last_mem_check > 60:  # Check every minute
        last_mem_check = time.time()
        # Clear processed files if memory is high
        if len(processed_files) > 1000:
            processed_files.clear()

# ===== Optimized Media Processing ===== #
async def analyze_media(media) -> Dict:
    """Memory-efficient media analysis"""
    check_memory_usage()
    
    file_name = re.sub(r'[^\w\s\-\.]', '', getattr(media, "file_name", "Unnamed"))
    
    return {
        "name": file_name,
        "size": humanbytes(getattr(media, "file_size", 0)),
        "duration": time_formatter(getattr(media, "duration", 0)),
        "type": "🎬 Video" if hasattr(media, "video") else "🎵 Audio" if hasattr(media, "audio") else "📁 Document",
        "upload_time": datetime.now().strftime("%d %b %Y %H:%M"),
        "is_nsfw": await detect_nsfw_content(file_name),
        "is_premium": "premium" in file_name.lower(),
        "quality": detect_media_quality(file_name),
        "hash": await generate_file_signature(media.file_id)
    }

# ===== Memory-Efficient Thumbnail Processing ===== #
async def process_thumbnail(thumb_file: str) -> Optional[str]:
    """Process thumbnail with memory limits"""
    try:
        with Image.open(thumb_file) as img:
            # Downscale if too large
            if max(img.size) > 1024:
                img.thumbnail((1024, 1024))
            
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            text = WATERMARK
            text_width = draw.textlength(text, font=font)
            position = (img.width - text_width - 10, img.height - 30)
            
            draw.text(
                position,
                text,
                fill="white",
                font=font,
                stroke_width=2,
                stroke_fill="black"
            )
            
            output_path = f"thumb_{os.path.basename(thumb_file)}"
            img.save(output_path, format='JPEG', quality=85, optimize=True)
            return output_path
    except Exception as e:
        print(f"Thumbnail processing error: {e}")
        return None
    finally:
        if 'img' in locals():
            del img  # Explicit cleanup

# ===== Optimized Main Handler ===== #
@Client.on_message(filters.chat(CHANNELS) & (filters.document | filters.video | filters.audio))
async def media_handler(client: Client, message: Message):
    try:
        start_time = time.time()
        media = getattr(message, message.media.value)
        
        # Memory check
        check_memory_usage()
        
        # Duplicate check
        file_hash = await generate_file_signature(media.file_id)
        if file_hash in processed_files:
            return
        
        # Process media
        media_info = await analyze_media(media)
        processed_files.add(file_hash)
        
        # Prepare content
        file_id, _ = unpack_new_file_id(media.file_id)
        buttons = [[InlineKeyboardButton("📥 Download", url=f"https://t.me/{temp.U_NAME}?start={file_id}")]]
        
        # Thumbnail handling
        thumb_path = None
        if hasattr(media, "thumbs") and media.thumbs:
            try:
                thumb_path = await client.download_media(
                    media.thumbs[0].file_id,
                    file_name=f"temp_{file_hash[:8]}.jpg"
                )
                thumb_path = await process_thumbnail(thumb_path)
            except Exception as e:
                print(f"Thumbnail error: {e}")
        
        # Send content
        try:
            if thumb_path:
                await client.send_photo(
                    chat_id=UPDATE_CHANNEL,
                    photo=thumb_path,
                    caption=script.MEDIA_CAPTION.format(**media_info),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            else:
                await client.copy_message(
                    chat_id=UPDATE_CHANNEL,
                    from_chat_id=message.chat.id,
                    message_id=message.id,
                    caption=script.MEDIA_CAPTION.format(**media_info),
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
        finally:
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)
                
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        error_msg = f"Error processing {getattr(media, 'file_name', 'unknown')}: {str(e)}"
        await client.send_message(LOG_CHANNEL, error_msg[:4000])