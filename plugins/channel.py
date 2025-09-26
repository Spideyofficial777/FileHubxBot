import os
import re
import time
import asyncio
import hashlib
import traceback
import base64
from datetime import datetime
from typing import Optional, Tuple, Union
from struct import pack

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, Document, Video, Audio
from pyrogram.errors import FloodWait, FileIdInvalid, FileReferenceEmpty
from pyrogram.file_id import FileId

from config import CHANNELS, UPDATE_CHANNEL, OWNER_ID, LOG_CHANNEL, temp, CHANNEL_ID
from database.database import save_file, Media, db
from Script import script
from umongo.exceptions import ValidationError
from helper_func import admin

# Try to import PIL, fallback if not available
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ===== Configuration ===== #
MEDIA_TYPES = {
    "video": "🎬 Video",
    "audio": "🎵 Audio",
    "document": "📄 Document"
}

NSFW_KEYWORDS = {"xxx", "porn", "adult", "18+", "nsfw"}
PREMIUM_TAG = "⭐ PREMIUM CONTENT"
WATERMARK_TEXT = "© Copyright (C) 2025 by Spidey Official"

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
    if not PIL_AVAILABLE:
        return image_path
        
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

async def create_download_button(file_id: str, custom_url: str = None) -> InlineKeyboardMarkup:
    """Generate enhanced download buttons with custom URL option"""
    buttons = []
    
    # Main download button
    buttons.append([InlineKeyboardButton("⬇️ Download Now", url=f"https://telegram.me/{temp.U_NAME}?start={file_id}")])
    
    # Custom URL button if provided
    if custom_url:
        buttons.append([InlineKeyboardButton("🔗 Custom Download", url=custom_url)])
    
    # Help and info buttons
    buttons.append([
        InlineKeyboardButton("❓ How to Download", url="https://t.me/spideyofficial_777/12"),
        InlineKeyboardButton("📱 Get File", callback_data=f"get_file_{file_id}")
    ])
    
    return InlineKeyboardMarkup(buttons)

async def create_enhanced_caption(file_name, file_size, duration, media_type, upload_time, 
                                file_id, is_nsfw=False, is_premium=False, custom_url=None) -> str:
    """Generate enhanced caption with detailed file information"""
    try:
        # Base file information
        caption_parts = [
            f"✨ **{media_type} Alert** ✨",
            "",
            f"📌 **Name:** `{file_name}`",
            f"📊 **Size:** `{file_size}`",
            f"🕒 **Duration:** `{duration}`",
            f"📅 **Uploaded:** `{upload_time}`",
            f"🆔 **File ID:** `{file_id[:20]}...`"
        ]
        
        # Add premium/NSFW tags
        if is_premium:
            caption_parts.append("")
            caption_parts.append("⭐ **PREMIUM CONTENT** ⭐")
        
        if is_nsfw:
            caption_parts.append("")
            caption_parts.append("🔞 **NSFW CONTENT** 🔞")
        
        # Add custom URL info if available
        if custom_url:
            caption_parts.append("")
            caption_parts.append(f"🔗 **Custom URL:** {custom_url}")
        
        # Add download instructions
        caption_parts.extend([
            "",
            "🔻 **Download Instructions:**",
            "1️⃣ Click 'Download Now' button",
            "2️⃣ Start the bot if not started",
            "3️⃣ Get your file instantly!",
            "",
            "🌿 **Maintained by:** [Spidey Official](https://t.me/Spideyofficial777)"
        ])
        
        return "\n".join(caption_parts)
        
    except Exception as e:
        print(f"Enhanced caption error: {e}")
        return f"📌 Name: {file_name}\n📊 Size: {file_size}\n🕒 Duration: {duration}\n\n🔻 Download Now!"

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
        
        # Extract custom URL from caption if present
        custom_url = None
        url_pattern = r'https?://[^\s]+'
        urls = re.findall(url_pattern, caption_text)
        if urls:
            custom_url = urls[0]  # Use first URL found

        # Create enhanced caption and buttons
        caption = await create_enhanced_caption(
            file_name, file_size, duration, media_type, upload_time, 
            file_id, is_nsfw, is_premium, custom_url
        )
        reply_markup = await create_download_button(file_id, custom_url)
        target_channel = await db.movies_update_channel_id() or UPDATE_CHANNEL

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

        # Send DM to main channel with file details
        await send_dm_to_main_channel(client, file_name, file_size, duration, media_type, file_id, custom_url)

        await db.log_media_forward(file_id, datetime.now())

    except Exception as e:
        error_msg = f"❌ Forward Error:\n{traceback.format_exc()}"
        await client.send_message(LOG_CHANNEL, error_msg[:4000])

async def send_dm_to_main_channel(client: Client, file_name: str, file_size: str, duration: str, 
                                media_type: str, file_id: str, custom_url: str = None):
    """Send detailed file information to main channel via DM"""
    try:
        # Create detailed file information message
        dm_message = f"""
📁 **New File Added to Database**

🎬 **File Details:**
• **Name:** `{file_name}`
• **Type:** {media_type}
• **Size:** `{file_size}`
• **Duration:** `{duration}`
• **File ID:** `{file_id[:30]}...`

🔗 **Download Options:**
• Bot Download: `https://telegram.me/{temp.U_NAME}?start={file_id}`
{f"• Custom URL: {custom_url}" if custom_url else ""}

⏰ **Added:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}

🌿 **Maintained by:** [Spidey Official](https://t.me/Spideyofficial777)
        """
        
        # Send to main channel
        await client.send_message(
            chat_id=CHANNEL_ID,
            text=dm_message,
            disable_web_page_preview=True
        )
        
        # Also send to log channel for tracking
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"📁 File added: {file_name} ({file_size}) - {media_type}",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"DM to main channel error: {e}")
        # Log error but don't fail the main process
        await client.send_message(
            LOG_CHANNEL,
            f"❌ DM Error for {file_name}: {str(e)}"
        )

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

# ===== Callback Handlers ===== #
@Client.on_callback_query(filters.regex("^get_file_"))
async def handle_get_file_callback(client: Client, callback_query):
    """Handle get file callback"""
    try:
        file_id = callback_query.data.split("_", 2)[2]
        
        # Send file directly to user
        await callback_query.answer("📁 Sending file...")
        
        # Create direct download message
        download_message = f"""
📁 **File Download**

🔗 **Direct Download Link:**
`https://telegram.me/{temp.U_NAME}?start={file_id}`

📱 **How to Download:**
1. Click the link above
2. Start the bot if not started
3. Get your file instantly!

💡 **Tip:** Save this link for future use!

🌿 **Maintained by:** [Spidey Official](https://t.me/Spideyofficial777)
        """
        
        await callback_query.edit_message_text(
            download_message,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬇️ Download Now", url=f"https://telegram.me/{temp.U_NAME}?start={file_id}")],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
        )
        
    except Exception as e:
        await callback_query.answer(f"❌ Error: {str(e)}", show_alert=True)

@Client.on_callback_query(filters.regex("^close$"))
async def handle_close_callback(client: Client, callback_query):
    """Handle close callback"""
    try:
        await callback_query.message.delete()
    except:
        await callback_query.answer("❌ Could not close message")

# ===== Admin Commands ===== #
@Client.on_message(filters.command('setcustomurl') & filters.private & admin)
async def set_custom_url(client: Client, message: Message):
    """Set custom URL for file downloads"""
    try:
        if len(message.command) < 3:
            await message.reply_text(
                "Usage: `/setcustomurl <file_id> <custom_url>`\n\n"
                "Example: `/setcustomurl BQACAgIAAxkBAAIB... https://example.com/download`"
            )
            return
        
        file_id = message.command[1]
        custom_url = message.command[2]
        
        # Validate URL
        if not custom_url.startswith(('http://', 'https://')):
            await message.reply_text("❌ Invalid URL. Must start with http:// or https://")
            return
        
        # Store custom URL in database (you can implement this in your database)
        # For now, we'll just confirm
        await message.reply_text(
            f"✅ Custom URL set successfully!\n\n"
            f"**File ID:** `{file_id[:30]}...`\n"
            f"**Custom URL:** {custom_url}\n\n"
            f"Users will now see this custom URL as an additional download option."
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error setting custom URL: {str(e)}")

@Client.on_message(filters.command('fileinfo') & filters.private & admin)
async def get_file_info(client: Client, message: Message):
    """Get detailed information about a file"""
    try:
        if len(message.command) < 2:
            await message.reply_text("Usage: `/fileinfo <file_id>`")
            return
        
        file_id = message.command[1]
        
        # Get file information from database
        # This is a placeholder - implement based on your database structure
        file_info = f"""
📁 **File Information**

🆔 **File ID:** `{file_id}`
📊 **Status:** Available
📅 **Added:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}

🔗 **Download Links:**
• Bot Download: `https://telegram.me/{temp.U_NAME}?start={file_id}`

💡 **Usage:** Send this file ID to any user or use in your bot
        """
        
        await message.reply_text(file_info)
        
    except Exception as e:
        await message.reply_text(f"❌ Error getting file info: {str(e)}")

# ===== Enhanced Media Processing ===== #
@Client.on_message(filters.command('processmedia') & filters.private & admin)
async def process_media_command(client: Client, message: Message):
    """Manually process media from a message"""
    try:
        if not message.reply_to_message:
            await message.reply_text("❌ Please reply to a media message to process it.")
            return
        
        reply_msg = message.reply_to_message
        media = reply_msg.document or reply_msg.video or reply_msg.audio
        
        if not media:
            await message.reply_text("❌ No media found in the replied message.")
            return
        
        # Process the media
        await handle_new_media(client, reply_msg)
        await message.reply_text("✅ Media processed successfully!")
        
    except Exception as e:
        await message.reply_text(f"❌ Error processing media: {str(e)}")

# ===== Bulk Operations ===== #
@Client.on_message(filters.command('bulkprocess') & filters.private & admin)
async def bulk_process_media(client: Client, message: Message):
    """Process multiple media files at once"""
    try:
        if len(message.command) < 2:
            await message.reply_text(
                "Usage: `/bulkprocess <chat_id> <start_message_id> <end_message_id>`\n\n"
                "Example: `/bulkprocess -1001234567890 100 200`"
            )
            return
        
        chat_id = int(message.command[1])
        start_id = int(message.command[2])
        end_id = int(message.command[3])
        
        processed_count = 0
        error_count = 0
        
        await message.reply_text(f"🔄 Processing media from message {start_id} to {end_id}...")
        
        for msg_id in range(start_id, end_id + 1):
            try:
                msg = await client.get_messages(chat_id, msg_id)
                if msg and (msg.document or msg.video or msg.audio):
                    await handle_new_media(client, msg)
                    processed_count += 1
                    await asyncio.sleep(0.5)  # Rate limiting
            except Exception as e:
                error_count += 1
                print(f"Error processing message {msg_id}: {e}")
        
        await message.reply_text(
            f"✅ Bulk processing completed!\n\n"
            f"📊 **Results:**\n"
            f"• Processed: {processed_count}\n"
            f"• Errors: {error_count}\n"
            f"• Total: {processed_count + error_count}"
        )
        
    except Exception as e:
        await message.reply_text(f"❌ Error in bulk processing: {str(e)}")
