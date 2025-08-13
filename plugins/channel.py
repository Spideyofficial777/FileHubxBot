import os
import re
import time
import asyncio
import hashlib
import traceback
from datetime import datetime
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import FloodWait

from info import CHANNELS, MOVIE_UPDATE_CHANNEL, ADMINS, LOG_CHANNEL
from database.ia_filterdb import save_file, unpack_new_file_id
from utils import get_poster, temp
from database.users_chats_db import db
from Script import script

# ===== Configuration ===== #
MEDIA_TYPES = {
    "video": "🎬 Video",
    "audio": "🎵 Audio",
    "document": "📄 Document"
}

NSFW_KEYWORDS = {"xxx", "porn", "adult", "18+", "nsfw"}
PREMIUM_TAG = "⭐ PREMIUM CONTENT"
WATERMARK_TEXT = "© YourBrand"

processed_files = set()
media_filter = filters.document | filters.video | filters.audio


# ===== Utility Functions ===== #
def humanbytes(size: int) -> str:
    """Convert bytes to human-readable format"""
    if not size:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def time_formatter(seconds: int) -> str:
    """Convert seconds to H:M:S format"""
    if not seconds:
        return "Unknown"
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes:02d}:{seconds:02d}"


async def generate_file_hash(file_id: str) -> str:
    """Generate SHA256 hash for duplicate detection"""
    return hashlib.sha256(file_id.encode()).hexdigest()


async def clean_filename(filename: str) -> str:
    """Sanitize filenames for display"""
    if not filename:
        return "Unknown"
    return re.sub(r'[^\w\s\-\.\(\)]', '', filename).strip()


async def add_watermark(image_path: str) -> str:
    """Add text watermark to images"""
    try:
        with Image.open(image_path).convert("RGBA") as img:
            draw = ImageDraw.Draw(img)
            font_size = max(14, img.width // 30)
            font = ImageFont.load_default()

            # Adjust font if PIL supports truetype
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                pass

            text_width = draw.textlength(WATERMARK_TEXT, font=font)
            x = img.width - text_width - 10
            y = img.height - font_size - 10
            draw.text((x, y), WATERMARK_TEXT, fill=(255, 255, 255, 200), font=font)

            watermarked_path = f"watermarked_{os.path.basename(image_path)}"
            img.save(watermarked_path)
            return watermarked_path
    except Exception:
        return image_path


async def get_media_info(message: Message) -> Tuple[str, str, str, str, str]:
    """Extract metadata from message's media"""
    media = message.document or message.video or message.audio
    file_name = await clean_filename(getattr(media, "file_name", ""))
    file_size = humanbytes(getattr(media, "file_size", 0))
    duration = time_formatter(getattr(media, "duration", 0))
    media_type = MEDIA_TYPES.get(message.media.value, f"📁 {message.media.value.capitalize()}")
    upload_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
    return file_name, file_size, duration, media_type, upload_time


async def generate_caption(file_name, file_size, duration, media_type, upload_time, is_nsfw=False, is_premium=False) -> str:
    """Generate beautiful formatted caption"""
    base_caption = script.MEDIA_UPDATE_TXT.format(
        type=media_type,
        name=file_name,
        size=file_size,
        duration=duration,
        upload_time=upload_time
    )
    tags = []
    if is_nsfw:
        tags.append("🔞 NSFW CONTENT")
    if is_premium:
        tags.append(PREMIUM_TAG)
    if tags:
        base_caption += "\n\n" + " | ".join(tags)
    return base_caption


async def create_download_button(file_id: str) -> InlineKeyboardMarkup:
    """Generate download button with deep link"""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬇️ Download Now", url=f"https://telegram.me/{temp.U_NAME}?start={file_id}")],
        [InlineKeyboardButton("❓ How to Download", url="https://t.me/spideyofficial_777/12")]
    ])


# ===== Core Handler ===== #
@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def handle_new_media(client: Client, message: Message):
    try:
        media = message.document or message.video or message.audio
        if not media:
            return

        file_hash = await generate_file_hash(media.file_id)
        if file_hash in processed_files:
            return
        processed_files.add(file_hash)

        await save_file(media)

        if not await db.get_send_movie_update_status(client.me.id):
            return

        file_id, _ = unpack_new_file_id(media.file_id)
        await forward_to_update_channel(client, message, file_id)

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        await client.send_message(LOG_CHANNEL, f"❌ Media Handling Error:\n{traceback.format_exc()}")


async def forward_to_update_channel(client: Client, message: Message, file_id: str):
    try:
        file_name, file_size, duration, media_type, upload_time = await get_media_info(message)
        lower_name_caption = (file_name + " " + (message.caption or "")).lower()

        is_nsfw = any(kw in lower_name_caption for kw in NSFW_KEYWORDS)
        is_premium = "premium" in lower_name_caption

        caption = await generate_caption(file_name, file_size, duration, media_type, upload_time, is_nsfw, is_premium)
        reply_markup = await create_download_button(file_id)
        target_channel = await db.movies_update_channel_id() or MOVIE_UPDATE_CHANNEL

        # Try sending thumbnail
        thumb_sent = False
        try:
            media_obj = message.document or message.video or message.audio
            if hasattr(media_obj, "thumbs") and media_obj.thumbs:
                thumb = media_obj.thumbs[0]
                thumb_file = await client.download_media(thumb.file_id)
                watermarked_thumb = await add_watermark(thumb_file)

                await client.send_photo(
                    chat_id=target_channel,
                    photo=watermarked_thumb,
                    caption=caption,
                    reply_markup=reply_markup
                )
                os.remove(thumb_file)
                if watermarked_thumb != thumb_file:
                    os.remove(watermarked_thumb)
                thumb_sent = True
        except Exception:
            pass

        # Fallback to copy original media
        if not thumb_sent:
            try:
                await client.copy_message(
                    chat_id=target_channel,
                    from_chat_id=message.chat.id,
                    message_id=message.id,
                    caption=caption,
                    reply_markup=reply_markup
                )
            except Exception:
                await client.send_message(
                    chat_id=target_channel,
                    text=caption,
                    reply_markup=reply_markup
                )

        await db.log_media_forward(file_id, datetime.now())

    except Exception:
        await client.send_message(LOG_CHANNEL, f"❌ Forward Error:\n{traceback.format_exc()}")


# ===== Album Handler ===== #
@Client.on_message(filters.chat(CHANNELS) & filters.media_group)
async def handle_media_group(client: Client, message: Message):
    try:
        await asyncio.sleep(1.5)  # Ensure all group messages arrive
        album_messages = await client.get_media_group(message.chat.id, message.id)
        for msg in album_messages:
            if media_filter.check(msg):
                await handle_new_media(client, msg)
    except Exception:
        await client.send_message(LOG_CHANNEL, f"❌ Album Error:\n{traceback.format_exc()}")
