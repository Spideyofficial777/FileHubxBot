import os
from os import environ, getenv
import logging
from logging.handlers import RotatingFileHandler

# =========================[ BOT CREDENTIALS ]========================= #

# Bot token from @BotFather
TG_BOT_TOKEN = environ.get("TG_BOT_TOKEN", "")

# Your API credentials from my.telegram.org
APP_ID = int(environ.get("APP_ID", "28519661"))
API_HASH = environ.get("API_HASH", "your_api_hash_here")

# =========================[ CHANNEL CONFIG ]========================== #

CHANNEL_ID = int(environ.get("CHANNEL_ID", "-1002423451263"))
VERIFIED_LOG = int(environ.get("VERIFIED_LOG", "-1002423451263"))
OWNER = environ.get("OWNER", "hacker_x_official_777")  # Without @
OWNER_ID = int(environ.get("OWNER_ID", "7965267063"))
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", "-1002294764885"))
CHANNEL = int(environ.get("CHANNEL", "-1002423451263"))
UPDATE_CHANNEL = int(environ.get("UPDATE_CHANNEL", "-1002461263750"))

# =========================[ SERVER CONFIG ]=========================== #

PORT = environ.get("PORT", "8001")

# =========================[ DATABASE CONFIG ]========================= #

DB_URI = environ.get(
    "DATABASE_URL",
    "mongodb+srv://username:password@cluster0.mongodb.net/?retryWrites=true&w=majority"
)
DB_NAME = environ.get("DATABASE_NAME", "FileHubxBot")

# =========================[ BOT BEHAVIOR SETTINGS ]=================== #

FSUB_LINK_EXPIRY = int(getenv("FSUB_LINK_EXPIRY", "10"))  # 0 = no expiry
BAN_SUPPORT = environ.get("BAN_SUPPORT", "https://t.me/Spideyofficial_777")
TG_BOT_WORKERS = int(environ.get("TG_BOT_WORKERS", "200"))

# =========================[ IMAGES & MEDIA ]========================== #

START_PIC = environ.get("START_PIC", "https://telegra.ph/file/ec17880d61180d3312d6a.jpg")
FORCE_PIC = environ.get("FORCE_PIC", "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg")
VERIFY_IMG = environ.get("VERIFY_IMG", "https://graph.org/file/1669ab9af68eaa62c3ca4.jpg")

# =========================[ SHORTLINK SETTINGS ]====================== #

SHORTLINK_URL = environ.get("SHORTLINK_URL", "shortxlinks.com")
SHORTLINK_API = environ.get("SHORTLINK_API", "your_shortlink_api_here")

VERIFY_EXPIRE = int(environ.get("VERIFY_EXPIRE", "3600"))
TUT_VID = environ.get("TUT_VID", "https://t.me/spideyofficial_777/12")

# =========================[ START & FORCE MESSAGES ]================== #

START_MSG = environ.get(
    "START_MESSAGE",
    "<b>ʜᴇʟʟᴏ {first}\n\n"
    "<blockquote> ɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ "
    "ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.\n"
    "<blockquote>🌿 ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ :  <a href='https://telegram.me/Hacker_x_official_777'>"
    "ʜᴀᴄᴋᴇʀ_x_ᴏꜰꜰɪᴄɪᴀʟ_𝟽𝟽𝟽</a></blockquote></b>"
)

FORCE_MSG = environ.get(
    "FORCE_SUB_MESSAGE",
    "ʜᴇʟʟᴏ {first}\n\n<b>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button "
    "ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b>"
)

CMD_TXT = """<blockquote><b>» ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:</b></blockquote>

<b>›› /dlt_time :</b> sᴇᴛ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /check_dlt_time :</b> ᴄʜᴇᴄᴋ ᴄᴜʀʀᴇɴᴛ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /dbroadcast :</b> ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴏᴄᴜᴍᴇɴᴛ / ᴠɪᴅᴇᴏ
<b>›› /ban :</b> ʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /unban :</b> ᴜɴʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /banlist :</b> ɢᴇᴛ ʟɪsᴛ ᴏꜰ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀs
<b>›› /addchnl :</b> ᴀᴅᴅ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ
<b>›› /delchnl :</b> ʀᴇᴍᴏᴠᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴄʜᴀɴɴᴇʟ
<b>›› /listchnl :</b> ᴠɪᴇᴡ ᴀᴅᴅᴇᴅ ᴄʜᴀɴɴᴇʟs
<b>›› /fsub_mode :</b> ᴛᴏɢɢʟᴇ ꜰᴏʀᴄᴇ sᴜʙ ᴍᴏᴅᴇ
<b>›› /pbroadcast :</b> sᴇɴᴅ ᴘʜᴏᴛᴏ ᴛᴏ ᴀʟʟ ᴜꜱᴇʀs
<b>›› /add_admin :</b> ᴀᴅᴅ ᴀɴ ᴀᴅᴍɪɴ
<b>›› /deladmin :</b> ʀᴇᴍᴏᴠᴇ ᴀɴ ᴀᴅᴍɪɴ
<b>›› /admins :</b> ɢᴇᴛ ʟɪsᴛ ᴏꜰ ᴀᴅᴍɪɴs
<b>›› /addpremium :</b> ᴀᴅᴅ ᴀ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀ
<b>›› /premium_users :</b> ʟɪsᴛ ᴀʟʟ ᴘʀᴇᴍɪᴜᴍ ᴜꜱᴇʀs
<b>›› /remove_premium :</b> ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ꜰʀᴏᴍ ᴀ ᴜꜱᴇʀ
<b>›› /myplan :</b> ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘʀᴇᴍɪᴜᴍ sᴛᴀᴛᴜs
<b>›› /count :</b> ᴄᴏᴜɴᴛ verifications
"""

CUSTOM_CAPTION = environ.get(
    "CUSTOM_CAPTION",
    "<b>• <blockquote>🌿 ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ :  "
    "<a href='https://telegram.me/Hacker_x_official_777'>ʜᴀᴄᴋᴇʀ_x_ᴏꜰꜰɪᴄɪᴀʟ_𝟽𝟽𝟽</a></blockquote></b>"
)

PROTECT_CONTENT = environ.get("PROTECT_CONTENT", "False") == "True"
DISABLE_CHANNEL_BUTTON = environ.get("DISABLE_CHANNEL_BUTTON", "False") == "True"

BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"

# =========================[ PREMIUM SETTINGS ]======================== #

OWNER_TAG = environ.get("OWNER_TAG", "hacker_x_official_777")
UPI_ID = environ.get("UPI_ID", "https://example.com/payment")
QR_PIC = environ.get("QR_PIC", "https://telegra.ph/file/3e83c69804826b3cba066-16cffa90cd682570da.jpg")
SCREENSHOT_URL = environ.get("SCREENSHOT_URL", "https://telegram.me/Hacker_x_official_777")

# Pricing
PRICE1 = environ.get("PRICE1", "25 rs")   # 7 Days
PRICE2 = environ.get("PRICE2", "60 rs")   # 1 Month
PRICE3 = environ.get("PRICE3", "150 rs")  # 3 Months
PRICE4 = environ.get("PRICE4", "280 rs")  # 6 Months
PRICE5 = environ.get("PRICE5", "550 rs")  # 1 Year

# =========================[ EXTRA SETTINGS ]========================== #

NSFW_MODEL = "Falconsai/nsfw_image_detection"
WATERMARK = "© MediaHub"
PREMIUM_TAG = "🌟 PREMIUM"

MIRROR_REGIONS = {
    "US": "https://us-cdn.example.com",
    "EU": "https://eu-cdn.example.com",
    "ASIA": "https://asia-cdn.example.com"
}

# =========================[ LOGGING SETUP ]=========================== #

LOG_FILE_NAME = "filehubxbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(LOG_FILE_NAME, maxBytes=50_000_000, backupCount=10),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
