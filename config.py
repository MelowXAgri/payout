import os
import pytz

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "5202821562:AAGTnvlkVdW7fMmd9PiwXYEU3O6Mmrcqjdo")
    CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-1002633596412"))
    CHANNEL_ID_INDO = int(os.getenv("CHANNEL_ID_INDO", "-1002472785107"))
    CHANNEL_ID_CCTV = int(os.getenv("CHANNEL_ID_CCTV", "-1002472785107"))
    CHANNEL_ID_OMETV = int(os.getenv("CHANNEL_ID_OMETV", "-1002472785107"))
    CHANNEL_ID_JAV = int(os.getenv("CHANNEL_ID_JAV", "-1002472785107"))
    ADMIN_ID = [int(id) for id in os.getenv("ADMIN_ID", "1516420756,7481738979,7830551403").split(",")]

    FORCE_SUB_CHANNEL_ID = int(os.getenv("FORCE_SUB_CHANNEL_ID", "-1002633596412"))
    FORCE_SUB_CHANNEL_NAME = os.getenv("FORCE_SUB_CHANNEL_NAME", "Destinationoflife")

    TUTORIAL_LINK = os.getenv("TUTORIAL_LINK", "https://t.me/riyowasheree/12")

    TRAKTEER_USERNAME = os.getenv("TRAKTEER_USERNAME", "buatbeliseblakjablay")
    TRAKTEER_WEBHOOK_TOKEN = os.getenv("TRAKTEER_WEBHOOK_TOKEN", "trhook-Xvug28pz09TXiOZDsjZroFxK")

    OK_CONNECT_MEMBER_ID = os.getenv("OK_CONNECT_MEMBER_ID", "OK1130455")
    OK_CONNECT_SIGNATURE = os.getenv("OK_CONNECT_SIGNATURE", "372603317404212791130455OKCT99D74F95FAB43728DB3B533F8ED8EC5D")

    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://raze98fhx:xgM9MDTC4eue333Y@cluster0.nu84e.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

    TIMEZONE = pytz.timezone("Asia/Jakarta")