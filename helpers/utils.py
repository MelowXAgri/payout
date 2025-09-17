import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from helpers.qris import get_qris_payment
from database.qris_repository import QrisRepository

UTC = pytz.utc

qris_repository = QrisRepository()

async def cctv_markup():
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"raze_cctv_qris")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="raze_back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def ometv_markup():
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"raze_ometv_qris")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="raze_back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def jav_markup():
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"raze_jav_qris")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="raze_back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup
