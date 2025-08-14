import os
import re
import time
import asyncio
import hashlib
import traceback
from datetime import datetime
from typing import Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, Document, Video, Audio
from pyrogram.errors import FloodWait, FileIdInvalid, FileReferenceEmpty
from pyrogram.file_id import FileId

from config import CHANNELS, UPDATE_CHANNEL, OWNER_ID, LOG_CHANNEL, temp
from database.database import save_file, Media, db
from Script import script
from umongo.exceptions import ValidationError

# ===== Configuration ===== #
MEDIA_TYPES = {
    "video": "🎬 Video",
    "audio": "🎵 Audio",
    "document": "📄 Document"
}

NSFW_KEYWORDS = {"xxx", "porn", "adult", "18+", "nsfw"}
PREMIUM_TAG = "⭐ PREMIUM CONTENT"
WATERMARK_TEXT = "©filehubxbot"

processed_files = set()
media_filter = filters.document | filters.video | filters.audio

# ===== Utility Functions ===== #
def humanbytes(size: Union[int, float], precision: int = 2) -> str:
    """Convert bytes to human-readable format"""
    if not isinstance(size, (int, float)) or size < 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{precision}f} {unit}"

def time_formatter(seconds: int) -> str:
    """Convert seconds to H:M:S format"""
    if not isinstance(seconds, (int, float)) or seconds <= 0:
        return "00:00"
    
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
    return re.sub(r'[^\w\s\-\.\(\)]', '', str(filename)).strip()

async def add_watermark(image_path: str) -> str:
    """Add text watermark to images"""
    try:
        with Image.open(image_path).convert("RGBA") as img:
            draw = ImageDraw.Draw(img)
            font_size = max(14, img.width // 30)
            
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            text = WATERMARK_TEXT
            text_width = draw.textlength(text, font=font)
            x = img.width - text_width - 10
            y = img.height - font_size - 10
            
            draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)
            watermarked_path = f"watermarked_{os.path.basename(image_path)}"
            img.save(watermarked_path)
            return watermarked_path
    except Exception as e:
        print(f"Watermark error: {e}")
        return image_path

async def get_media_info(media: Union[Document, Video, Audio]) -> Tuple[str, str, str, str, str]:
    """Extract metadata from media object"""
    try:
        file_name = await clean_filename(getattr(media, "file_name", ""))
        file_size = humanbytes(getattr(media, "file_size", 0))
        
        duration = time_formatter(getattr(media, "duration", 0))
        media_type = MEDIA_TYPES.get(media.__class__.__name__.lower(), "📁 File")
        upload_time = datetime.now().strftime("%d %b %Y, %I:%M %p")
        
        return file_name, file_size, duration, media_type, upload_time
    except Exception as e:
        print(f"Media info error: {e}")
        return "Unknown", "0 B", "00:00", "📁 File", datetime.now().strftime("%d %b %Y, %I:%M %p")

async def generate_caption(file_name, file_size, duration, media_type, upload_time, 
                          is_nsfw=False, is_premium=False) -> str:
    """Generate formatted caption"""
    try:
        base_caption = script.MEDIA_CAPTION.format(
            type=media_type,
            name=file_name,
            size=file_size,
            duration=duration,
            upload_time=upload_time,
            premium_tag=PREMIUM_TAG if is_premium else "",
            nsfw_warning=script.NSFW_WARNING if is_nsfw else ""
        )
        return base_caption
    except Exception as e:
        print(f"Caption generation error: {e}")
        return f"📌 Name: {file_name}\n📊 Size: {file_size}\n🕒 Duration: {duration}"

async def create_download_button(file_id: str) -> InlineKeyboardMarkup:
    """Generate download button"""
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

        # Save to database
        result = await save_file(media)
        if result in ["err", "dup"]:
            return

        if not await db.get_send_movie_update_status(client.me.id):
            return

        # Forward to update channel
        try:
            decoded = FileId.decode(media.file_id)
            file_id = encode_file_id(
                pack(
                    "<iiqq",
                    int(decoded.file_type),
                    decoded.dc_id,
                    decoded.media_id,
                    decoded.access_hash
                )
            )
            await forward_to_update_channel(client, message, file_id)
        except Exception as e:
            await client.send_message(
                LOG_CHANNEL, 
                f"❌ File ID Error in {getattr(media, 'file_name', 'Unknown')}:\n{str(e)}"
            )

    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception as e:
        error_msg = f"❌ Media Handling Error:\n{traceback.format_exc()}"
        await client.send_message(LOG_CHANNEL, error_msg[:4000])

async def forward_to_update_channel(client: Client, message: Message, file_id: str):
    try:
        media = message.document or message.video or message.audio
        file_name, file_size, duration, media_type, upload_time = await get_media_info(media)
        
        caption_text = message.caption or ""
        lower_name_caption = (file_name + " " + caption_text).lower()
        is_nsfw = any(kw in lower_name_caption for kw in NSFW_KEYWORDS)
        is_premium = "premium" in lower_name_caption

        caption = await generate_caption(
            file_name, file_size, duration, media_type, upload_time, 
            is_nsfw, is_premium
        )
        reply_markup = await create_download_button(file_id)
        target_channel = await db.movies_update_channel_id() or MOVIE_UPDATE_CHANNEL

        # Try sending thumbnail if available
        thumb_sent = False
        if hasattr(media, "thumbs") and media.thumbs:
            try:
                thumb = media.thumbs[-1]  # Get highest quality thumb
                thumb_file = await client.download_media(thumb.file_id)
                if thumb_file and os.path.exists(thumb_file):
                    watermarked_thumb = await add_watermark(thumb_file)
                    
                    await client.send_photo(
                        chat_id=target_channel,
                        photo=watermarked_thumb,
                        caption=caption,
                        reply_markup=reply_markup
                    )
                    thumb_sent = True
                    
                    # Cleanup
                    for f in [thumb_file, watermarked_thumb]:
                        if f != thumb_file and os.path.exists(f):
                            os.remove(f)
            except Exception as e:
                print(f"Thumbnail error: {e}")

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
            except Exception as e:
                print(f"Copy error: {e}")
                await client.send_message(
                    chat_id=target_channel,
                    text=caption,
                    reply_markup=reply_markup
                )

        await db.log_media_forward(file_id, datetime.now())

    except Exception as e:
        error_msg = f"❌ Forward Error:\n{traceback.format_exc()}"
        await client.send_message(LOG_CHANNEL, error_msg[:4000])

# ===== Album Handler ===== #
@Client.on_message(filters.chat(CHANNELS) & filters.media_group)
async def handle_media_group(client: Client, message: Message):
    try:
        await asyncio.sleep(2)  # Wait for all group messages
        album_messages = await client.get_media_group(message.chat.id, message.id)
        for msg in album_messages:
            if media_filter.check(msg):
                await handle_new_media(client, msg)
    except Exception as e:
        error_msg = f"❌ Album Error:\n{traceback.format_exc()}"
        await client.send_message(LOG_CHANNEL, error_msg[:4000])

# File ID encoding functions
def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def pack(*args):
    """Wrapper for struct.pack"""
    from struct import pack as _pack
    return _pack(*args)
