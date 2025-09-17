import pytz
from datetime import datetime, timedelta
from database.user_repository import UserRepository
from database.filerecord import DBBotContent
from telegram.constants import ParseMode
from config import Config

UTC = pytz.utc

async def create_invite_link(bot_instance):
    expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=5)
    invite_link = await bot_instance.create_chat_invite_link(
        chat_id=Config.CHANNEL_ID, expire_date=expiry, creates_join_request=True
    )
    return invite_link.invite_link

async def create_indo_vvip_invite_link(bot_instance):
    expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=5)
    invite_link = await bot_instance.create_chat_invite_link(
        chat_id=Config.CHANNEL_ID_INDO, expire_date=expiry, creates_join_request=True
    )
    return invite_link.invite_link

async def create_cctv_ngintip_invite_link(bot_instance):
    expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=5)
    invite_link = await bot_instance.create_chat_invite_link(
        chat_id=Config.CHANNEL_ID_CCTV, expire_date=expiry, creates_join_request=True
    )
    return invite_link.invite_link

async def create_ometv_invite_link(bot_instance):
    expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=5)
    invite_link = await bot_instance.create_chat_invite_link(
        chat_id=Config.CHANNEL_ID_OMETV, expire_date=expiry, creates_join_request=True
    )
    return invite_link.invite_link

async def create_jav_invite_link(bot_instance):
    expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=5)
    invite_link = await bot_instance.create_chat_invite_link(
        chat_id=Config.CHANNEL_ID_JAV, expire_date=expiry, creates_join_request=True
    )
    return invite_link.invite_link

async def notify_telegram(bot_instance, user_id, duration, username=""):
    if duration != "lifetime" and duration != "indo_vvip" and duration != "cctv_ngintip" and duration != "ometv" and duration != "jav":
        if type(duration) == int:
            try:
                invite_link = await create_invite_link(bot_instance)
            except:
                print(f"Failed: ( {Config.CHANNEL_ID} ) | ( {user_id} ) | ( {username} )")
            expiry = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(days=duration)
            await UserRepository().add_vip_user(user_id, expiry)
            caption = (
                "<blockquote>"
                "🎉 Pembayaran berhasil!\n\n"
                f"🔥 Klik link ini untuk join grup VIP: <a href='{invite_link}'>Join VIP</a>\n"
                "⚠️ Link akan kadaluarsa dalam 5 menit!"
                "</blockquote>"
            )
            await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)
    elif duration == "lifetime":
        invite_link = "https://t.me/LIVERECORDFILEBOT"
        await DBBotContent().add_user(user_id=user_id, username=username)
        caption = (
            "<blockquote>"
            "🎉 Pembayaran berhasil!\n\n"
            f"🔥 Klik link ini untuk akses: <a href='{invite_link}'>Akses VIP</a>\n"
            "</blockquote>"
        )
        await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)
    elif duration == "indo_vvip":
        try:
            invite_link = await create_indo_vvip_invite_link(bot_instance)
        except:
            print(f"Failed: ( {Config.CHANNEL_ID_INDO} ) | ( {user_id} ) | ( {username} )")
        await UserRepository().add_indo_vip_user(user_id)
        caption = (
            "<blockquote>"
            "🎉 Pembayaran berhasil!\n\n"
            f"🔥 Klik link ini untuk join grup INDO VIP: <a href='{invite_link}'>Join VIP</a>\n"
            "⚠️ Link akan kadaluarsa dalam 5 menit!"
            "</blockquote>"
        )
        await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)
    elif duration == "cctv_ngintip":
        try:
            invite_link = await create_cctv_ngintip_invite_link(bot_instance)
        except:
            print(f"Failed: ( {Config.CHANNEL_ID_CCTV} ) | ( {user_id} ) | ( {username} )")
        await UserRepository().add_cctv_vip_user(user_id)
        caption = (
            "<blockquote>"
            "🎉 Pembayaran berhasil!\n\n"
            f"🔥 Klik link ini untuk join grup CCTV & NGINTIP: <a href='{invite_link}'>Join VIP</a>\n"
            "⚠️ Link akan kadaluarsa dalam 5 menit!"
            "</blockquote>"
        )
        await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)
    elif duration == "ometv":
        try:
            invite_link = await create_ometv_invite_link(bot_instance)
        except:
            print(f"Failed: ( {Config.CHANNEL_ID_OMETV} ) | ( {user_id} ) | ( {username} )")
        await UserRepository().add_ometv_vip_user(user_id)
        caption = (
            "<blockquote>"
            "🎉 Pembayaran berhasil!\n\n"
            f"🔥 Klik link ini untuk join grup OMETV: <a href='{invite_link}'>Join VIP</a>\n"
            "⚠️ Link akan kadaluarsa dalam 5 menit!"
            "</blockquote>"
        )
        await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)
    elif duration == "jav":
        try:
            invite_link = await create_jav_invite_link(bot_instance)
        except:
            print(f"Failed: ( {Config.CHANNEL_ID_JAV} ) | ( {user_id} ) | ( {username} )")
        await UserRepository().add_jav_vip_user(user_id)
        caption = (
            "<blockquote>"
            "🎉 Pembayaran berhasil!\n\n"
            f"🔥 Klik link ini untuk join grup JAV: <a href='{invite_link}'>Join VIP</a>\n"
            "⚠️ Link akan kadaluarsa dalam 5 menit!"
            "</blockquote>"
        )
        await bot_instance.send_message(chat_id=user_id, text=caption, parse_mode=ParseMode.HTML)
    