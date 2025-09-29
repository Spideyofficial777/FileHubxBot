# Don't Remove Credit @Spideyofficial777
# Ask Doubt on telegram @Spideyofficial777
#
# Copyright (C) 2025 by Spidey Official, < https://t.me/Spideyofficial777 >.
#
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
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, ChatInviteLink, ChatPrivileges
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
# 🎯 ENHANCED VERIFICATION CACHE CLASS
class VerificationCache:
    def __init__(self):
        self._cache = {}
    
    async def get(self, user_id):
        if user_id in self._cache:
            data, timestamp = self._cache[user_id]
            if time.time() - timestamp < 3600:  # 1 hour TTL
                return data
            else:
                del self._cache[user_id]
        return None
    
    async def set(self, user_id, data):
        self._cache[user_id] = (data, time.time())
    
    async def delete(self, user_id):
        if user_id in self._cache:
            del self._cache[user_id]
    
    async def cleanup_expired(self):
        current_time = time.time()
        expired = [uid for uid, (_, timestamp) in self._cache.items() 
                  if current_time - timestamp >= 3600]
        for uid in expired:
            del self._cache[uid]

# Initialize enhanced cache
verification_cache = VerificationCache()

@Bot.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    id = message.from_user.id
    is_premium = await is_premium_user(id)

    # 🔥 ENHANCED BAN CHECK WITH STYLISH UI
    banned_users = await db.get_ban_users()
    if user_id in banned_users:
        return await message.reply_photo(
            photo="https://telegra.ph/file/c78645947613fcdb9a1d0.jpg",
            caption="🚫 <b>ᴀᴄᴄᴏᴜɴᴛ ʀᴇꜱᴛʀɪᴄᴛᴇᴅ</b>\n\n"
                   "⛔️ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ꜰʀᴏᴍ ᴜꜱɪɴɢ ᴛʜɪꜱ ʙᴏᴛ\n\n"
                   "<i>ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ ɪꜰ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪꜱ ɪꜱ ᴀ ᴍɪꜱᴛᴀᴋᴇ</i>",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📧 ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ", url=BAN_SUPPORT)]]
            )
        )

    # ⚡ ENHANCED ADMIN VERIFICATION WITH CACHE
    if user_id in await db.get_all_admins():
        verify_status = {
            'is_verified': True,
            'verify_token': None, 
            'verified_time': time.time(),
            'link': "",
            'verified_count': 0,
            'user_type': 'admin'
        }
        await verification_cache.set(user_id, verify_status)
        
        # 👑 ADMIN SPECIAL WELCOME
        if len(message.text) <= 7:
            await message.reply_photo(
                photo=START_PIC,
                caption=f"👑 <b>ᴡᴇʟᴄᴏᴍᴇ ᴀᴅᴍɪɴ {message.from_user.mention}!</b>\n\n"
                       f"🆔 <b>ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>\n"
                       f"📊 <b>ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ:</b> {await db.total_users_count()}\n\n"
                       f"<i>ʏᴏᴜ ʜᴀᴠᴇ ꜰᴜʟʟ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ</i>",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📊 ᴅᴀꜱʜʙᴏᴀʀᴅ", callback_data="admin")],
                    [InlineKeyboardButton("👥 ᴜꜱᴇʀꜱ", callback_data="users_stats"),
                     InlineKeyboardButton("📈 ꜱᴛᴀᴛꜱ", callback_data="stats")]
                ])
            )
            return

    else:
        # 🔍 SMART CACHE VERIFICATION SYSTEM
        verify_status = await verification_cache.get(user_id)
        if not verify_status:
            verify_status = await db.get_verify_status(id)
            await verification_cache.set(user_id, verify_status)

        # 🎯 ENHANCED VERIFICATION HANDLING
        if SHORTLINK_URL or SHORTLINK_API:
            # ⏰ CHECK VERIFICATION EXPIRY
            if verify_status['is_verified'] and VERIFY_EXPIRE < (time.time() - verify_status['verified_time']):
                await db.update_verify_status(user_id, is_verified=False)
                verify_status['is_verified'] = False
                await verification_cache.set(user_id, verify_status)

            # 🔑 TOKEN VERIFICATION PROCESS
            if "verify_" in message.text:
                try:
                    _, token = message.text.split("_", 1)
                    
                    # 🛡️ ENHANCED TOKEN VALIDATION
                    if verify_status['verify_token'] != token:
                        await verification_cache.delete(user_id)
                        return await message.reply_photo(
                            photo="https://telegra.ph/file/25d81e95a59a58745b4b2.jpg",
                            caption="❌ <b>ᴛᴏᴋᴇɴ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜰᴀɪʟᴇᴅ</b>\n\n"
                                   "• ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ᴛᴏᴋᴇɴ\n"
                                   "• ᴛᴏᴋᴇɴ ᴍᴀʏ ʜᴀᴠᴇ ʙᴇᴇɴ ᴜꜱᴇᴅ ᴀʟʀᴇᴀᴅʏ\n"
                                   "• ꜱᴇꜱꜱɪᴏɴ ᴍɪɢʜᴛ ʜᴀᴠᴇ ᴇxᴘɪʀᴇᴅ\n\n"
                                   "🔄 <b>ꜱᴏʟᴜᴛɪᴏɴ:</b>\n"
                                   "ᴄʟɪᴄᴋ /ꜱᴛᴀʀᴛ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ᴀ ɴᴇᴡ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🔄 ᴛʀʏ ᴀɢᴀɪɴ", callback_data="restart_verification")]
                            ])
                        )
                    
                    # ✅ UPDATE VERIFICATION STATUS
                    await db.update_verify_status(id, is_verified=True, verified_time=time.time())
                    verify_status['is_verified'] = True
                    verify_status['verified_time'] = time.time()
                    
                    # 📈 UPDATE VERIFICATION COUNT
                    current = await db.get_verify_count(id)
                    new_count = current + 1
                    await db.set_verify_count(id, new_count)
                    verify_status['verified_count'] = new_count
                    
                    # 💾 UPDATE CACHE
                    await verification_cache.set(user_id, verify_status)

                    # 🎉 ENHANCED SUCCESS MESSAGE
                    await message.reply_animation(
                        animation="https://telegra.ph/file/4c64144118b4d7291a804.mp4",
                        caption=f"🎉 <b>ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b> 🎉\n\n"
                               f"👤 <b>ᴡᴇʟᴄᴏᴍᴇ:</b> {message.from_user.mention}\n"
                               f"✅ <b>ꜱᴛᴀᴛᴜꜱ:</b> ꜰᴜʟʟʏ ᴠᴇʀɪꜰɪᴇᴅ\n"
                               f"⏰ <b>ᴀᴄᴄᴇꜱꜱ ᴅᴜʀᴀᴛɪᴏɴ:</b> {get_exp_time(VERIFY_EXPIRE)}\n"
                               f"🔢 <b>ᴛᴏᴋᴇɴꜱ ᴜꜱᴇᴅ:</b> {new_count}\n"
                               f"📅 <b>ᴠᴇʀɪꜰɪᴇᴅ ᴏɴ:</b> {datetime.now().strftime('%d %b %Y ᴀᴛ %I:%M %p')}\n\n"
                               f"<i>ʏᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ ᴜɴʟɪᴍɪᴛᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴛᴏ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ!</i>",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("📁 ᴀᴄᴄᴇꜱꜱ ꜰɪʟᴇꜱ", callback_data="get_files")],
                            [InlineKeyboardButton("💎 ɢᴏ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium"),
                             InlineKeyboardButton("📊 ᴘʀᴏꜰɪʟᴇ", callback_data="profile")]
                        ])
                    )

                    # 📊 ENHANCED USER VERIFICATION LOGGING
                    await verify_user(client, id, token)

                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    current_date = now.strftime("%Y-%m-%d")

                    log_msg = (
                        f"🎯 <b>ᴇɴʜᴀɴᴄᴇᴅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ</b>\n\n"
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
                    print(f"ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴇʀʀᴏʀ: {e}")
                    return await message.reply(
                        "🔴 <b>ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴇʀʀᴏʀ</b>\n\n"
                        "ᴡᴇ ᴇɴᴄᴏᴜɴᴛᴇʀᴇᴅ ᴀɴ ɪꜱꜱᴜᴇ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ʏᴏᴜʀ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ.\n\n"
                        "<b>ᴘʟᴇᴀꜱᴇ ᴛʀʏ:</b>\n"
                        "1. ᴄʟɪᴄᴋ /ꜱᴛᴀʀᴛ ᴀɢᴀɪɴ\n"
                        "2. ᴜꜱᴇ ᴀ ɴᴇᴡ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʟɪɴᴋ\n"
                        "3. ᴄᴏɴᴛᴀᴄᴛ ꜱᴜᴘᴘᴏʀᴛ ɪꜰ ɪꜱꜱᴜᴇ ᴘᴇʀꜱɪꜱᴛꜱ"
                    )

            # 🔐 SHOW VERIFICATION REQUIRED MESSAGE
            if not verify_status['is_verified'] and not is_premium:
                # 🔑 GENERATE SECURE TOKEN
                token = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
                await db.update_verify_status(id, verify_token=token, link="")
                verify_status['verify_token'] = token
                await verification_cache.set(user_id, verify_status)
                
                # 🔗 ENHANCED SHORTLINK GENERATION
                try:
                    link = await get_shortlink(SHORTLINK_URL, SHORTLINK_API, f'https://telegram.dog/{client.username}?start=verify_{token}')
                except Exception as e:
                    print(f"ꜱʜᴏʀᴛʟɪɴᴋ ᴇʀʀᴏʀ: {e}")
                    link = f'https://telegram.dog/{client.username}?start=verify_{token}'
                
                # 🎨 STYLISH VERIFICATION BUTTONS
                btn = [
                    [InlineKeyboardButton("🔗 ꜱᴛᴀʀᴛ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ", url=link)], 
                    [InlineKeyboardButton('📺 ʜᴏᴡ ᴛᴏ ᴠᴇʀɪꜰʏ', url=TUT_VID)],
                    [
                        InlineKeyboardButton('💎 ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ', callback_data='premium'),
                        InlineKeyboardButton('🆓 ꜰʀᴇᴇ ᴛʀɪᴀʟ', callback_data='free_trial')
                    ],
                    [InlineKeyboardButton("❓ ɴᴇᴇᴅ ʜᴇʟᴘ?", callback_data="verification_help")]
                ]
                
                # 📝 ENHANCED VERIFICATION MESSAGE
                verification_text = f"""
🔐 <b>ᴀᴄᴄᴏᴜɴᴛ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ</b>

👋 <b>ʜᴇʟʟᴏ {message.from_user.first_name}!</b>

ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ᴜꜱɪɴɢ ᴏᴜʀ ꜱᴇʀᴠɪᴄᴇꜱ ᴀɴᴅ ᴀᴄᴄᴇꜱꜱ ᴀʟʟ ꜰᴇᴀᴛᴜʀᴇꜱ, ᴡᴇ ʀᴇQᴜɪʀᴇ ᴀ Qᴜɪᴄᴋ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ.

<b>📋 ᴡʜᴀᴛ ʜᴀᴘᴘᴇɴꜱ ɴᴇxᴛ?</b>
1. ᴄʟɪᴄᴋ ᴛʜᴇ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ
2. ᴄᴏᴍᴘʟᴇᴛᴇ ᴏɴᴇ ꜱɪᴍᴘʟᴇ ꜱᴛᴇᴘ
3. ɢᴇᴛ ɪɴꜱᴛᴀɴᴛ ᴀᴄᴄᴇꜱꜱ ꜰᴏʀ {get_exp_time(VERIFY_EXPIRE)}

<b>⭐ ᴘʀᴇᴍɪᴜᴍ ʙᴇɴᴇꜰɪᴛꜱ:</b>
• ɴᴏ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ʀᴇQᴜɪʀᴇᴅ
• ꜰᴀꜱᴛᴇʀ ᴀᴄᴄᴇꜱꜱ
• ᴘʀɪᴏʀɪᴛʏ ꜱᴜᴘᴘᴏʀᴛ
• ᴇɴʜᴀɴᴄᴇᴅ ꜰᴇᴀᴛᴜʀᴇꜱ

<b>🛡️ 100% ꜱᴀꜰᴇ & ꜱᴇᴄᴜʀᴇ</b>
• ɴᴏ ᴘᴇʀꜱᴏɴᴀʟ ᴅᴀᴛᴀ ᴄᴏʟʟᴇᴄᴛᴇᴅ
• ɪɴꜱᴛᴀɴᴛ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ
• ᴇɴᴄʀʏᴘᴛᴇᴅ ᴘʀᴏᴄᴇꜱꜱ
"""
                return await message.reply_photo(
                    photo=VERIFY_IMG,
                    caption=verification_text,
                    reply_markup=InlineKeyboardMarkup(btn),
                    protect_content=False,
                    quote=True
                )

    # 📢 ENHANCED FORCE SUBSCRIPTION CHECK
    if not await is_subscribed(client, user_id):
        return await not_joined(client, message)

    # ⏰ ENHANCED AUTO-DELETE WITH USER PREFERENCES
    FILE_AUTO_DELETE = await db.get_del_timer()

    # 👤 ENHANCED USER REGISTRATION
    if not await db.present_user(user_id):
        try:
            await db.add_user(user_id)
            # 📨 ENHANCED NEW USER NOTIFICATION
            join_time = datetime.now().strftime("%d %b %Y ᴀᴛ %I:%M %p")
            await client.send_message(
                CHANNEL_ID, 
                f"🆕 <b>ɴᴇᴡ ᴜꜱᴇʀ ʀᴇɢɪꜱᴛᴇʀᴇᴅ</b>\n\n"
                f"👤 <b>ᴜꜱᴇʀ:</b> {message.from_user.mention}\n"
                f"🆔 <b>ɪᴅ:</b> <code>{user_id}</code>\n"
                f"📛 <b>ꜰɪʀꜱᴛ ɴᴀᴍᴇ:</b> {message.from_user.first_name}\n"
                f"👥 <b>ᴜꜱᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username if message.from_user.username else 'ɴᴏɴᴇ'}\n"
                f"⏰ <b>ᴊᴏɪɴᴇᴅ ᴀᴛ:</b> {join_time}\n\n"
                f"#ɴᴇᴡ_ᴜꜱᴇʀ #ɪᴅ_{user_id}"
            )
        except Exception as e:
            print(f"ᴜꜱᴇʀ ʀᴇɢɪꜱᴛʀᴀᴛɪᴏɴ ᴇʀʀᴏʀ: {e}")

    # 📁 ENHANCED FILE HANDLING SYSTEM
    text = message.text
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
                print(f"ᴇʀʀᴏʀ ᴅᴇᴄᴏᴅɪɴɢ ɪᴅꜱ: {e}")
                return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ꜰɪʟᴇ ʀᴀɴɢᴇ ᴘʀᴏᴠɪᴅᴇᴅ.")

        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception as e:
                print(f"ᴇʀʀᴏʀ ᴅᴇᴄᴏᴅɪɴɢ ɪᴅ: {e}")
                return await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ꜰɪʟᴇ ɪᴅ ᴘʀᴏᴠɪᴅᴇᴅ.")

        # ⏳ ENHANCED PROGRESS INDICATOR
        temp_msg = await message.reply("🔄 <b>ᴘʀᴏᴄᴇꜱꜱɪɴɢ ʏᴏᴜʀ ʀᴇQᴜᴇꜱᴛ...</b>")
        
        try:
            messages = await get_messages(client, ids)
        except Exception as e:
            await temp_msg.delete()
            return await message.reply_text("❌ ꜰᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ꜰɪʟᴇꜱ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
        
        await temp_msg.delete()

        # 📤 ENHANCED FILE SENDING WITH BATCH PROCESSING
        sent_messages = []
        success_count = 0
        fail_count = 0

        for msg in messages:
            try:
                # 📝 ENHANCED CAPTION HANDLING
                if bool(CUSTOM_CAPTION) and msg.document:
                    caption = CUSTOM_CAPTION.format(
                        previouscaption="" if not msg.caption else msg.caption.html,
                        filename=msg.document.file_name
                    )
                else:
                    caption = "" if not msg.caption else msg.caption.html

                reply_markup = msg.reply_markup if not DISABLE_CHANNEL_BUTTON else None

                # 🚀 SEND FILE WITH ENHANCED ERROR HANDLING
                sent_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                sent_messages.append(sent_msg)
                success_count += 1

            except FloodWait as e:
                await asyncio.sleep(e.x)
                try:
                    sent_msg = await msg.copy(
                        chat_id=message.from_user.id,
                        caption=caption,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup,
                        protect_content=PROTECT_CONTENT
                    )
                    sent_messages.append(sent_msg)
                    success_count += 1
                except Exception as flood_error:
                    print(f"ꜰʟᴏᴏᴅᴡᴀɪᴛ ᴇʀʀᴏʀ: {flood_error}")
                    fail_count += 1

            except Exception as e:
                print(f"ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇ: {e}")
                fail_count += 1

        # 🗑️ ENHANCED AUTO-DELETE NOTIFICATION
        if FILE_AUTO_DELETE > 0 and success_count > 0:
            expiry_time = get_exp_time(FILE_AUTO_DELETE)
            
            notification_msg = await message.reply(
                f"📦 <b>ꜰɪʟᴇ ᴅᴇʟɪᴠᴇʀʏ ꜱᴜᴍᴍᴀʀʏ</b>\n\n"
                f"✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇɴᴛ: {success_count} ꜰɪʟᴇꜱ\n"
                f"❌ ꜰᴀɪʟᴇᴅ: {fail_count} ꜰɪʟᴇꜱ\n\n"
                f"⏰ <b>ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ ɪɴ:</b> {expiry_time}\n"
                f"💾 <b>ꜱᴀᴠᴇ ꜰɪʟᴇꜱ ᴛᴏ ʏᴏᴜʀ ꜱᴀᴠᴇᴅ ᴍᴇꜱꜱᴀɢᴇꜱ</b>"
            )

            # ⏰ ENHANCED AUTO-DELETE FUNCTIONALITY
            await asyncio.sleep(FILE_AUTO_DELETE)

            deleted_count = 0
            for sent_msg in sent_messages:
                if sent_msg:
                    try:
                        await sent_msg.delete()
                        deleted_count += 1
                    except Exception as e:
                        print(f"ᴇʀʀᴏʀ ᴅᴇʟᴇᴛɪɴɢ ᴍᴇꜱꜱᴀɢᴇ: {e}")

            # 📝 ENHANCED POST-DELETE NOTIFICATION
            try:
                reload_url = f"https://t.me/{client.username}?start={message.command[1]}" if len(message.command) > 1 else None
                
                keyboard = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔄 ɢᴇᴛ ꜰɪʟᴇꜱ ᴀɢᴀɪɴ", url=reload_url)]]
                ) if reload_url else None

                await notification_msg.edit(
                    f"🗑️ <b>ᴀᴜᴛᴏ-ᴄʟᴇᴀɴᴜᴘ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>\n\n"
                    f"✅ ᴅᴇʟᴇᴛᴇᴅ {deleted_count} ꜰɪʟᴇꜱ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ\n"
                    f"📝 ꜰɪʟᴇꜱ ᴀʀᴇ ɴᴏ ʟᴏɴɢᴇʀ ᴀᴄᴄᴇꜱꜱɪʙʟᴇ ꜰʀᴏᴍ ᴛʜɪꜱ ᴄʜᴀᴛ\n\n"
                    f"<i>ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ꜰɪʟᴇꜱ ᴀɢᴀɪɴ</i>",
                    reply_markup=keyboard
                )
            except Exception as e:
                print(f"ɴᴏᴛɪꜰɪᴄᴀᴛɪᴏɴ ᴜᴘᴅᴀᴛᴇ ᴇʀʀᴏʀ: {e}")

        elif success_count == 0:
            await message.reply_text("❌ ɴᴏ ꜰɪʟᴇꜱ ᴄᴏᴜʟᴅ ʙᴇ ᴅᴇʟɪᴠᴇʀᴇᴅ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ.")

    else:
        # 🎊 ENHANCED WELCOME MESSAGE WITH BETTER UI
        reply_markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📢 ᴍᴏʀᴇ ᴄʜᴀɴɴᴇʟꜱ", url="https://t.me/Spideyofficial777")],
                [
                    InlineKeyboardButton("ℹ️ ᴀʙᴏᴜᴛ", callback_data="about"),
                    InlineKeyboardButton("🆘 ʜᴇʟᴘ", callback_data="help")
                ],
                [
                    InlineKeyboardButton("💎 ᴘʀᴇᴍɪᴜᴍ", callback_data="premium"),
                    InlineKeyboardButton("📊 ꜱᴛᴀᴛꜱ", callback_data="stats")
                ],
                [InlineKeyboardButton("🔐 ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ꜱᴛᴀᴛᴜꜱ", callback_data="verification_status")]
            ]
        )
        
        # ✨ ENHANCED WELCOME MESSAGE WITH RANDOM EFFECTS
        effects = [
            5104841245755180586,  # 🔥 ꜰɪʀᴇ
            5159385139981059251,  # 🎈 ʙᴀʟʟᴏᴏɴꜱ  
            5046509860389126442,  # 🎊 ᴄᴏɴꜰᴇᴛᴛɪ
            5107584321108051014,  # ✨ ꜱᴘᴀʀᴋʟᴇꜱ
            5104927257829441566,  # 🌟 ꜱᴛᴀʀꜱ
            5104854308671914026   # 💫 ᴘᴜʟꜱᴇ
        ]
        
        await message.reply_photo(
            photo=START_PIC,
            caption=START_MSG.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name,
                username=None if not message.from_user.username else '@' + message.from_user.username,
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            message_effect_id=int(random.choice(effects))
        )

# 🧹 ENHANCED VERIFICATION CACHE CLEANUP FUNCTION
async def cleanup_verification_cache():
    """ᴄʟᴇᴀɴ ᴜᴘ ᴇxᴘɪʀᴇᴅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴄᴀᴄʜᴇ ᴘᴇʀɪᴏᴅɪᴄᴀʟʟʏ"""
    while True:
        await asyncio.sleep(3600)  # ᴄʟᴇᴀɴ ᴇᴠᴇʀʏ ʜᴏᴜʀ
        current_time = time.time()
        expired_users = []
        
        for user_id, (data, timestamp) in verification_cache._cache.items():
            if data.get('is_verified') and VERIFY_EXPIRE < (current_time - data.get('verified_time', 0)):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            await verification_cache.delete(user_id)
        
        if expired_users:
            print(f"ᴄʟᴇᴀɴᴇᴅ ᴜᴘ {len(expired_users)} ᴇxᴘɪʀᴇᴅ ᴠᴇʀɪꜰɪᴄᴀᴛɪᴏɴ ᴄᴀᴄʜᴇ ᴇɴᴛʀɪᴇꜱ")

# 🚀 START CACHE CLEANUP TASK
@Bot.on_message(filters.command('start'))
async def start_cache_cleanup(client, message):
    # ꜱᴛᴀʀᴛ ʙᴀᴄᴋɢʀᴏᴜɴᴅ ᴛᴀꜱᴋ ɪꜰ ɴᴏᴛ ᴀʟʀᴇᴀᴅʏ ʀᴜɴɴɪɴɢ
    if not hasattr(client, 'cache_cleanup_task'):
        client.cache_cleanup_task = asyncio.create_task(cleanup_verification_cache())
        
# Enhanced premium features
@Bot.on_message(filters.command('features') & filters.private)
async def show_features(client: Client, message: Message):
    features_text = """
🚀 <b>Enhanced Features</b>

<b>Free Users:</b>
✅ File Access (with verification)
✅ Auto-delete protection
✅ Basic support

<b>Premium Users:</b>
⭐ No verification required
⭐ Priority file delivery  
⭐ Extended auto-delete time
⭐ Exclusive content access
⭐ Priority support
⭐ Higher download limits
⭐ Early feature access

<b>Admin Features:</b>
👑 User management
📊 Advanced analytics
🔧 Bot configuration
⚡ Instant support
"""
    
    buttons = [
        [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ", callback_data="premium")],
        [InlineKeyboardButton("🆓 ᴛʀʏ ꜰʀᴇᴇ ᴛʀɪᴀʟ", callback_data="free_trial")],
        [InlineKeyboardButton("📊 ᴍʏ ꜱᴛᴀᴛᴜꜱ", callback_data="mystatus")]
    ]
    
    await message.reply_photo(
        photo="https://graph.org/file/7519d226226bec1090db7.jpg",
        caption=features_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Enhanced status command
@Bot.on_message(filters.command('status') & filters.private)
async def user_status(client: Client, message: Message):
    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)
    
    # Get verification status from cache
    verify_status = verification_cache.get(user_id, await db.get_verify_status(user_id))
    
    status_text = f"""
📊 <b>User Status</b>

👤 <b>User:</b> {message.from_user.mention}
🆔 <b>ID:</b> <code>{user_id}</code>
💎 <b>Premium:</b> {'✅ Active' if is_premium else '❌ Inactive'}
🔐 <b>Verified:</b> {'✅ Yes' if verify_status.get('is_verified') else '❌ No'}

"""
    
    if verify_status.get('is_verified'):
        verified_time = verify_status.get('verified_time', 0)
        time_left = VERIFY_EXPIRE - (time.time() - verified_time)
        if time_left > 0:
            status_text += f"⏳ <b>Verification expires in:</b> {get_exp_time(time_left)}\n"
    
    if is_premium:
        premium_info = await get_premium_info(user_id)
        if premium_info:
            status_text += f"⭐ <b>Premium expires:</b> {premium_info['expiry']}\n"
    
    status_text += f"\n📈 <b>Total verifications:</b> {verify_status.get('verified_count', 0)}"
    
    buttons = [
        [InlineKeyboardButton("💎 ᴜᴘɢʀᴀᴅᴇ", callback_data="premium")],
        [InlineKeyboardButton("🔄 ʀᴇꜰʀᴇꜱʜ", callback_data="refresh_status")]
    ]
    
    await message.reply_text(status_text, reply_markup=InlineKeyboardMarkup(buttons))

# from pyrogram.types import CallbackQuery
# from email_system import email_system
# Fixed Email Test Callback Handler
@Bot.on_callback_query(filters.regex(r"^email_test$"))
async def email_test_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    await callback_query.answer("🧪 Starting enhanced email service test...")
    
    # Show testing message
    processing_msg = await callback_query.message.reply_text(
        "🧪 <b>Enhanced Email Service Test</b>\n\n"
        "🔍 Testing components:\n"
        "• SMTP Connection & Authentication\n"
        "• Backup Server Fallback\n"
        "• Admin Email Delivery\n"
        "• User Email Delivery\n"
        "• Connection Stability\n\n"
        "<i>This may take 15-30 seconds...</i>"
    )
    
    # Get user's email from database
    user_email = None
    try:
        status = await email_system.get_subscription_status(user_id)
        if status.get('success') and status.get('subscribed'):
            user_email = status.get('email')
    except Exception as e:
        logger.error(f"Error getting user email: {e}")
    
    # Run comprehensive test
    test_results = await email_system.test_email_service(
        user_id=user_id,
        user_email=user_email
    )
    
    await processing_msg.delete()
    
    # Prepare detailed result message
    if test_results.get('overall_success'):
        result_text = "✅ <b>Email Test Completed Successfully!</b>\n\n"
        result_text += f"📊 <b>Test ID:</b> <code>{test_results['test_id']}</code>\n"
        result_text += f"🕒 <b>Duration:</b> {test_results.get('duration', 'N/A')}s\n"
        result_text += f"🎯 <b>Success Rate:</b> {test_results.get('success_percentage', 0)}%\n"
        result_text += f"🔗 <b>Server:</b> {test_results['configuration']['smtp_server']}\n\n"
        
        result_text += "<b>Detailed Results:</b>\n"
        for test_name, test_result in test_results['tests'].items():
            status = "✅" if test_result.get('success') else "❌"
            emoji = "🔗" if "connection" in test_name else "📧"
            result_text += f"{emoji} {status} <b>{test_name.replace('_', ' ').title()}:</b> {test_result.get('message', 'N/A')}\n"
        
        result_text += f"\n📨 <i>Test completed at {test_results['timestamp']}</i>"
        
    else:
        result_text = "❌ <b>Email Test Failed!</b>\n\n"
        result_text += f"📊 <b>Test ID:</b> <code>{test_results.get('test_id', 'N/A')}</code>\n"
        result_text += f"🚫 <b>Error:</b> {test_results.get('error', 'Unknown error')}\n\n"
        
        result_text += "<b>Failed Tests:</b>\n"
        for test_name, test_result in test_results.get('tests', {}).items():
            if not test_result.get('success'):
                result_text += f"❌ <b>{test_name.replace('_', ' ').title()}:</b> {test_result.get('message', 'N/A')}\n"
        
        result_text += "\n🔧 <b>Possible Solutions:</b>\n"
        result_text += "• Check SMTP credentials in environment variables\n"
        result_text += "• Verify email password (use App Password for Gmail)\n"
        result_text += "• Ensure less secure apps are enabled (if using Gmail)\n"
        result_text += "• Check firewall/port restrictions\n"
    
    # Enhanced buttons with diagnostics
    buttons = [
        [InlineKeyboardButton("🔄 Run Test Again", callback_data="email_test")],
        [InlineKeyboardButton("📊 System Diagnostics", callback_data="email_diagnostics")],
        [InlineKeyboardButton("⚙️ SMTP Settings Help", callback_data="smtp_help")],
        [InlineKeyboardButton("📧 Manage Subscription", callback_data="email_manage")]
    ]
    
    await callback_query.message.edit_text(
        result_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
@Bot.on_message(filters.command('myplan') & filters.private)
async def check_plan(client: Client, message: Message):
    user_id = message.from_user.id  # Get user ID from the message

    # Get the premium status of the user
    status_message = await check_user_plan(user_id)

    # Send the response message to the user
    await message.reply(status_message)

#=====================================================================================##
# Command to add premium user
@Bot.on_message(filters.command('addpremium') & filters.private & admin)
async def add_premium_user_command(client, msg):
    if len(msg.command) != 4:
        await msg.reply_text(
            "Usage: /addpremium <user_id> <time_value> <time_unit>\n\n"
            "Time Units:\n"
            "s - seconds\n"
            "m - minutes\n"
            "h - hours\n"
            "d - days\n"
            "y - years\n\n"
            "Examples:\n"
            "/addpremium 123456789 30 m → 30 minutes\n"
            "/addpremium 123456789 2 h → 2 hours\n"
            "/addpremium 123456789 1 d → 1 day\n"
            "/addpremium 123456789 1 y → 1 year"
        )
        return

    try:
        user_id = int(msg.command[1])
        time_value = int(msg.command[2])
        time_unit = msg.command[3].lower()  # supports: s, m, h, d, y

        # Call add_premium function
        expiration_time = await add_premium(user_id, time_value, time_unit)

        # Notify the admin
        await msg.reply_text(
            f"✅ User `{user_id}` added as a premium user for {time_value} {time_unit}.\n"
            f"Expiration Time: `{expiration_time}`"
        )

        # Notify the user
        await client.send_message(
            chat_id=user_id,
            text=(
                f"🎉 Premium Activated!\n\n"
                f"You have received premium access for `{time_value} {time_unit}`.\n"
                f"Expires on: `{expiration_time}`"
            ),
        )

    except ValueError:
        await msg.reply_text("❌ Invalid input. Please ensure user ID and time value are numbers.")
    except Exception as e:
        await msg.reply_text(f"⚠️ An error occurred: `{str(e)}`")


# Command to remove premium user
@Bot.on_message(filters.command('remove_premium') & filters.private & admin)
async def pre_remove_user(client: Client, msg: Message):
    if len(msg.command) != 2:
        await msg.reply_text("useage: /remove_premium user_id ")
        return
    try:
        user_id = int(msg.command[1])
        await remove_premium(user_id)
        await msg.reply_text(f"User {user_id} has been removed.")
    except ValueError:
        await msg.reply_text("user_id must be an integer or not available in database.")


# Command to list active premium users
@Bot.on_message(filters.command('premium_users') & filters.private & admin)
async def list_premium_users_command(client, message):
    # Define IST timezone
    ist = timezone("Asia/Kolkata")

    # Retrieve all users from the collection
    premium_users_cursor = collection.find({})
    premium_user_list = ['Active Premium Users in database:']
    current_time = datetime.now(ist)  # Get current time in IST

    # Use async for to iterate over the async cursor
    async for user in premium_users_cursor:
        user_id = user["user_id"]
        expiration_timestamp = user["expiration_timestamp"]

        try:
            # Convert expiration_timestamp to a timezone-aware datetime object in IST
            expiration_time = datetime.fromisoformat(expiration_timestamp).astimezone(ist)

            # Calculate remaining time
            remaining_time = expiration_time - current_time

            if remaining_time.total_seconds() <= 0:
                # Remove expired users from the database
                await collection.delete_one({"user_id": user_id})
                continue  # Skip to the next user if this one is expired

            # If not expired, retrieve user info
            user_info = await client.get_users(user_id)
            username = user_info.username if user_info.username else "No Username"
            first_name = user_info.first_name
            mention=user_info.mention

            # Calculate days, hours, minutes, seconds left
            days, hours, minutes, seconds = (
                remaining_time.days,
                remaining_time.seconds // 3600,
                (remaining_time.seconds // 60) % 60,
                remaining_time.seconds % 60,
            )
            expiry_info = f"{days}d {hours}h {minutes}m {seconds}s left"

            # Add user details to the list
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"User: @{username}\n"
                f"Name: {mention}\n"
                f"Expiry: {expiry_info}"
            )
        except Exception as e:
            premium_user_list.append(
                f"UserID: <code>{user_id}</code>\n"
                f"Error: Unable to fetch user details ({str(e)})"
            )

    if len(premium_user_list) == 1:  # No active users found
        await message.reply_text("I found 0 active premium users in my DB")
    else:
        await message.reply_text("\n\n".join(premium_user_list), parse_mode=None)


#=====================================================================================##

@Bot.on_message(filters.command("count") & filters.private & admin)
async def total_verify_count_cmd(client, message: Message):
    total = await db.get_total_verify_count()
    await message.reply_text(f"Tᴏᴛᴀʟ ᴠᴇʀɪғɪᴇᴅ ᴛᴏᴋᴇɴs ᴛᴏᴅᴀʏ: <b>{total}</b>")


#=====================================================================================##

@Bot.on_message(filters.command('commands') & filters.private & admin)
async def bcmd(bot: Bot, message: Message):        
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴄʟᴏsᴇ •", callback_data = "close")]])
    await message.reply(text=CMD_TXT, reply_markup = reply_markup, quote= True)



@Bot.on_message(filters.command("plan") & filters.private)
async def plan_command(client: Client, message: Message):
    mention = message.from_user.mention

    buttons = [[
        InlineKeyboardButton('ʀᴇғᴇʀ ᴀɴᴅ ɢᴇᴛ ᴘʀᴇᴍɪᴜᴍ', callback_data='reffff'),
    ],[
        InlineKeyboardButton('ʙʀᴏɴᴢᴇ ', callback_data='broze'),
        InlineKeyboardButton('ꜱɪʟᴠᴇʀ ', callback_data='silver')
    ],[
        InlineKeyboardButton('ɢᴏʟᴅ ', callback_data='gold'),
        InlineKeyboardButton('ᴘʟᴀᴛɪɴᴜᴍ ', callback_data='platinum')
    ],[
        InlineKeyboardButton('ᴅɪᴀᴍᴏɴᴅ ', callback_data='diamond'),
        InlineKeyboardButton('ᴏᴛʜᴇʀ ', callback_data='other')
    ],[
        InlineKeyboardButton('ɢᴇᴛ ғʀᴇᴇ ᴛʀᴀɪʟ ғᴏʀ 𝟻 ᴍɪɴᴜᴛᴇs ☺️', callback_data='free')
    ],[
        InlineKeyboardButton('⇋ ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ ⇋', callback_data='start')
    ]]

    await message.reply_photo(
        photo="https://graph.org/file/7519d226226bec1090db7.jpg",
        caption=script.PREPLANS_TXT.format(mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
