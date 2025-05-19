from pyrogram import Client 
from bot import Bot
from config import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto, ChatPermissions, WebAppInfo, InputMediaAnimation, InputMediaPhoto
from pyrogram import Client, filters, enums
from database.database import *
from Script import script

@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "help":
        await query.message.edit_text(
            text=HELP_TXT.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('ʜᴏᴍᴇ', callback_data='start'),
                 InlineKeyboardButton("ᴄʟᴏꜱᴇ", callback_data='close')]
            ])
        )

    elif data == "about":
        await query.message.edit_text(text="● ◌ ◌")
        await query.message.edit_text(text="● ● ◌")
        await query.message.edit_text(text="● ● ●")

        features_keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("‼️ ᴅɪꜱᴄʟᴀɪᴍᴇʀ ‼️", callback_data="disclaimer")],
                [
                    InlineKeyboardButton(
                        "• ᴠɪsɪᴛ ᴏᴜʀ ᴄᴏᴍᴍᴜɴɪᴛʏ •", url="t.me/SPIDEYOFFICIAL_777"
                    )
                ],
                [
                    InlineKeyboardButton("• ᴏᴡɴᴇʀ •", user_id=int(7965267063)),
                    InlineKeyboardButton("• sᴏᴜʀᴄᴇ •", callback_data="source"),
                ],
                [InlineKeyboardButton("🛰️ ʀᴇɴᴅᴇʀɪɴɢ ꜱᴛᴀᴛᴜꜱ ☁️", callback_data="rendr")],
                [InlineKeyboardButton("⋞ Back ᴛᴏ ʜᴏᴍᴇ ", callback_data="back")],
            ]
        )

        await query.message.edit_text(
            script.ABOUT_TXT, reply_markup=features_keyboard
        )

    elif data == "start":
        await query.message.edit_text(
            text=START_MSG.format(first=query.from_user.first_name),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ʜᴇʟᴘ", callback_data='help'),
                 InlineKeyboardButton("ᴀʙᴏᴜᴛ", callback_data='about')]
            ])
        )


    elif data == "premium":
        await query.message.delete()
        await client.send_photo(
            chat_id=query.message.chat.id,
            photo=QR_PIC,
            caption=(
                f"👋 {query.from_user.username}\n\n"
                f"🎖️ Available Plans :\n\n"
                f"● {PRICE1}  For 25 Days Prime Membership\n\n"
                f"● {PRICE2}  For 1 Month Prime Membership\n\n"
                f"● {PRICE3}  For 3 Months Prime Membership\n\n"
                f"● {PRICE4}  For 6 Months Prime Membership\n\n"
                f"● {PRICE5}  For 1 Year Prime Membership\n\n\n"
                f"💵 ASK UPI ID TO ADMIN AND PAY THERE -  <code>{UPI_ID}</code>\n\n\n"
                f"♻️ After Payment You Will Get Instant Membership \n\n\n"
                f"‼️ Must Send Screenshot after payment & If anyone want custom time membrship then ask admin"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "ADMIN 24/7", url=(SCREENSHOT_URL)
                        )
                    ],
                    [InlineKeyboardButton("🔒 Close", callback_data="close")],
                ]
            )
        )



    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await db.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "ᴏғғ" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        cid, action = data.split("_")[2:]
        cid = int(cid)
        mode = "on" if action == "on" else "off"

        await db.set_channel_mode(cid, mode)
        await query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        # Refresh the same channel's mode view
        chat = await client.get_chat(cid)
        status = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await query.message.edit_text(
            f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "fsub_back":
        channels = await db.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await db.get_channel_mode(cid)
                status = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except:
                continue

        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "seeplans":
        btn = [[
            InlineKeyboardButton('🍁 𝗖𝗹𝗶𝗰𝗸 𝗔𝗹𝗹 𝗣𝗹𝗮𝗻𝘀 & 𝗣𝗿𝗶𝗰𝗲𝘀 🍁', callback_data='free')
        ],[
            InlineKeyboardButton('• 𝗖𝗹𝗼𝘀𝗲 •', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(btn)
        m=await query.message.reply_sticker("CAACAgQAAxkBAAEiLZ9l7VMuTY7QHn4edR6ouHUosQQ9gwACFxIAArzT-FOmYU0gLeJu7x4E") 
        await m.delete()
        await query.message.reply_photo(
            photo=(SUBSCRIPTION),
            caption=script.PREPLANS_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)
    #Spidey        
    elif data == "xyz":
        buttons = [[
            InlineKeyboardButton('☎️ 𝗖𝗼𝗻𝘁𝗮𝗰𝘁 𝗢𝘄𝗻𝗲𝗿 𝗧𝗼 𝗞𝗻𝗼𝘄 𝗠𝗼𝗿𝗲', user_id = ADMINS[0])
        ],[
            InlineKeyboardButton('• 𝗕𝗮𝗰𝗸 •', callback_data='free')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PAYPICS))
        )
        await query.message.edit_text(
            text=script.OTHER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
	)
    elif data == "premium_info":
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
        
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/7519d226226bec1090db7.jpg")
        )
        await query.message.edit_text(
            text=script.PREPLANS_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
           
    elif data == "free":
        buttons = [[
            InlineKeyboardButton('⚜️ ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ꜰʀᴇᴇ ᴛʀɪᴀʟ', callback_data="give_trial")
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='other'),
            InlineKeyboardButton('1 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='broze')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FREE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif data == "broze":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='free'),
            InlineKeyboardButton('2 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='silver')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/670f6df9f755dc2c9a00a.jpg")
        )
        await query.message.edit_text(
            text=script.BRONZE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "silver":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='broze'),
            InlineKeyboardButton('3 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='gold')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/670f6df9f755dc2c9a00a.jpg")
        )
        await query.message.edit_text(
            text=script.SILVER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif data == "gold":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='silver'),
            InlineKeyboardButton('4 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='platinum')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/670f6df9f755dc2c9a00a.jpg")
        )
        await query.message.edit_text(
            text=script.GOLD_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "platinum":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='gold'),
            InlineKeyboardButton('5 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='diamond')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/670f6df9f755dc2c9a00a.jpg")
        )
        await query.message.edit_text(
            text=script.PLATINUM_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "diamond":
        buttons = [[
            InlineKeyboardButton('🔐 ᴄʟɪᴄᴋ ʜᴇʀᴇ ᴛᴏ ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ', callback_data='purchase')
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='platinum'),
            InlineKeyboardButton('6 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='other')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.DIAMOND_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif data == "purchase":
        buttons = [[
            InlineKeyboardButton('💵 ᴘᴀʏ ᴠɪᴀ ᴜᴘɪ ɪᴅ 💵', callback_data='upi_info')
        ],[
            InlineKeyboardButton('📸 ꜱᴄᴀɴ ǫʀ ᴄᴏᴅᴇ 📸', callback_data='qr_info')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/7519d226226bec1090db7.jpg")
        )
        await query.message.edit_text(
            text=script.PURCHASE_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif data == "upi_info":
        buttons = [[
            InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʜᴇʀᴇ', url=OWNER_LNK)
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='purchase')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/7519d226226bec1090db7.jpg")
        )
        await query.message.edit_text(
            text=script.UPI_TXT.format(query.from_user.mention, OWNER_UPI_ID),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif data == "qr_info":
        buttons = [[
            InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ ʜᴇʀᴇ', url=OWNER_LNK)
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='purchase')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/7519d226226bec1090db7.jpg")
        )
        await query.message.edit_text(
            text=script.QR_TXT.format(query.from_user.mention, QR_CODE),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
    elif data == "other":
        buttons = [[
            InlineKeyboardButton('☎️ ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ', url="t.me/hacker_x_official_777")
        ],[
            InlineKeyboardButton('⋞ ʙᴀᴄᴋ', callback_data='diamond'),
            InlineKeyboardButton('7 / 7', callback_data='pagesn1'),
            InlineKeyboardButton('ɴᴇxᴛ ⋟', callback_data='free')
        ],[
            InlineKeyboardButton('⇋ ʙᴀᴄᴋ ⇋', callback_data='premium_info')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await Bot.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto("https://graph.org/file/670f6df9f755dc2c9a00a.jpg")
        )
        await query.message.edit_text(
            text=script.OTHER_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif data == "group_info":
        await query.message.edit_text(text="● ◌ ◌")
        await query.message.edit_text(text="● ● ◌")
        await query.message.edit_text(text="● ● ●")

        buttons = [
            [
                InlineKeyboardButton(
                    "× ᴀʟʟ ᴏᴜʀ ʟɪɴᴋꜱ ×", url="https://t.me/SPIDEYOFFICIAL777"
                )
            ],
            [
                InlineKeyboardButton("• ᴍᴏᴠɪᴇ ɢʀᴏᴜᴘ •", url="https://t.me/+KTXnXf_YPxJlOGRl"),
                InlineKeyboardButton(
                    "• ᴜᴘᴅᴀᴛᴇs •", url="https://t.me/SpideyOfficialUpdatez"
                ),
            ],
            [
                InlineKeyboardButton("• ʜᴀᴄᴋ •", url="https://t.me/+cMlrPqMjUwtmNTI1"),
                InlineKeyboardButton(
                    "• 𝟷𝟾+ 🚫 •", url="https://t.me/movie_flex_official"
                ),
            ],
            [
                InlineKeyboardButton(
                    "• ᴄɪɴᴇғʟɪx •", url="https://t.me/+QVmLP_hlHNw3M2I1"
                )
            ],
            [InlineKeyboardButton("⪻ ʙᴀᴄᴋ •", callback_data="back")],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await query.message.edit_text(
            text=script.CHANNELS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
        )

    elif data == "close_data":
        try:
            user = query.message.reply_to_message.from_user.id
        except:
            user = query.from_user.id

        if int(user) != 0 and query.from_user.id != int(user):
            return await query.answer(script.ALRT_TXT, show_alert=True)

        await query.answer("ᴛʜᴀɴᴋs ꜰᴏʀ ᴄʟᴏsᴇ")
        await query.message.delete()

        try:
            await query.message.reply_to_message.delete()
        except:
            pass

    elif data == "source":
        await query.message.edit_text(text="● ◌ ◌")
        await query.message.edit_text(text="● ● ◌")
        await query.message.edit_text(text="● ● ●")

        buttons = [
        [
                InlineKeyboardButton("⪻ ʙᴀᴄᴋ", callback_data="about"),
                InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", callback_data="group_info"),
        ]
    ]

        reply_markup = InlineKeyboardMarkup(buttons)


        await query.message.edit_text(
            text=script.SOURCE_TXT.format(
                query.from_user.mention if query.from_user else "User"
            ),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            )
                                      