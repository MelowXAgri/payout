import asyncio
import random
import pytz
from datetime import datetime, timedelta
from config import Config
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from database.user_repository import UserRepository
from database.qris_repository import QrisRepository
from database.promo_repository import PromoRepository
from database.filerecord import DBBotContent
from helpers.pricing import pricing, life_time, indo_vvip_price, promo, cctv_price, ometv_price, jav_price
from helpers.okconnect import okconn, get_mutasi
from helpers.qris import get_qris_payment
from helpers.notifications import notify_telegram, create_invite_link, create_indo_vvip_invite_link
from helpers.message import TOS
from helpers.utils import cctv_markup, jav_markup, ometv_markup

UTC = pytz.utc

start_photo_file_id = None
user_repository = UserRepository()
qris_repository = QrisRepository()
db_bot_content = DBBotContent()
promo_repository = PromoRepository()

async def order_markup():
    keyboard = [
        [InlineKeyboardButton("LIVE RECORD : PERBULAN ( V1 )", callback_data="raze_group")],
        [InlineKeyboardButton("LIVE RECORD : PERMANEN ( V2 )", callback_data="raze_permanen")],
        [InlineKeyboardButton("BOKEP VIRAL INDO ( VVIP )", callback_data="raze_indo_vvip")],
        #[InlineKeyboardButton("REKAMAN CCTV & NGINTIP", callback_data="raze_cctv")],
        #[InlineKeyboardButton("REKAMAN OME TV", callback_data="raze_ometv")],
        #[InlineKeyboardButton("BOKEP ASEAN JAV", callback_data="raze_jav")],
        # [InlineKeyboardButton("INFO VIP", url="https://t.me/livexrecord")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def payment_markup(qris_price, trakteer_price, duration):
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"raze_qris_{qris_price}_{duration}")],
        # [InlineKeyboardButton("Trakteer", callback_data=f"raze_trakteer_{trakteer_price}_{duration}")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="raze_back")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def permanent_markup():
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"raze_permanen_qris")],
        # [InlineKeyboardButton("Trakteer", callback_data=f"raze_permanen_trakteer")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="raze_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def indo_vvip_markup():
    keyboard = [
        [InlineKeyboardButton("QRIS", callback_data=f"raze_indo_vvip_qris")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="raze_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

async def promo_markup():
    keyboard = [
        [InlineKeyboardButton(f"{promo['monthly']['label']}", callback_data=f"raze_promo_monthly_qris")],
        [InlineKeyboardButton(f"{promo['permanent']['label']}", callback_data=f"raze_promo_permanent_qris")],
        [InlineKeyboardButton(f"{promo['indo_vvip']['label']}", callback_data=f"raze_promo_indo_vvip_qris")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="raze_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup

# FORCE SUB CHANNEL

async def force_sub_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Memeriksa apakah pengguna telah bergabung dengan channel yang ditentukan."""
    user = update.effective_user

    try:
        # Cek status keanggotaan
        member = await context.bot.get_chat_member(chat_id=Config.FORCE_SUB_CHANNEL_ID, user_id=user.id)

        # Jika bukan member, admin, atau creator, maka anggap belum subscribe
        if member.status not in ["creator", "administrator", "member"]:
            raise Exception("User belum bergabung")

    except Exception as e:
        # Jika gagal mendapatkan status member, anggap belum join

        # Kirim pesan dengan tombol untuk join channel
        keyboard = [
            [InlineKeyboardButton("✅ JOIN CHANNEL", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL_NAME}")],
            [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=user.id,
            text=(
                "🚨 Anda harus bergabung dengan channel kami terlebih dahulu untuk menggunakan bot ini!\n\n"
                "<blockquote>note:\njika sudah klik ' JOIN CHANNEL ' lalu klik ' REFRESH '</blockquote>"
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        return False  # False berarti pengguna **BELUM** join

    return True  # True berarti pengguna **SUDAH** join

async def refresh_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk tombol REFRESH."""
    query = update.callback_query
    await query.answer()  # Berikan respon atas callback query

    user = update.effective_user
    try:
        member = await context.bot.get_chat_member(chat_id=Config.FORCE_SUB_CHANNEL_ID, user_id=user.id)
        if member.status in ["creator", "administrator", "member"]:
            # Jika sudah join, ubah pesan menjadi notifikasi sukses
            await query.edit_message_text(
                text="✅ Terima kasih, Anda telah bergabung dengan channel kami. Silakan klik /start untuk melanjutkan.",
                reply_markup=None,
            )
            return
    except Exception as e:
        pass

    # Jika masih belum join, tampilkan kembali pesan dan keyboard yang sama
    keyboard = [
        [InlineKeyboardButton("✅ JOIN CHANNEL", url=f"https://t.me/{Config.FORCE_SUB_CHANNEL_NAME}")],
        [InlineKeyboardButton("🔄 REFRESH", callback_data="refresh")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        await query.edit_message_text(
            text=(
                "🚨 Anda belum bergabung dengan channel kami. Silakan join terlebih dahulu untuk menggunakan bot ini!\n\n"
                "<blockquote>note:\njika sudah klik ' JOIN CHANNEL ' lalu klik ' REFRESH '</blockquote>"
            ),
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

# END FORCE SUB CHANNEL

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    await user_repository.add_user(user_id)
    is_subscribed = await force_sub_channel(update, context)
    if not is_subscribed:
        return
    caption = (
        f"✨Halo, {first_name} !\n\n"
        "Selamat datang di BOT GROUP VIP\n\n"
        "Contoh grup dan preview media: @livexrecord\n\n"
        "Berikut perintah yang tersedia:\n"
        "/order - Untuk join group VIP\n"
        "/status - Untuk melihat status VIP anda\n"
        "/promo - Untuk melihat promo yang tersedia\n\n"
        "Jangan ragu untuk menggunakan salah satu perintah ini untuk berinteraksi dengan bot🎉\n\n"
        "<blockquote>Note: Global payment with Dollar $ , please contact support @Ibrawashere</blockquote>"
    )
    await update.message.reply_text(text=caption, parse_mode=ParseMode.HTML)
    return

    global start_photo_file_id
    try:
        if start_photo_file_id is None:
            with open("img/start.jpg", "rb") as start_photo:
                msg = await update.message.reply_photo(photo=start_photo, caption=caption, parse_mode=ParseMode.HTML)
                start_photo_file_id = msg.photo[-1].file_id
        else:
            await update.message.reply_photo(photo=start_photo_file_id, caption=caption, parse_mode=ParseMode.HTML)
    except Exception as e:
        print(f"Error in start_handler: {e}")
        await update.message.reply_text(text=caption, parse_mode=ParseMode.HTML)

async def order_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    is_subscribed = await force_sub_channel(update, context)
    if not is_subscribed:
        return
    caption = (
        "<blockquote>"
        f"Halo {update.effective_user.first_name} 👋 Ingin order apa hari ini? ✨\n\n"
        "Bot ini dibuat khusus untuk memudahkan kamu mendapatkan akses ke GROUP RECORD VIP kami yang berisi:\n\n"
        "📱 Ribuan koleksi video berkualitas\n"
        "🔥 Update video terbaru setiap hari\n"
        "⚡ Akses cepat dan mudah\n\n"
        "Silahkan gunakan tombol di bawah untuk mendapatkan akses VIP 🚀"
        "</blockquote>"
    )
    reply_markup = await order_markup()
    await update.message.reply_text(
        text=caption,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def raze_group_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    # vip_user = await user_repository.vip_users.find_one({"user_id": user_id})
    vip_user = False
    if vip_user:
        invite_link = await create_invite_link(context.bot)
        caption = (
            "<blockquote>"
            "🎉 Anda masih memiliki langganan VIP aktif!\n\n"
            f"🔥 Klik link ini untuk join grup VIP: <a href='{invite_link}'>Join VIP</a>\n"
            "⚠️ Link akan kadaluarsa dalam 5 menit!"
            "</blockquote>"
        )
        try:
            await update.callback_query.delete_message()
            await update.callback_query.message.reply_text(
                text=caption,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        return
    await update.callback_query.answer()
    caption = (
        "<blockquote>"
        "KONTEN VIDEO V1: GRUP\n"
        "- TIDAK PERMANEN\n"
        "- UPDATE SETIAP HARI"
        "</blockquote>"
    )
    keyboard = [
        [InlineKeyboardButton(i['label'], callback_data=f"raze_subscribe_{i['price']['qris']}_{i['price']['trakteer']}_{i['duration']}")] for i in pricing
    ]
    keyboard.append([InlineKeyboardButton("🔙 Kembali", callback_data="raze_back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def raze_subscribe_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    await update.callback_query.answer()
    data = update.callback_query.data.replace("raze_subscribe_", "").split("_")
    qris_price = int(data[0])
    trakteer_price = int(data[1])
    duration = int(data[2])
    caption = (
        "<blockquote>"
        "🛒Order\n\n"
        f"💰 IDR: {qris_price}\n\n"
        "Pilih metode pembayaran:"
        "</blockquote>"
    )
    reply_markup = await payment_markup(qris_price, trakteer_price, duration)
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def raze_permanen_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    # permanen_user = await db_bot_content.users.find_one({"user_id": user_id})
    permanen_user = False
    if permanen_user:
        invite_link = "https://t.me/LIVERECORDFILEBOT"
        caption = (
            "<blockquote>"
            "🎉 Anda sudah berlangganan!\n\n"
            f"🔥 Klik link ini untuk akses: <a href='{invite_link}'>Akses VIP</a>\n"
            "</blockquote>"
        )
        try:
            await update.callback_query.delete_message()
            await update.callback_query.message.reply_text(
                text=caption,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        return
    await update.callback_query.answer()
    caption = (
        "<blockquote>"
        "KONTEN VIDEO V2: BOT\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP MINGGU\n\n"
        f"💰 IDR: {life_time['qris']}"
        "</blockquote>"
    )
    reply_markup = await permanent_markup()
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def raze_permanen_qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = life_time['qris']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "lifetime"
        }
    )

async def raze_permanen_trakteer_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    first_name = update.callback_query.from_user.first_name
    price = life_time['trakteer']
    payment_url = f"https://trakteer.id/{Config.TRAKTEER_USERNAME}/tip?quantity={price}&step=2&display_name={first_name}&supporter_message=order_vip_{user_id}_lifetime"
    keyboard = [[InlineKeyboardButton("💸 Bayar Sekarang", web_app=WebAppInfo(url=payment_url))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.edit_message_text(
            "<blockquote>"
            "🛒Order\n\nKlik tombol dibawah untuk membayar.\n\n"
            f"⚠️<b>Jangan ubah text pada kolom pesan untuk memastikan pembayaran anda berhasil.</b>"
            "</blockquote>",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def raze_indo_vvip_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    # indo_vvip_member = await user_repository.indo_vvip_users.find_one({"user_id": user_id})
    indo_vvip_member = False
    if indo_vvip_member:
        invite_link = await create_indo_vvip_invite_link(context.bot)
        caption = (
            "<blockquote>"
            "🎉 Anda sudah berlangganan!\n\n"
            f"🔥 Klik link ini untuk join grup INDO VIP: <a href='{invite_link}'>Join VIP</a>\n"
            "⚠️ Link akan kadaluarsa dalam 5 menit!"
            "</blockquote>"
        )
        try:
            await update.callback_query.delete_message()
            await update.callback_query.message.reply_text(
                text=caption,
                parse_mode=ParseMode.HTML
            )
        except:
            pass
        return
    caption = (
        "<blockquote>"
        "BOKEP VIRAL INDO VVIP: GRUP\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP HARI\n\n"
        f"💰 IDR: {indo_vvip_price['qris']}"
        "</blockquote>"
    )
    reply_markup = await indo_vvip_markup()
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def raze_indo_vvip_qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = indo_vvip_price['qris']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "indo_vvip"
        }
    )

# CCTV & NGINTIP

async def raze_cctv_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    caption = (
        "<blockquote>"
        "REKAMAN CCTV & NGINTIP\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP HARI\n\n"
        f"💰 IDR: {cctv_price['qris']}"
        "</blockquote>"
    )
    reply_markup = await cctv_markup()
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def raze_cctv_qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = cctv_price['qris']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "cctv_ngintip"
        }
    )

# END CCTV & NGINTIP

# OME TV

async def raze_ometv_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    caption = (
        "<blockquote>"
        "REKAMAN OME TV\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP HARI\n\n"
        f"💰 IDR: {ometv_price['qris']}"
        "</blockquote>"
    )
    reply_markup = await ometv_markup()
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def raze_ometv_qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = ometv_price['qris']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "ometv"
        }
    )

# END OME TV

# ASEAN JAV

async def raze_jav_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    caption = (
        "<blockquote>"
        "BOKEP ASEAN JAV\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP HARI\n\n"
        f"💰 IDR: {jav_price['qris']}"
        "</blockquote>"
    )
    reply_markup = await jav_markup()
    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def raze_jav_qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = jav_price['qris']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "jav"
        }
    )

# END ASEAN JAV

# PROMO

async def raze_promo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    is_subscribed = await force_sub_channel(update, context)
    if not is_subscribed:
        return

    if user_id in Config.ADMIN_ID:
        if len(context.args) != 1:
            pass
        else:
            promo_status = False
            if context.args[0] == "on":
                promo_status = True
            elif context.args[0] == "off":
                promo_status = False
            else:
                await update.message.reply_text("Usage:\n\n/promo [on/off]")
                return
            
            # Update status promo di database (menggunakan upsert jika dokumen tidak ada)
            await promo_repository.promo.update_one(
                {"_id": "promo_status"},
                {"$set": {"status": promo_status}},
                upsert=True
            )
            await update.message.reply_text(f"Status promo telah diubah menjadi: {context.args[0]}")
            return

    promo_status = await promo_repository.promo.find_one({"_id": "promo_status"})
    if not promo_status or not promo_status.get("status", False):
        await update.message.reply_text("⚠️ Tidak ada promo yang berlangsung.")
        return

    reply_markup = await promo_markup()
    await update.message.reply_text(
        "🎉 PILIH PAKET PROMO\n\n"
        "<blockquote>"
        f"{promo['monthly']['label']}\n"
        "- TIDAK PERMANEN\n"
        "- UPDATE SETIAP HARI\n"
        f"- IDR : {promo['monthly']['price']['qris']}"
        "</blockquote>\n\n"
        "<blockquote>"
        f"{promo['permanent']['label']}\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP HARI\n"
        f"- IDR : {promo['permanent']['price']['qris']}"
        "</blockquote>\n\n"
        "<blockquote>"
        f"{promo['indo_vvip']['label']}\n"
        "- PERMANEN\n"
        "- UPDATE SETIAP HARI\n"
        f"- IDR : {promo['indo_vvip']['price']['qris']}"
        "</blockquote>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

async def raze_promo_monthly_qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = promo['monthly']['price']['qris']
    duration = 30
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "monthly"
        }
    )

async def raze_promo_permanent_qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = promo['permanent']['price']['qris']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "lifetime"
        }
    )

async def raze_promo_indo_vvip_qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = promo['indo_vvip']['price']['qris']
    duration = 0
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "indo_vvip"
        }
    )

# END PROMO

async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    is_subscribed = await force_sub_channel(update, context)
    if not is_subscribed:
        return
    vip_user = await user_repository.vip_users.find_one({"user_id": user_id})
    
    if vip_user:
        expiry = vip_user["expiry"]
        expiry_dt = expiry.astimezone(Config.TIMEZONE)
        remaining_time = expiry_dt - datetime.now(UTC).astimezone(Config.TIMEZONE)
        days = remaining_time.days
        hours, remainder = divmod(remaining_time.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        expiry_str = expiry_dt.strftime("%d %B %Y, %H:%M %Z")
        await update.message.reply_text(
            "<blockquote>"
            f"🎉 Anda telah terdaftar sebagai VIP!\n\n"
            f"📅 <b>Tanggal Kadaluarsa:</b> {expiry_str}\n"
            f"⏱️ <b>Sisa Waktu:</b> {days} hari, {hours} jam, {minutes} menit"
            "</blockquote>",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text("❌ Anda belum terdaftar sebagai VIP.")

async def tos_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    channel = await context.bot.get_chat(Config.CHANNEL_ID)
    channel_name = channel.title
    await update.message.reply_text(
        text=TOS.format(FORMAT_CHANNEL_NAME=channel_name),
        parse_mode=ParseMode.HTML
    )

async def back_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    caption = (
        "<blockquote>"
        f"Halo {update.effective_user.first_name} 👋 Ingin order apa hari ini? ✨\n\n"
        "Bot ini dibuat khusus untuk memudahkan kamu mendapatkan akses ke GROUP RECORD VIP kami yang berisi:\n\n"
        "📱 Ribuan koleksi video berkualitas\n"
        "🔥 Update video terbaru setiap hari\n"
        "⚡ Akses cepat dan mudah\n\n"
        "Silahkan gunakan tombol di bawah untuk mendapatkan akses VIP 🚀"
        "</blockquote>"
    )

    reply_markup = await order_markup()

    try:
        await update.callback_query.edit_message_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def qris_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username
    if await qris_repository.qris.find_one({"user_id": user_id}):
        try:
            await update.callback_query.edit_message_text(
                text="⚠️ Anda masih memiliki order yang sedang berlangsung.\n\nSilahkan batalkan order dengan perintah /cancel terlebih dahulu sebelum melakukan order baru."
            )
        except:
            pass
        return
    price = int(update.callback_query.data.split("_")[2])
    duration = int(update.callback_query.data.split("_")[3])
    while True:
        unique_code = random.randint(100, 999)
        total_price = price + unique_code
        existing_price = await qris_repository.qris.find_one({"price": total_price})
        if not existing_price:
            break
    qris_url, qris_code = get_qris_payment(total_price)
    qris_expired = datetime.now(UTC).astimezone(Config.TIMEZONE) + timedelta(minutes=10)
    try:
        await update.callback_query.delete_message()
    except:
        pass
    caption = (
        "<blockquote>"
        "🔃 Scan QRIS ini untuk pembayaran.\n\n"
        f"💰 <b>Jumlah:</b> Rp {total_price}\n"
        f"⏳ <b>Expired:</b> {qris_expired.strftime('%H:%M:%S WIB')}\n\n"
        "⏰ QRIS akan kadaluarsa dalam 10 menit."
        "</blockquote>"
    )
    msg = await update.callback_query.message.reply_photo(
        qris_url,
        caption=caption,
        parse_mode=ParseMode.HTML
    )
    await qris_repository.add_qris(user_id, msg.id, duration, qris_code, qris_url, qris_expired.astimezone(UTC))
    
    context.job_queue.run_repeating(
        check_qris_payment, interval=10, first=5, user_id=user_id,
        data={
            "total_price": total_price, 
            "user_id": user_id, 
            "username": username, 
            "msg_id": msg.id, 
            "subscription": "monthly"
        }
    )

async def check_qris_payment(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.data['user_id']
    username = job.data['username']
    total_price = job.data['total_price']
    msg_id = job.data['msg_id']
    subscription = job.data['subscription']
    order = await qris_repository.qris.find_one({"user_id": user_id})
    if not order:
        job.schedule_removal()
        return
    
    expiry = order['expiry'].replace(tzinfo=pytz.UTC).astimezone(Config.TIMEZONE)
    msg_id = order['msg_id']
    
    histories = get_mutasi("windashop", "1130455:2KE4VHY31vaBi7mDIkf5qObWUMLu6gNl")
    if histories["status"]:
        for history in histories['data']:
            if history['type'] == 'CR' and int(history['amount']) == total_price:
                await qris_repository.remove_qris(user_id)
                try:
                    await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
                except:
                    pass
                if subscription == "monthly":
                    await notify_telegram(context.bot, user_id, order['duration'])
                elif subscription == "lifetime":
                    await notify_telegram(context.bot, user_id, "lifetime", username)
                elif subscription == "indo_vvip":
                    await notify_telegram(context.bot, user_id, "indo_vvip", username)
                elif subscription == "cctv_ngintip":
                    await notify_telegram(context.bot, user_id, "cctv_ngintip", username)
                elif subscription == "ometv":
                    await notify_telegram(context.bot, user_id, "ometv", username)
                elif subscription == "jav":
                    await notify_telegram(context.bot, user_id, "jav", username)
                job.schedule_removal()
                return
    
    if datetime.now(UTC).astimezone(Config.TIMEZONE) >= expiry.astimezone(Config.TIMEZONE):
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=msg_id)
        except:
            pass
        await context.bot.send_message(chat_id=user_id, text="⚠️ Pembayaran gagal. QRIS telah kadaluarsa.")
        await qris_repository.qris.delete_one({"user_id": user_id})
        job.schedule_removal()

async def qris_cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await user_repository.add_user(user_id)
    user_qris = await qris_repository.qris.find_one({"user_id": user_id})
    if user_qris:
        if 'msg_id' in user_qris and user_qris['msg_id'] is not None:
            try:
                await context.bot.delete_message(chat_id=user_id, message_id=user_qris['msg_id'])
            except:
                pass
        await qris_repository.remove_qris(user_id)
        await update.message.reply_text("✅ Order berhasil dibatalkan.")
    else:
        await update.message.reply_text("❌ Anda tidak memiliki order yang sedang berlangsung.")

async def trakteer_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    user_id = update.callback_query.from_user.id
    first_name = update.callback_query.from_user.first_name
    price = int(update.callback_query.data.split("_")[2])
    payment_url = f"https://trakteer.id/{Config.TRAKTEER_USERNAME}/tip?quantity={price}&step=2&display_name={first_name}&supporter_message=order_vip_{user_id}"
    keyboard = [[InlineKeyboardButton("Bayar Sekarang", web_app=WebAppInfo(url=payment_url))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await update.callback_query.edit_message_text(
            "<blockquote>"
            "🛒Order\n\nKlik tombol dibawah untuk membayar.\n\n"
            f"⚠️<b>Jangan ubah text pada kolom pesan untuk memastikan pembayaran anda berhasil.</b>"
            "</blockquote>",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    except:
        pass

async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    caption = (
        "🔐Perintah untuk Admin:\n\n"
        "/broadcast - Broadcast ke pengguna BOT\n"
        "/vipbroadcast - Broadcast ke member VIP\n"
        "/broadcastpin - Broadcast dengan pin\n"
        "/vipbroadcastpin - Broadcast dengan pin ke member VIP\n"
        "/cekuser - Cek user VIP\n"
        "/add - Tambah manual user VIP\n"
        "/addindo - Tambah manual user INDO VIP\n"
        "/addcctv - Tambah manual user CCTV VIP\n"
        "/addometv - Tambah manual user OMETV VIP\n"
        "/addjav - Tambah manual user JAV VIP\n"
        "/promo [on|off] - Promo VIP"
    )
    await update.message.reply_text(text=caption)

async def broadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        sent = 0
        async for user in user_repository.users.find():
            try:
                await context.bot.copy_message(
                    chat_id=int(user['user_id']),
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
                sent += 1
                await asyncio.sleep(0.5)
            except:
                pass
        total_user = await user_repository.users.count_documents({})
        await update.message.reply_text(f"✅ Berhasil mengirim pesan ke {sent}/{total_user} pengguna.")
    else:
        await update.message.reply_text("Reply ke pesan yang ingin di-broadcast.")

async def vipbroadcast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        sent = 0
        async for user in user_repository.vip_users.find():
            try:
                await context.bot.copy_message(
                    chat_id=int(user['user_id']),
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
                sent += 1
                await asyncio.sleep(0.5)
            except:
                pass
        total_user = await user_repository.vip_users.count_documents({})
        await update.message.reply_text(f"✅ Berhasil mengirim pesan ke {sent}/{total_user} member VIP.")
    else:
        await update.message.reply_text("Reply ke pesan yang ingin di-broadcast.")

async def broadcast_and_pin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        sent = 0
        async for user in user_repository.users.find():
            try:
                msg_to_pin = await context.bot.copy_message(
                    chat_id=int(user['user_id']),
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
                await context.bot.pin_chat_message(
                    chat_id=int(user['user_id']),
                    message_id=msg_to_pin.message_id,
                    disable_notification=False
                )
                sent += 1
                await asyncio.sleep(0.5)
            except:
                pass
        total_user = await user_repository.users.count_documents({})
        await update.message.reply_text(f"✅ Berhasil mengirim pesan dan menyematkan ke {sent}/{total_user} pengguna.")
    else:
        await update.message.reply_text("Reply ke pesan yang ingin di-broadcast.")

async def vipbroadcast_and_pin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if update.message.reply_to_message:
        msg = update.message.reply_to_message
        sent = 0
        async for user in user_repository.vip_users.find():
            try:
                msg_to_pin = await context.bot.copy_message(
                    chat_id=int(user['user_id']),
                    from_chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    caption=msg.caption,
                    caption_entities=msg.caption_entities,
                    reply_markup=msg.reply_markup
                )
                await context.bot.pin_chat_message(
                    chat_id=int(user['user_id']),
                    message_id=msg_to_pin.message_id,
                    disable_notification=False
                )
                sent += 1
                await asyncio.sleep(0.5)
            except:
                pass
        total_user = await user_repository.vip_users.count_documents({})
        await update.message.reply_text(f"✅ Berhasil mengirim pesan dan menyematkan ke {sent}/{total_user} member VIP.")
    else:
        await update.message.reply_text("Reply ke pesan yang ingin di-broadcast.")

async def cekuser_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    now = datetime.now(UTC).astimezone(Config.TIMEZONE)
    time_ranges = {
        "< 1 minggu": (now, now + timedelta(weeks=1)),
        "1-2 minggu": (now + timedelta(weeks=1), now + timedelta(weeks=2)),
        "2-3 minggu": (now + timedelta(weeks=2), now + timedelta(weeks=3)),
        "3-4 minggu": (now + timedelta(weeks=3), now + timedelta(weeks=4)),
        "1-6 bulan": (now + timedelta(weeks=4), now + timedelta(weeks=24)),
        "6-12 bulan": (now + timedelta(weeks=24), now + timedelta(weeks=52)),
    }
    response = "Jumlah pengguna berdasarkan masa VIP:\n\n"
    for label, (start, end) in time_ranges.items():
        count = await user_repository.vip_users.count_documents({"expiry": {"$gte": start, "$lt": end}})
        response += f"{label}: {count} pengguna\n"
    vip_count = await user_repository.vip_users.count_documents({})
    indo_vip_count = await user_repository.indo_vvip_users.count_documents({})
    cctv_vip_count = await user_repository.cctv_ngintip_users.count_documents({})
    ometv_vip_count = await user_repository.ometv_users.count_documents({})
    jav_vip_count = await user_repository.asean_jav_users.count_documents({})
    user_count = await user_repository.users.count_documents({})
    filerecord_count = await db_bot_content.users.count_documents({})
    response += f"\n\nTotal pengguna VIP: {vip_count}\n\n"
    response += f"Total pengguna INDO VIP: {indo_vip_count}\n\n"
    response += f"Total pengguna CCTV VIP: {cctv_vip_count}\n\n"
    response += f"Total pengguna OMETV VIP: {ometv_vip_count}\n\n"
    response += f"Total pengguna ASEAN JAV VIP: {jav_vip_count}\n\n"
    response += f"Total pengguna bot FileRecord : {filerecord_count}\n\n"
    response += f"Total pengguna bot: {user_count}"
    await update.message.reply_text(response)

async def add_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if len(context.args) != 2:
        await update.message.reply_text("Usage: /add user_id jumlah_bulan")
        return
    try:
        user_id = int(context.args[0])
        months = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Format salah. Pastikan user_id dan jumlah bulan adalah angka.")
        return
    user = await user_repository.vip_users.find_one({"user_id": user_id})
    now = datetime.now(UTC).astimezone(Config.TIMEZONE)
    if user:
        expiry = user["expiry"].astimezone(Config.TIMEZONE)
        new_expiry = expiry + timedelta(days=30 * months)
    else:
        new_expiry = now + timedelta(days=30 * months)
    await user_repository.vip_users.update_one(
        {"user_id": user_id},
        {"$set": {"expiry": new_expiry}},
        upsert=True
    )
    expiry_str = new_expiry.strftime("%d %B %Y, %H:%M %Z")
    await update.message.reply_text(f"✅ User {user_id} telah ditambahkan/ diperpanjang VIP hingga {expiry_str}.")

async def add_indo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addindo user_id")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah. Pastikan user_id adalah angka.")
        return
    user = await user_repository.indo_vvip_users.find_one({"user_id": user_id})
    if user:
        await update.message.reply_text("⚠ User sudah berlangganan!")
        return
    await user_repository.indo_vvip_users.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    await update.message.reply_text(f"✅ User {user_id} telah ditambahkan ke INDO VIP.")

async def add_cctv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addcctv user_id")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah. Pastikan user_id adalah angka.")
        return
    user = await user_repository.cctv_ngintip_users.find_one({"user_id": user_id})
    if user:
        await update.message.reply_text("⚠ User sudah berlangganan!")
        return
    await user_repository.cctv_ngintip_users.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    await update.message.reply_text(f"✅ User {user_id} telah ditambahkan ke CCTV & NGINTIP VIP.")

async def add_ometv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addometv user_id")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah. Pastikan user_id adalah angka.")
        return
    user = await user_repository.ometv_users.find_one({"user_id": user_id})
    if user:
        await update.message.reply_text("⚠ User sudah berlangganan!")
        return
    await user_repository.ometv_users.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    await update.message.reply_text(f"✅ User {user_id} telah ditambahkan ke OMETV VIP.")

async def add_jav_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in Config.ADMIN_ID:
        return
    await user_repository.add_user(user_id)
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addjav user_id")
        return
    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Format salah. Pastikan user_id adalah angka.")
        return
    user = await user_repository.asean_jav_users.find_one({"user_id": user_id})
    if user:
        await update.message.reply_text("⚠ User sudah berlangganan!")
        return
    await user_repository.asean_jav_users.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
    await update.message.reply_text(f"✅ User {user_id} telah ditambahkan ke ASEAN JAV VIP.")

async def handle_chat_join_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    req = update.chat_join_request
    user_id = req.from_user.id
    await user_repository.add_user(user_id)
    if req.chat.id == Config.CHANNEL_ID:
        member = await user_repository.vip_users.find_one({"user_id": user_id})
        if member:
            await context.bot.approve_chat_join_request(chat_id=Config.CHANNEL_ID, user_id=user_id)
            await context.bot.send_message(user_id, "✅ Permintaan join Anda telah disetujui!")
        else:
            await context.bot.decline_chat_join_request(chat_id=Config.CHANNEL_ID, user_id=user_id)
            await context.bot.send_message(user_id, "❌ Anda belum berlangganan VIP.")
    elif req.chat.id == Config.CHANNEL_ID_INDO:
        member = await user_repository.indo_vvip_users.find_one({"user_id": user_id})
        if member:
            await context.bot.approve_chat_join_request(chat_id=Config.CHANNEL_ID_INDO, user_id=user_id)
            await context.bot.send_message(user_id, "✅ Permintaan join Anda telah disetujui!")
        else:
            await context.bot.decline_chat_join_request(chat_id=Config.CHANNEL_ID_INDO, user_id=user_id)
            await context.bot.send_message(user_id, "❌ Anda belum berlangganan INDO VIP.")
    elif req.chat.id == Config.CHANNEL_ID_CCTV:
        member = await user_repository.cctv_ngintip_users.find_one({"user_id": user_id})
        if member:
            await context.bot.approve_chat_join_request(chat_id=Config.CHANNEL_ID_CCTV, user_id=user_id)
            await context.bot.send_message(user_id, "✅ Permintaan join Anda telah disetujui!")
        else:
            await context.bot.decline_chat_join_request(chat_id=Config.CHANNEL_ID_CCTV, user_id=user_id)
            await context.bot.send_message(user_id, "❌ Anda belum berlangganan CCTV & NGINTIP VIP.")
    elif req.chat.id == Config.CHANNEL_ID_OMETV:
        member = await user_repository.ometv_users.find_one({"user_id": user_id})
        if member:
            await context.bot.approve_chat_join_request(chat_id=Config.CHANNEL_ID_OMETV, user_id=user_id)
            await context.bot.send_message(user_id, "✅ Permintaan join Anda telah disetujui!")
        else:
            await context.bot.decline_chat_join_request(chat_id=Config.CHANNEL_ID_OMETV, user_id=user_id)
            await context.bot.send_message(user_id, "❌ Anda belum berlangganan OMETV VIP.")
    elif req.chat.id == Config.CHANNEL_ID_JAV:
        member = await user_repository.asean_jav_users.find_one({"user_id": user_id})
        if member:
            await context.bot.approve_chat_join_request(chat_id=Config.CHANNEL_ID_JAV, user_id=user_id)
            await context.bot.send_message(user_id, "✅ Permintaan join Anda telah disetujui!")
        else:
            await context.bot.decline_chat_join_request(chat_id=Config.CHANNEL_ID_JAV, user_id=user_id)
            await context.bot.send_message(user_id, "❌ Anda belum berlangganan ASEAN JAV VIP.")
    