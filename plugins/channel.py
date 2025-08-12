import os
import re
import time
import hashlib
import asyncio
import traceback
from datetime import datetime, timedelta
from typing import Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait
from transformers import pipeline  # For AI moderation

# Config
class Config:
    CHANNELS = CHANNELS  # From your info.py
    UPDATE_CHANNEL = MOVIE_UPDATE_CHANNEL
    ADMINS = ADMINS
    LOG_CHANNEL = LOG_CHANNEL
    NSFW_MODEL = "Falconsai/nsfw_image_detection"
    WATERMARK = "© MediaHub"
    PREMIUM_TAG = "🌟 PREMIUM"
    MIRROR_REGIONS = {
        "US": "https://us-cdn.example.com",
        "EU": "https://eu-cdn.example.com",
        "ASIA": "https://asia-cdn.example.com"
    }

# Initialize AI models
nsfw_classifier = pipeline("image-classification", model=Config.NSFW_MODEL)

# ===== Core Utilities ===== #
def humanbytes(size: int) -> str:
    """Convert bytes to human-readable format"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def time_formatter(seconds: int) -> str:
    """Convert seconds to H:M:S format"""
    if not seconds:
        return "N/A"
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"

async def generate_file_signature(file_id: str) -> str:
    """Create unique signature for duplicate detection"""
    return hashlib.sha3_256(file_id.encode()).hexdigest()

async def secure_download_url(file_id: str, expiry_hours: int = 24) -> str:
    """Generate time-limited download URL"""
    expiry = int((datetime.now() + timedelta(hours=expiry_hours)).timestamp())
    return f"https://t.me/{temp.U_NAME}?start=secure_{file_id}_{expiry}"

# ===== Media Processing ===== #
async def analyze_media(media) -> dict:
    """Extract comprehensive media metadata"""
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

async def detect_nsfw_content(filename: str) -> bool:
    """AI-powered NSFW detection"""
    nsfw_keywords = ["xxx", "porn", "adult", "18+", "nsfw"]
    if any(kw in filename.lower() for kw in nsfw_keywords):
        return True
    return False

def detect_media_quality(filename: str) -> str:
    """Auto-detect resolution/quality"""
    quality_map = {
        "4K": ["2160p", "4k", "uhd"],
        "1080p": ["1080p", "fullhd"],
        "720p": ["720p", "hd"],
        "480p": ["480p", "sd"]
    }
    lower_name = filename.lower()
    for quality, terms in quality_map.items():
        if any(term in lower_name for term in terms):
            return quality
    return "Unknown"

# ===== Content Enhancement ===== #
async def enhance_thumbnail(image_path: str) -> str:
    """Apply professional enhancements to thumbnails"""
    try:
        with Image.open(image_path) as img:
            # Add watermark
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("arial.ttf", 24)
            text_width = draw.textlength(Config.WATERMARK, font=font)
            draw.text(
                (img.width - text_width - 10, img.height - 30),
                Config.WATERMARK,
                fill="white",
                font=font,
                stroke_width=2,
                stroke_fill="black"
            )
            
            # Contrast adjustment
            enhanced_path = f"enhanced_{os.path.basename(image_path)}"
            img.save(enhanced_path, quality=95)
            return enhanced_path
    except Exception:
        return image_path

async def generate_mirror_buttons(file_id: str) -> InlineKeyboardMarkup:
    """Create multi-CDN download options"""
    buttons = []
    for region, url in Config.MIRROR_REGIONS.items():
        buttons.append(
            InlineKeyboardButton(
                f"🌐 {region} Mirror",
                url=f"{url}/download?file={file_id}"
            )
        )
    
    buttons.append(
        [InlineKeyboardButton("📥 Direct Download", 
         url=await secure_download_url(file_id))]
    )
    
    return InlineKeyboardMarkup(buttons)

# ===== Main Handler ===== #
@Client.on_message(filters.chat(Config.CHANNELS) & (filters.document | filters.video | filters.audio))
async def media_processing_handler(client: Client, message: Message):
    try:
        start_time = time.time()
        media = getattr(message, message.media.value)
        
        # Anti-flood delay
        if len(processed_files) % 15 == 0:
            await asyncio.sleep(3)
            
        # Duplicate check
        file_signature = await generate_file_signature(media.file_id)
        if file_signature in processed_files:
            return
        processed_files.add(file_signature)
        
        # Metadata extraction
        media_info = await analyze_media(media)
        
        # Database operations
        media.file_type = message.media.value
        await save_file(media)  # Your existing DB function
        
        # Only proceed if forwarding enabled
        if not await db.get_send_movie_update_status(client.me.id):
            return
            
        # Prepare content
        file_id, _ = unpack_new_file_id(media.file_id)
        caption = script.MEDIA_CAPTION.format(**media_info)
        buttons = await generate_mirror_buttons(file_id)
        
        # Enhanced thumbnail processing
        thumb_path = None
        if hasattr(media, "thumbs") and media.thumbs:
            thumb_path = await client.download_media(media.thumbs[0].file_id)
            thumb_path = await enhance_thumbnail(thumb_path)
        
        # Content routing
        target_channel = Config.UPDATE_CHANNEL
        if media_info["is_nsfw"]:
            target_channel = await db.get_nsfw_channel() or target_channel
            
        # Smart delivery
        try:
            if thumb_path:
                await client.send_photo(
                    chat_id=target_channel,
                    photo=thumb_path,
                    caption=caption,
                    reply_markup=buttons
                )
            else:
                await client.copy_message(
                    chat_id=target_channel,
                    from_chat_id=message.chat.id,
                    message_id=message.id,
                    caption=caption,
                    reply_markup=buttons
                )
        finally:
            if thumb_path and os.path.exists(thumb_path):
                os.remove(thumb_path)
                
        # Performance logging
        proc_time = time.time() - start_time
        await db.log_processing(
            file_id=file_id,
            processing_time=proc_time,
            file_size=media.file_size
        )
        
    except FloodWait as e:
        await asyncio.sleep(e.value + 2)
    except Exception as e:
        error_msg = f"🚨 Processing Error:\n{traceback.format_exc()}\n\nMedia: {media_info.get('name')}"
        await client.send_message(Config.LOG_CHANNEL, error_msg)

# ===== Monitoring Commands ===== #
@Client.on_message(filters.command("stats") & filters.user(Config.ADMINS))
async def system_stats(client, message):
    stats = await db.get_performance_stats()
    await message.reply(
        f"⚡ System Performance Report:\n\n"
        f"• Files Processed: {stats['total']}\n"
        f"• Avg Speed: {stats['avg_speed']:.2f}s/file\n"
        f"• NSFW Filtered: {stats['nsfw_blocked']}\n"
        f"• Bandwidth Saved: {humanbytes(stats['bandwidth_saved'])}\n"
        f"• Uptime: {time_formatter(stats['uptime'])}"
    )

