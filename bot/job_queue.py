import asyncio
import pytz
import traceback
from bot.bot import TelegramBot
from config import Config
from datetime import datetime
from database.user_repository import UserRepository
from telegram.ext import ContextTypes, JobQueue
from telegram.constants import ParseMode
from helpers.message import template

UTC = pytz.utc
TIMEZONE = Config.TIMEZONE
app = TelegramBot().app
vip_users = UserRepository().vip_users

async def remove_expired_vip_job(context: ContextTypes.DEFAULT_TYPE):
    async for member in vip_users.find():
        if datetime.now(UTC).astimezone(TIMEZONE) > member["expiry"].astimezone(TIMEZONE):
            user_id = member["user_id"]
            try:
                await app.bot.ban_chat_member(Config.CHANNEL_ID, user_id)
                await app.bot.unban_chat_member(Config.CHANNEL_ID, user_id)
                await vip_users.delete_one({"user_id": user_id})
                await asyncio.sleep(5)
            except Exception as e:
                print(traceback.format_exc())
            try:
                await app.bot.send_message(
                    chat_id=user_id,
                    text=template["expired_vip"],
                    parse_mode=ParseMode.HTML
                )
            except:
                pass

def setup_jobs(job_queue: JobQueue):
    job_queue.run_repeating(remove_expired_vip_job, interval=3600, first=10)