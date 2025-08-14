import os
from os import environ, getenv
import logging
from logging.handlers import RotatingFileHandler

# rohit_1888 on Tg
# --------------------------------------------
# Bot token @Botfather
TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "")
APP_ID = int(os.environ.get("APP_ID", "28519661"))  # Your API ID from my.telegram.org
API_HASH = os.environ.get("API_HASH", "d47c74c8a596fd3048955b322304109d")  # Your API Hash from my.telegram.org
# --------------------------------------------
CHANNEL_ID = int(os.environ.get("CHANNEL_ID", "-1002423451263"))
VERIFIED_LOG = int(environ.get('VERIFIED_LOG', '-1002423451263'))  # Your db channel Id
OWNER = os.environ.get("OWNER", "hacker_x_official_777")  # Owner username without @
OWNER_ID = int(os.environ.get("OWNER_ID", "7965267063"))  # Owner id
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1002294764885'))
CHANNELS = int(os.environ.get("CHANNEL", "-1002423451263"))
UPDATE_CHANNEL = int(os.environ.get("UPDATE_CHANNEL", "-1002461263750"))
# --------------------------------------------
PORT = os.environ.get("PORT", "8001")
# --------------------------------------------
DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://vajoko2131:x3qqdqblhmi0s2fX@cluster0.xrpgiv7.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DATABASE_NAME", "FileHubxBot")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'My_Tg_files')
# --------------------------------------------
FSUB_LINK_EXPIRY = int(os.getenv("FSUB_LINK_EXPIRY", "10"))  # 0 means no expiry
BAN_SUPPORT = os.environ.get("BAN_SUPPORT", "https://t.me/Spideyofficial_777")
TG_BOT_WORKERS = int(os.environ.get("TG_BOT_WORKERS", "200"))
# --------------------------------------------
START_PIC = os.environ.get("START_PIC", "https://telegra.ph/file/ec17880d61180d3312d6a.jpg")
FORCE_PIC = os.environ.get("FORCE_PIC", "https://telegra.ph/file/e292b12890b8b4b9dcbd1.jpg")
VERIFY_IMG = environ.get("VERIFY_IMG", "https://graph.org/file/1669ab9af68eaa62c3ca4.jpg")
# --------------------------------------------
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "shortxlinks.com")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "09c3f9bc3a8b121b1e6b82a954e59da523dd188e")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 3600))  # Add time in seconds
TUT_VID = os.environ.get("TUT_VID", "https://t.me/spideyofficial_777/12")
# --------------------------------------------
START_MSG = os.environ.get("START_MESSAGE", "<b>ʜᴇʟʟᴏ {mention}\n\n<blockquote> ɪ ᴀᴍ ғɪʟᴇ sᴛᴏʀᴇ ʙᴏᴛ, ɪ ᴄᴀɴ sᴛᴏʀᴇ ᴘʀɪᴠᴀᴛᴇ ғɪʟᴇs ɪɴ sᴘᴇᴄɪғɪᴇᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴏᴛʜᴇʀ ᴜsᴇʀs ᴄᴀɴ ᴀᴄᴄᴇss ɪᴛ ғʀᴏᴍ sᴘᴇᴄɪᴀʟ ʟɪɴᴋ.</blockquote></b>")
FORCE_MSG = os.environ.get("FORCE_SUB_MESSAGE", "ʜᴇʟʟᴏ {mention}\n\n<b><blockquote>ᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴀɴᴅ ᴛʜᴇɴ ᴄʟɪᴄᴋ ᴏɴ ʀᴇʟᴏᴀᴅ button ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ ꜰɪʟᴇ.</b></blockquote>")


CMD_TXT = """<blockquote><b>» ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:</b></blockquote>

<b>›› /dlt_time :</b> sᴇᴛ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /check_dlt_time :</b> ᴄʜᴇᴄᴋ ᴄᴜʀʀᴇɴᴛ ᴅᴇʟᴇᴛᴇ ᴛɪᴍᴇ
<b>›› /dbroadcast :</b> ʙʀᴏᴀᴅᴄᴀsᴛ ᴅᴏᴄᴜᴍᴇɴᴛ / ᴠɪᴅᴇᴏ
<b>›› /ban :</b> ʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /unban :</b> ᴜɴʙᴀɴ ᴀ ᴜꜱᴇʀ
<b>›› /banlist :</b> ɢᴇᴛ ʟɪsᴛ ᴏꜰ ʙᴀɴɴᴇᴅ ᴜsᴇʀs
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

CUSTOM_CAPTION = os.environ.get(
    "CUSTOM_CAPTION",
    "<b>• <blockquote>🌿 ᴍᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ :  <a href='https://telegram.me/Hacker_x_official_777'>ʜᴀᴄᴋᴇʀ_x_ᴏꜰꜰɪᴄɪᴀʟ_𝟽𝟽𝟽</a></blockquote></b>"
)
PROTECT_CONTENT = os.environ.get('PROTECT_CONTENT', "False") == "True"
DISABLE_CHANNEL_BUTTON = os.environ.get("DISABLE_CHANNEL_BUTTON", None) == 'True'
# --------------------------------------------
BOT_STATS_TEXT = "<b>BOT UPTIME</b>\n{uptime}"
USER_REPLY_TEXT = "ʙᴀᴋᴋᴀ ! ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴍʏ ꜱᴇɴᴘᴀɪ!!"

# ==========================(BUY PREMIUM)====================#
OWNER_TAG = os.environ.get("OWNER_TAG", "hacker_x_official_777")
UPI_ID = os.environ.get("UPI_ID", "https://operational-dania-gam-inghatyar777-3a4bd9c8.koyeb.app/")
QR_PIC = os.environ.get("QR_PIC", "https://telegra.ph/file/3e83c69804826b3cba066-16cffa90cd682570da.jpg")
SCREENSHOT_URL = os.environ.get("SCREENSHOT_URL", "https://telegram.me/Hacker_x_official_777")

PRICE1 = os.environ.get("PRICE1", "25 rs")
PRICE2 = os.environ.get("PRICE2", "60 rs")
PRICE3 = os.environ.get("PRICE3", "150 rs")
PRICE4 = os.environ.get("PRICE4", "280 rs")
PRICE5 = os.environ.get("PRICE5", "550 rs")

# ===================(END)========================#
NSFW_MODEL = "Falconsai/nsfw_image_detection"
WATERMARK = "© MediaHub"
PREMIUM_TAG = "🌟 PREMIUM"

MIRROR_REGIONS = {
    "US": "https://us-cdn.example.com",
    "EU": "https://eu-cdn.example.com",
    "ASIA": "https://asia-cdn.example.com"
}

class temp(object):
    ME = None
    U_NAME = None
    B_NAME = None
    B_LINK = None
    
LOG_FILE_NAME = "filehubxbot.txt"

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)


def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
