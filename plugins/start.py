# Don't Remove Credit @Spideyofficial777
# Ask Doubt on telegram @Spideyofficial777
#
# Copyright (C) 2025 by Spidey Official, < https://t.me/Spideyofficial777 >.
#
# released under the MIT License.
#
#
# All rights reserved.
#

import asyncio
import os
import random
import sys
import re
import string
import string as spidey
import time
from datetime import datetime, timedelta
import pytz
from pyrogram import Client, filters, __version__
from pyrogram.enums import ParseMode, ChatAction
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ReplyKeyboardMarkup,
    ChatInviteLink,
    ChatPrivileges,
)
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserNotParticipant
from bot import Bot
from config import *
from helper_func import *
from database.database import *
from database.db_premium import *
from Script import script
from plugins.email import email_system, initialize_email_system, shutdown_email_system

BAN_SUPPORT = f"{BAN_SUPPORT}"
TUT_VID = f"{TUT_VID}"

# Enhanced verification tracking
verification_cache = {}

# Beautiful progress messages
progress_messages = [
    "🔄 <b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇꜱᴛ...</b>",
    "📡 <b>ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ꜱᴇʀᴠᴇʀ...</b>",
    "🔍 <b>ꜱᴇᴀʀᴄʜɪɴɢ ꜰᴏʀ ʏᴏᴜʀ ꜰɪʟᴇꜱ...</b>",
    "📂 <b>ʟᴏᴀᴅɪɴɢ ꜰɪʟᴇ ᴅᴀᴛᴀ...</b>",
    "⚡ <b>ᴘʀᴇᴘᴀʀɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ...</b>",
    "🎯 <b>ᴀʟᴍᴏꜱᴛ ᴛʜᴇʀᴇ...</b>",
    "✨ <b>ꜰɪɴᴀʟɪᴢɪɴɢ...</b>",
    "!!!!!!!!!",
    "!!!!!!!!!",
]

success_messages = [
    "🎉 <b>ᴡᴏᴡ! ʏᴏᴜʀ ꜰɪʟᴇꜱ ᴀʀᴇ ʀᴇᴀᴅʏ!</b> 🌟",
    "✅ <b>ꜱᴜᴄᴄᴇꜱꜱ! ᴀʟʟ ꜰɪʟᴇꜱ ᴅᴇʟɪᴠᴇʀᴇᴅ!</b> 🚀",
    "🔥 <b>ʙᴏᴏᴍ! ʏᴏᴜʀ ꜰɪʟᴇꜱ ᴀʀᴇ ʜᴇʀᴇ!</b> 💫",
    "📦 <b>ᴘᴀᴄᴋᴀɢᴇ ᴅᴇʟɪᴠᴇʀᴇᴅ ꜱᴜᴄᴄᴇꜱꜱ꜠ᴜʟʟʏ!</b> 🎁",
    "⚡ <b>ʟɪɢʜᴛɴɪɴɢ ꜰᴀꜱᴛ! ꜰɪʟᴇꜱ ᴀʀᴇ ʀᴇᴀᴅʏ!</b> ⚡",
    "!!!!!!!!!",
    "!!!!!!!!!",
]


# Enhanced progress animation function
async def show_progress_animation(client, message, total_steps=7):
    temp_msg = await message.reply(progress_messages[0])

    for i in range(1, total_steps):
        await asyncio.sleep(0.8)
        try:
            animated_text = f"{progress_messages[i]}\n\n"
            await temp_msg.edit(animated_text)
        except Exception:
            continue

    return temp_msg


def get_loading_emoji(step):
    emojis = ["🔄", "📡", "🔍", "📂", "⚡", "🎯", "✨"]
    return emojis[step % len(emojis)]


def get_status_text(step):
    statuses = [
        "ɪɴɪᴛɪᴀʟɪᴢɪɴɢ ꜱʏꜱᴛᴇᴍ",
        "ᴇꜱᴛᴀʙʟɪꜱʜɪɴɢ ꜱᴇᴄᴜʀᴇ ᴄᴏɴɴᴇᴄᴛɪᴏɴ",
        "ʟᴏᴄᴀᴛɪɴɢ ʏᴏᴜʀ ꜰɪʟᴇꜱ",
        "ᴘʀᴏᴄᴇꜱꜱɪɴɢ ꜰɪʟᴇ ᴅᴀᴛᴀ",
        "ᴏᴘᴛɪᴍɪᴢɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ꜱᴘᴇᴇᴅ",
        "ꜰɪɴᴀʟ ᴘʀᴇᴘᴀʀᴀᴛɪᴏɴꜱ",
        "ᴀʟᴍᴏꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇ",
        "!!!!!!!!!",
        "!!!!!!!!!",
    ]
    return statuses[step % len(statuses)]


async def enhanced_file_processing(client, message, ids):
    temp_msg = await show_progress_animation(client, message)

    try:
        messages = await get_messages(client, ids)

        success_msg = random.choice(success_messages)
        file_count = len(messages)

        final_success_msg = (
            f"{success_msg}\n\n"
            f"📊 <b>ꜰɪʟᴇ ꜱᴜᴍᴍᴀʀʏ:</b>\n"
            f"• 📁 ᴛᴏᴛᴀʟ ꜰɪʟᴇꜱ: {file_count}\n"
            f"• ✅ ꜱᴛᴀᴛᴜꜱ: ʀᴇᴀᴅʏ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ\n"
            f"• 🚀 ꜱᴘᴇᴇᴅ: ᴏᴘᴛɪᴍɪᴢᴇᴅ\n\n"
            f"💡 <i>ꜰɪʟᴇꜱ ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ ᴍᴏᴍᴇɴᴛᴀʀɪʟʏ...</i>"
        )

        await temp_msg.edit(final_success_msg)
        await asyncio.sleep(1.5)

        sent_messages = await send_files_with_progress(client, message, messages, temp_msg)

        return sent_messages

    except Exception as e:
        error_msg = (
            f"❌ <b>ᴏᴏᴘꜱ! ꜱᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ!</b>\n\n"
            f"🔧 <b>ᴇʀʀᴏʀ ᴅᴇᴛᴀɪʟꜱ:</b> {str(e)}\n"
            f"📞 <b>ɴᴇᴇᴅ ʜᴇʟᴘ?</b> ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ\n\n"
            f"<i>ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ɪɴ ᴀ ᴍᴏᴍᴇɴᴛ...</i>"
        )
        await temp_msg.edit(error_msg)
        return []


async def send_files_with_progress(client, message, messages, progress_msg):
    sent_messages = []
    total_files = len(messages)

    for index, msg in enumerate(messages, 1):
        try:
            progress_text = (
                f"📤 <b>ꜱᴇɴᴅɪɴɢ ꜰɪʟᴇꜱ...</b>\n\n"
                f"📁 <b>ꜰɪʟᴇ {index}</b> ᴏꜰ {total_files}\n"
                f"⚡ <b>ꜱᴛᴀᴛᴜꜱ:</b> ᴄᴏᴍᴘʟᴇᴛᴇ... !!!"
            )

            await progress_msg.edit(progress_text)

            if bool(CUSTOM_CAPTION) and msg.document:
                caption = CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name,
                )
            else:
                caption = "" if not msg.caption else msg.caption.html

            reply_markup = msg.reply_markup if not DISABLE_CHANNEL_BUTTON else None

            sent_msg = await msg.copy(
                chat_id=message.from_user.id,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                protect_content=PROTECT_CONTENT,
            )
            sent_messages.append(sent_msg)

        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                sent_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT,
                )
                sent_messages.append(sent_msg)
            except Exception:
                continue

        except Exception as e:
            print(f"Failed to send message: {e}")
            continue

    # Final completion message (left to progress message flow; not forcibly edited here)
    return sent_messages


# ================================================================================== #
# Auto-delete scheduler (merged from start (1).py). This is the single added auto-delete
# function integrated safely with existing logic. It schedules deletion and updates the
# notification message with a "Get file again" button when available.
# ================================================================================== #
async def schedule_auto_delete(client, codeflix_msgs, notification_msg, file_auto_delete, reload_url):
    try:
        await asyncio.sleep(file_auto_delete)
    except Exception as e:
        # If sleep is interrupted or invalid, still attempt to continue safely
        print(f"Auto-delete sleep interrupted or errored: {e}")

    deleted_count = 0
    for snt_msg in codeflix_msgs:
        if snt_msg:
            try:
                await snt_msg.delete()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting message {getattr(snt_msg, 'id', 'unknown')}: {e}")
                continue

    try:
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("ɢᴇᴛ ғɪʟᴇ ᴀɢᴀɪɴ!", url=reload_url)]]
        ) if reload_url else None

        # Safely edit the notification message to indicate files were deleted
        await notification_msg.edit(
            "<b>ʏᴏᴜʀ ᴠɪᴅᴇᴏ / ꜰɪʟᴇꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ.</b>\n\n"
            f"✅ ᴅᴇʟᴇᴛᴇᴅ {deleted_count} ꜰɪʟᴇꜱ\n\n"
            "<i>Click the button below to get them again (if available).</i>",
            reply_markup=keyboard,
        )
    except Exception as e:
        print(f"Error updating notification with 'Get File Again' button: {e}")


# ================================================================================== #
# /start command — main flow (keeps your enhanced verification, caching, progress UI)
# ================================================================================== #
@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    id = message.from_user.id
    is_premium = await is_premium_user(id)

    # Check if user is banned
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_text(
            "⛔️ <b>ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ</b>\n\n"
            "<i>ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ ɪꜰ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪꜱ ɪꜱ ᴀ ᴍɪꜱᴛᴀᴋᴇ</i>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ", url=BAN_SUPPORT)]]),
        )

    # Enhanced admin verification with caching
    if user_id in await db.get_all_admins():
        verify_status = {
            "is_verified": True,
            "verify_token": None,
            "verified_time": time.time(),
            "link": "",
            "verified_count": 0,
        }
        verification_cache[user_id] = verify_status
    else:
        if user_id in verification_cache:
            verify_status = verification_cache[user_id]
        else:
            verify_status = await db.get_verify_status(id)
            verification_cache[user_id] = verify_status

        if SHORTLINK_URL or SHORTLINK_API:
            if verify_status.get("is_verified") and VERIFY_EXPIRE < (time.time() - verify_status.get("verified_time", 0)):
                await db.update_verify_status(user_id, is_verified=False)
                verify_status["is_verified"] = False
                verification_cache[user_id] = verify_status

            if "verify_" in (message.text or ""):
                try:
                    _, token = message.text.split("_", 1)

                    if verify_status.get("verify_token") != token:
                        if user_id in verification_cache:
                            del verification_cache[user_id]
                        return await message.reply(
                            "❌ <b>ʏᴏᴜʀ ᴛᴏᴋᴇɴ ɪꜱ ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ</b>\n\nᴛʀʏ ᴀɢᴀɪɴ ʙʏ ᴄʟɪᴄᴋɪɴɢ /start"
                        )

                    await db.update_verify_status(id, is_verified=True, verified_time=time.time())
                    verify_status["is_verified"] = True
                    verify_status["verified_time"] = time.time()

                    current = await db.get_verify_count(id)
                    new_count = current + 1
                    await db.set_verify_count(id, new_count)
                    verify_status["verified_count"] = new_count

                    verification_cache[user_id] = verify_status

                    button_text = "📁 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ғɪʟᴇ"
                    button_url = verify_status.get("link") or "https://t.me/spideyofficialupdatez"

                    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=button_url)]])

                    await message.reply_photo(
                        photo=VERIFY_IMG,
                        caption=f"<blockquote><b>✅ ʜᴇʏ {message.from_user.mention}, ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱ꜠ᴜʟ!\n\n🎉 ʏᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ ꜰᴏʀ {get_exp_time(VERIFY_EXPIRE)}\n\nᴛᴏᴋᴇɴ ᴜꜱᴇᴅ: {new_count} ᴛɪᴍᴇꜱ</blockquote></b>",
                        reply_markup=reply_markup,
                    )

                    await verify_user(client, id, token)

                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    current_date = now.strftime("%Y-%m-%d")

                    log_msg = (
                        f"🎯 <b>ᴇɴʜᴀɴᴄᴇᴅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴜᴄᴄᴇꜱ꜠ᴜʟ</b>\n\n"
                        f"👤 ᴜꜱᴇʀ: {message.from_user.mention}\n"
                        f"🆔 ɪᴅ: <code>{message.from_user.id}</code>\n"
                        f"📊 ᴛᴏᴛᴀʟ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴꜱ: {new_count}\n"
                        f"🕒 ᴛɪᴍᴇ: {current_time}\n"
                        f"📅 ᴅᴀᴛᴇ: {current_date}\n"
                        f"⏰ ᴀᴄᴄᴇꜱꜱ ᴅᴜʀᴀᴛɪᴏɴ: {get_exp_time(VERIFY_EXPIRE)}\n"
                        f"#ᴠᴇʀɪꜰʏ_ᴄᴏᴍᴘʟᴇᴛᴇᴅ #ᴜꜱᴇʀ_{user_id}"
                    )
                    await client.send_message(chat_id=VERIFIED_LOG, text=log_msg)

                except Exception as e:
                    print(f"Verification error: {e}")
                    return await message.reply("❌ <b>ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ</b>\n\nᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ")

            if not verify_status.get("is_verified") and not is_premium:
                token = "".join(random.choices(spidey.ascii_letters + spidey.digits, k=12))
                await db.update_verify_status(id, verify_token=token, link="")
                verify_status["verify_token"] = token
                verification_cache[user_id] = verify_status

                try:
                    link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f"https://telegram.dog/{client.username}?start=verify_{token}")
                except Exception as e:
                    print(f"Shortlink error: {e}")
                    link = f"https://telegram.dog/{client.username}?start=verify_{token}"

                btn = [
                    [InlineKeyboardButton("🔗 ᴏᴘᴇɴ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ", url=link)],
                    [InlineKeyboardButton("📺 ᴛᴜᴛᴏʀɪᴀʟ ᴠɪᴅᴇᴏ", url=TUT_VID)],
                    [
                        InlineKeyboardButton("💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium"),
                        InlineKeyboardButton("🆓 ꜰʀᴇᴇ ᴛʀɪᴀʟ", callback_data="free_trial"),
                    ],
                ]

                return await message.reply_photo(
                    photo=VERIFY_REQUIERD_IMG,
                    caption=script.VERIFICATION_TXT.format(mention=message.from_user.mention, expire=get_exp_time(VERIFY_EXPIRE)),
                    reply_markup=InlineKeyboardMarkup(btn),
                    quote=True,
                )

    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    FILE_AUTO_DELETE = await db.get_del_timer()

    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
            await client.send_message(
                CHANNEL_ID,
                script.NEW_USER_TXT.format(
                    temp.B_LINK,
                    message.from_user.id,
                    message.from_user.mention,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        except Exception as e:
            print(f"User registration error: {e}")

    text = message.text or ""
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except IndexError:
            return

        string = await decode(base64_string)
        argument = string.split("-")

        ids = []
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
                ids = range(start, end + 1) if start <= end else list(range(start, end - 1, -1))
            except Exception as e:
                print(f"Error decoding IDs: {e}")
                return await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ꜰɪʟᴇ ʀᴀɴɢᴇ ᴘʀᴏᴠɪᴅᴇᴅ</b>")
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"Error decoding ID: {e}")
                return await message.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ꜰɪʟᴇ ɪᴅ ᴘʀᴏᴠɪᴅᴇᴅ</b>")

        # Use enhanced file processing with beautiful progress
        sent_messages = await enhanced_file_processing(client, message, ids)

        # Enhanced auto-delete notification
        if FILE_AUTO_DELETE > 0 and len(sent_messages) > 0:
            expiry_time = get_exp_time(FILE_AUTO_DELETE)

            notification_msg = await message.reply(
                f"📦 <b>ꜰɪʟᴇ ᴅᴇʟɪᴠᴇʀʏ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"
                f"✅ ꜱᴜᴄᴄᴇꜱ꜠ᴜʟʟʏ ꜱᴇɴᴛ: {len(sent_messages)} ꜰɪʟᴇꜱ\n"
                f"⏰ <b>ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪɴ:</b> {expiry_time}\n"
                f"💾 <b>ᴛɪᴘ:</b> ꜱᴀᴠᴇ ꜰɪʟᴇꜱ ᴛᴏ ʏᴏᴜʀ ꜱᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ !!!"
            )

            reload_url = f"https://t.me/{client.username}?start={message.command[1]}" if len(message.command) > 1 else None

            # Schedule auto-delete using the integrated scheduler
            try:
                asyncio.create_task(schedule_auto_delete(client, sent_messages, notification_msg, FILE_AUTO_DELETE, reload_url))
            except Exception as e:
                print(f"Error scheduling auto-delete task: {e}")

        elif len(sent_messages) == 0:
            await message.reply_text("❌ <b>ɴᴏ ꜰɪʟᴇꜱ ᴄᴏᴜʟᴅ ʙᴇ ᴅᴇʟɪᴠᴇʀᴇᴅ</b>\n\nᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ !!!")

    else:
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📢 ᴍᴏʀᴇ ᴄʜᴀɴɴᴇʟꜱ", callback_data="group_info")],
                [InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about"), InlineKeyboardButton("🆘 ʜᴇʟᴘ", callback_data="help")],
                [InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium"), InlineKeyboardButton("📊 ꜱᴛᴀᴛꜱ", callback_data="stats")],
            ]
        )

        effects = [
            5104841245755180586,
            5159385139981059251,
            5046509860389126442,
            5107584321108051014,
        ]

        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else "@" + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id,
            ),
            reply_markup=reply_markup,
            message_effect_id=int(random.choice(effects)),
        )


# Enhanced verification cache cleanup function
async def cleanup_verification_cache():
    while True:
        await asyncio.sleep(3600)
        current_time = time.time()
        expired_users = []

        for user_id, data in list(verification_cache.items()):
            if data.get("is_verified") and VERIFY_EXPIRE < (current_time - data.get("verified_time", 0)):
                expired_users.append(user_id)

        for user_id in expired_users:
            if user_id in verification_cache:
                del verification_cache[user_id]

        if expired_users:
            print(f"Cleaned up {len(expired_users)} expired verification cache entries")


@Bot.on_message(filters.command("start"))
async def start_cache_cleanup(client, message):
    if not hasattr(client, "cache_cleanup_task"):
        client.cache_cleanup_task = asyncio.create_task(cleanup_verification_cache())


# ================================================================================== #
# /features and /status handlers (single copies; duplicates removed)
# ================================================================================== #
@Bot.on_message(filters.command("features") & filters.private)
async def show_features(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")],
        [InlineKeyboardButton("🆓 ᴛʀʏ ꜰʀᴇᴇ ᴛʀɪᴀʟ", callback_data="free_trial")],
        [InlineKeyboardButton("📊 ᴍʏ ꜱᴛᴀᴛᴜꜱ", callback_data="mystatus")],
    ]

    await message.reply_photo(photo="https://graph.org/file/7519d226226bec1090db7.jpg", caption=script.FEATURES_TXT, reply_markup=InlineKeyboardMarkup(buttons))


@Bot.on_message(filters.command("status") & filters.private)
async def user_status(client: Client, message: Message):
    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)

    verify_status = verification_cache.get(user_id, await db.get_verify_status(user_id))

    status_text = f"""
📊 <b>ᴜꜱᴇʀ ꜱᴛᴀᴛᴜꜱ</b>

👤 <b>ᴜꜱᴇʀ:</b> {message.from_user.mention}
🆔 <b>ɪᴅ:</b> <code>{user_id}</code>
💎 <b>ᴘʀᴇᴍɪᴜᴍ:</b> {'✅ ᴀᴄᴛɪᴠᴇ' if is_premium else '❌ ɪɴᴀᴄᴛɪᴠᴇ'}
🔐 <b>ᴠᴇʀɪꜰɪᴇᴅ:</b> {'✅ ʏᴇꜱ' if verify_status.get('is_verified') else '❌ ɴᴏ'}
"""
    if verify_status.get("is_verified"):
        verified_time = verify_status.get("verified_time", 0)
        time_left = VERIFY_EXPIRE - (time.time() - verified_time)
        if time_left > 0:
            status_text += f"⏳ <b>ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴇxᴘɪʀᴇꜱ ɪɴ:</b> {get_exp_time(time_left)}\n"

    if is_premium:
        premium_info = await get_premium_info(user_id)
        if premium_info:
            status_text += f"⭐ <b>ᴘʀᴇᴍɪᴜᴍ ᴇxᴘɪʀᴇꜱ:</b> {premium_info['expiry']}\n"

    status_text += f"\n📈 <b>ᴛᴏᴛᴀʟ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴꜱ:</b> {verify_status.get('verified_count', 0)}"

    buttons = [
        [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ", callback_data="premium")],
        [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇꜱʜ", callback_data="refresh_status")],
    ]

    await message.reply_text(status_text, reply_markup=InlineKeyboardMarkup(buttons))


# ================================================================================== #
# Email test callback (keeps original handling)
# ================================================================================== #
@Bot.on_callback_query(filters.regex(r"^email_test$"))
async def email_test_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.answer("🧪 ꜱᴛᴀʀᴛɪɴɢ ᴇɴʜᴀɴᴄᴇᴅ ᴇᴍᴀɪʟ ꜱᴇʀᴠɪᴄᴇ ᴛᴇꜱᴛ...")

    processing_msg = await callback_query.message.reply_text(
        "🧪 <b>ᴇɴʜᴀɴᴄᴇᴅ ᴇᴍᴀɪʟ ꜱᴇʀᴠɪᴄᴇ ᴛᴇꜱᴛ</b>\n\n"
        "🔍 ᴛᴇꜱᴛɪɴɢ ᴄᴏᴍᴘᴏɴᴇɴᴛꜱ:\n"
        "• ꜱᴍᴛᴘ ᴄᴏɴɴᴇᴄᴛɪᴏɴ & ᴀᴜᴛʜᴇɴᴛɪᴄᴀᴛɪᴏɴ\n"
        "• ʙᴀᴄᴋᴜᴘ ꜱᴇʀᴠᴇʀ ꜰᴀʟʟʙᴀᴄᴋ\n"
        "• ᴀᴅᴍɪɴ ᴇᴍᴀɪʟ ᴅᴇʟɪᴠᴇʀʏ\n"
        "• ᴜꜱᴇʀ ᴇᴍᴀɪʟ ᴅᴇʟɪᴠᴇʀʏ\n"
        "• ᴄᴏɴɴᴇᴄᴛɪᴏɴ ꜱᴛᴀʙɪʟɪᴛʏ\n\n"
        "<i>ᴛʜɪꜱ ᴍᴀʏ ᴛᴀᴋᴇ 15-30 ꜱᴇᴄᴏɴᴅꜱ...</i>"
    )

    user_email = None
    try:
        status = await email_system.get_subscription_status(user_id)
        if status.get("success") and status.get("subscribed"):
            user_email = status.get("email")
    except Exception as e:
        print(f"Error getting user email: {e}")

    test_results = await email_system.test_email_service(user_id=user_id, user_email=user_email)

    await processing_msg.delete()

    if test_results.get("overall_success"):
        result_text = "✅ <b>ᴇᴍᴀɪʟ ᴛᴇꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱ꜠ᴜʟʟʏ!</b>\n\n"
        result_text += f"📊 <b>ᴛᴇꜱᴛ ɪᴅ:</b> <code>{test_results['test_id']}</code>\n"
        result_text += f"🕒 <b>ᴅᴜʀᴀᴛɪᴏɴ:</b> {test_results.get('duration', 'ɴ/ᴀ')}ꜱ\n"
        result_text += f"🎯 <b>ꜱᴜᴄᴄᴇꜱ꜠ᴜʟ ʀᴀᴛᴇ:</b> {test_results.get('success_percentage', 0)}%\n"
        result_text += f"🔗 <b>ꜱᴇʀᴠᴇʀ:</b> {test_results['configuration']['smtp_server']}\n\n"

        result_text += "<b>ᴅᴇᴛᴀɪʟᴇᴅ ʀᴇꜱᴜʟᴛꜱ:</b>\n"
        for test_name, test_result in test_results["tests"].items():
            status = "✅" if test_result.get("success") else "❌"
            emoji = "🔗" if "connection" in test_name else "📧"
            result_text += f"{emoji} {status} <b>{test_name.replace('_', ' ').title()}:</b> {test_result.get('message', 'ɴ/ᴀ')}\n"

        result_text += f"\n📨 <i>ᴛᴇꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ᴀᴛ {test_results['timestamp']}</i>"

    else:
        result_text = "❌ <b>ᴇᴍᴀɪʟ ᴛᴇꜱᴛ ꜰᴀɪʟᴇᴅ!</b>\n\n"
        result_text += f"📊 <b>ᴛᴇꜱᴛ ɪᴅ:</b> <code>{test_results.get('test_id', 'ɴ/ᴀ')}</code>\n"
        result_text += f"🚫 <b>ᴇʀʀᴏʀ:</b> {test_results.get('error', 'ᴜɴᴋɴᴏᴡɴ ᴇʀʀᴏʀ')}\n\n"

        result_text += "<b>ꜰᴀɪʟᴇᴅ ᴛᴇꜱᴛꜱ:</b>\n"
        for test_name, test_result in test_results.get("tests", {}).items():
            if not test_result.get("success"):
                result_text += f"❌ <b>{test_name.replace('_', ' ').title()}:</b> {test_result.get('message', 'ɴ/ᴀ')}\n"

        result_text += "\n🔧 <b>ᴘᴏꜱꜱɪʙʟᴇ ꜱᴏʟᴜᴛɪᴏɴꜱ:</b>\n"
        result_text += "• ᴄʜᴇᴄᴋ ꜱᴍᴛᴘ ᴄʀᴇᴅᴇɴᴛɪᴀʟꜱ ɪɴ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀᴛʙʟᴇꜱ\n"
        result_text += "• ᴠᴇʀɪꜰʏ ᴇᴍᴀɪʟ ᴘᴀꜱꜱᴡᴏʀᴅ (ᴜꜱᴇ ᴀᴘᴘ ᴘᴀꜱꜱᴡᴏʀᴅ ꜰᴏʀ ɢᴍᴀɪʟ)\n"
        result_text += "• ᴇɴꜱᴜʀᴇ ʟᴇꜱꜱ ꜱᴇᴄᴜʀᴇ ᴀᴘᴘꜱ ᴀʀᴇ ᴇɴᴀʙʟᴇᴅ (ɪꜰ ᴜꜱɪɴɢ ɢᴍᴀɪʟ)\n"
        result_text += "• ᴄʜᴇᴄᴋ ꜰɪʀᴇᴡᴀʟʟ/ᴘᴏʀᴛ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ\n"

    buttons = [
        [InlineKeyboardButton("🔄 ʀᴜɴ ᴛᴇꜱᴛ ᴀɢᴀɪɴ", callback_data="email_test")],
        [InlineKeyboardButton("📊 ꜱʏꜱᴛᴇᴍ ᴅɪᴀɢɴᴏꜱᴛɪᴄꜱ", callback_data="email_diagnostics")],
        [InlineKeyboardButton("⚙️ ꜱᴍᴛᴘ ꜱᴇᴛᴛɪɴɢꜱ ʜᴇʟᴘ", callback_data="smtp_help")],
        [InlineKeyboardButton("📧 ᴍᴀɴᴀɢᴇ ꜱᴜꜱʙᴄʀɪᴘᴛɪᴏɴ", callback_data="email_manage")],
    ]

    await callback_query.message.edit_text(result_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)


# ================================================================================== #
# Premium management commands (addpremium, remove_premium, premium_users)
# ================================================================================== #
@Bot.on_message(filters.command("myplan") & filters.private)
async def check_plan(client: Client, message: Message):
    user_id = message.from_user.id
    status_message = await check_user_plan(user_id)
    await message.reply(status_message)


@Bot.on_message(filters.command("addpremium") & filters.private & admin)
async def add_premium_user_command(client, msg: Message):
    if len(msg.command) != 4:
        await msg.reply_text(
            "ᴜꜱᴀɢᴇ: /addpremium <user_id> <time_value> <time_unit>\n\n"
            "ᴛɪᴍᴇ ᴜɴɪᴛꜱ:\n"
            "ꜱ - ꜱᴇᴄᴏɴᴅꜱ\n"
            "ᴍ - ᴍɪɴᴜᴛᴇꜱ\n"
            "ʜ - ʜᴏᴜʀꜱ\n"
            "ᴅ - ᴅᴀʏꜱ\n"
            "ʏ - ʏᴇᴀʀꜱ\n\n"
            "ᴇxᴀᴍᴘʟᴇꜱ:\n"
            "/addpremium 123456789 30 ᴍ → 30 ᴍɪɴᴜᴛᴇꜱ\n"
            "/addpremium 123456789 2 ʜ → 2 ʜᴏᴜʀꜱ\n"
            "/addpremium 123456789 1 ᴅ → 1 ᴅᴀʏ\n"
            "/addpremium 123456789 1 ʏ → 1 ʏᴇᴀʀ"
        )
        return

    try:
        user_id = int(msg.command[1])
        time_value = int(msg.command[2])
        time_unit = msg.command[3].lower()
        expiration_time = await add_premium(user_id, time_value, time_unit)

        await msg.reply_text(
            f"✅ ᴜꜱᴇʀ `{user_id}` ᴀᴅᴅᴇᴅ ᴀꜱ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ ꜰᴏʀ {time_value} {time_unit}.\n"
            f"ᴇxᴘɪʀᴀᴛɪᴏɴ ᴛɪᴍᴇ: `{expiration_time}`"
        )

        await client.send_message(
            chat_id=user_id,
            text=(
                f"🎉 <b>ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n\n"
                f"ʏᴏᴜ ʜᴀᴠᴇ ʀᴇᴄᴇɪᴠᴇᴅ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇꜱᴋ ꜰᴏʀ `{time_value} {time_unit}`.\n"
                f"ᴇxᴘɪʀᴀᴛɪᴏɴ: `{expiration_time}`"
            ),
        )

    except ValueError:
        await msg.reply_text("❌ <b>ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ</b>\n\nᴘʟᴇᴀꜱᴇ ᴇɴꜱᴜʀᴇ ᴜꜱᴇʀ ɪᴅ ᴀɴᴅ ᴛɪᴍᴇ ᴠᴀʟᴜᴇ ᴀʀᴇ ɴᴜᴍʙᴇʀꜱ")
    except Exception as e:
        await msg.reply_text(f"⚠️ <b>ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:</b> `{str(e)}`")


@Bot.on_message(filters.command("remove_premium") & filters.private & admin)
async def pre_remove_user(client: Client, msg: Message):
    if len(msg.command) != 2:
        await msg.reply_text("ᴜꜱᴀɢᴇ: /remove_premium ᴜꜱᴇʀ_ɪᴅ")
        return
    try:
        user_id = int(msg.command[1])
        await remove_premium(user_id)
        await msg.reply_text(f"ᴜꜱᴇʀ {user_id} ʜᴀꜱ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ")
    except ValueError:
        await msg.reply_text("ᴜꜱᴇʀ_ɪᴅ ᴍᴜꜱᴛ ʙᴇ ᴀɴ ɪɴᴛᴇɢᴇʀ ᴏʀ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ")


@Bot.on_message(filters.command("premium_users") & filters.private & admin)
async def list_premium_users_command(client: Client, message: Message):
    from pytz import timezone

    ist = timezone("Asia/Kolkata")
    premium_users_cursor = collection.find({})
    premium_user_list = ["<b>ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ɪɴ ᴅᴀᴛᴀʙᴀꜱᴇ:</b>"]
    current_time = datetime.now(ist)

    async for user in premium_users_cursor:
        user_id = user["user_id"]
        expiration_timestamp = user["expiration_timestamp"]
        try:
            expiration_time = datetime.fromisoformat(expiration_timestamp).astimezone(ist)
            remaining_time = expiration_time - current_time
            if remaining_time.total_seconds() <= 0:
                await collection.delete_one({"user_id": user_id})
                continue

            user_info = await client.get_users(user_id)
            username = user_info.username if user_info.username else "ɴᴏ ᴜꜱᴇʀɴᴀᴍᴇ"
            mention = user_info.mention
            days, hours, minutes, seconds = (
                remaining_time.days,
                remaining_time.seconds // 3600,
                (remaining_time.seconds // 60) % 60,
                remaining_time.seconds % 60,
            )
            expiry_info = f"{days}ᴅ {hours}ʜ {minutes}ᴍ {seconds}ꜱ ʟᴇꜰᴛ"
            premium_user_list.append(
                f"ᴜꜱᴇʀɪᴅ: <code>{user_id}</code>\n"
                f"ᴜꜱᴇʀ: @{username}\n"
                f"ɴᴀᴍᴇ: {mention}\n"
                f"ᴇxᴘɪʀʏ: {expiry_info}"
            )
        except Exception as e:
            premium_user_list.append(
                f"ᴜꜱᴇʀɪᴅ: <code>{user_id}</code>\n" f"ᴇʀʀᴏʀ: ᴜɴᴀʙʟᴇ ᴛᴏ ꜰᴇᴛᴄʜ ᴜꜱᴇʀ ᴅᴇᴛᴀɪʟꜱ ({str(e)})"
            )

    if len(premium_user_list) == 1:
        await message.reply_text("ɪ ꜰᴏᴜɴᴅ 0 ᴀᴄᴛɪᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀꜱ ɪɴ ᴍʏ ᴅʙ")
    else:
        await message.reply_text("\n\n".join(premium_user_list))


# ================================================================================== #
# Misc commands and admin utilities
# ================================================================================== #
@Bot.on_message(filters.command("count") & filters.private & admin)
async def total_verify_count_cmd(client: Client, message: Message):
    total = await db.get_total_verify_count()
    await message.reply_text(f"ᴛᴏᴛᴀʟ ᴠᴇʀɪꜰɪᴇᴅ ᴛᴏᴋᴇꜱ ᴛᴏᴅᴀʏ: <b>{total}</b>")


@Bot.on_message(filters.command("commands") & filters.private & admin)
async def bcmd(bot: Bot, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏꜱᴇ •", callback_data="close")]])
    await message.reply(text=CMD_TXT, reply_markup=reply_markup, quote=True)


# Plan command
@Bot.on_message(filters.command("plan") & filters.private)
async def plan_command(client: Client, message: Message):
    mention = message.from_user.mention
    buttons = [
        [InlineKeyboardButton("ʀᴇꜰᴇʀ ᴀɴᴅ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ", callback_data="reffff")],
        [InlineKeyboardButton("ʙʀᴏɴᴢᴇ ", callback_data="broze"), InlineKeyboardButton("ꜱɪʟᴠᴇʀ ", callback_data="silver")],
        [InlineKeyboardButton("ɢᴏʟᴅ ", callback_data="gold"), InlineKeyboardButton("ᴘʟᴀᴛɪɴᴜᴍ ", callback_data="platinum")],
        [InlineKeyboardButton("ᴅɪᴀᴍᴏɴᴅ ", callback_data="diamond"), InlineKeyboardButton("ᴏᴛʜᴇʀ ", callback_data="other")],
        [InlineKeyboardButton("ᴅɪɢ ᴛʀɪᴀʟ 𝟻 ᴍɪɴ", callback_data="free")],
        [InlineKeyboardButton("⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋", callback_data="start")],
    ]

    await message.reply_photo(photo="https://graph.org/file/7519d226226bec1090db7.jpg", caption=script.PREPLANS_TXT.format(mention), reply_markup=InlineKeyboardMarkup(buttons))


# ================================================================================== #
# Force-subscription helper (not_joined) - kept from the start (1).py merged version
# ================================================================================== #
# Create a simple cache to avoid repeated get_chat calls
chat_data_cache = {}


async def not_joined(client: Client, message: Message):
    temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>")
    user_id = message.from_user.id
    buttons = []
    count = 0

    try:
        all_channels = await db.show_channels()
        for total, chat_id in enumerate(all_channels, start=1):
            try:
                mode = await db.get_channel_mode(chat_id)
            except Exception:
                mode = None

            await message.reply_chat_action(ChatAction.TYPING)

            try:
                if chat_id in chat_data_cache:
                    data = chat_data_cache[chat_id]
                else:
                    data = await client.get_chat(chat_id)
                    chat_data_cache[chat_id] = data

                name = data.title

                if mode == "on" and not data.username:
                    invite = await client.create_chat_invite_link(
                        chat_id=chat_id,
                        creates_join_request=True,
                        expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None,
                    )
                    link = invite.invite_link
                else:
                    if data.username:
                        link = f"https://t.me/{data.username}"
                    else:
                        invite = await client.create_chat_invite_link(
                            chat_id=chat_id,
                            expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None,
                        )
                        link = invite.invite_link

                buttons.append([InlineKeyboardButton(text=name, url=link)])
                count += 1
                await temp.edit(f"<b>{'! ' * count}</b>")
            except Exception as e:
                print(f"Error with chat {chat_id}: {e}")
                return await temp.edit(
                    f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @rohit_1888</i></b>\n"
                    f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                )

        try:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="♻️ Tʀʏ Aɢᴀɪɴ",
                        url=f"https://t.me/{client.username}?start={message.command[1]}" if message.command and len(message.command) > 1 else f"https://t.me/{client.username}",
                    )
                ]
            )
        except Exception:
            pass

        await message.reply_photo(photo=FORCE_PIC, caption=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else "@" + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id,
        ), reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        print(f"Final Error: {e}")
        await temp.edit(
            f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @hacker_x_official_777</i></b>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
        )
