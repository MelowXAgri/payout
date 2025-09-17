from telegram.ext import Application, CallbackQueryHandler, ChatJoinRequestHandler, CommandHandler, filters
from config import Config
from bot.handlers import (
    add_cctv_handler,
    add_indo_handler,
    add_jav_handler,
    add_ometv_handler,
    broadcast_and_pin_handler,
    raze_cctv_callback_handler,
    raze_cctv_qris_callback_handler,
    raze_group_callback_handler,
    raze_indo_vvip_callback_handler,
    raze_indo_vvip_qris_callback_handler,
    raze_jav_callback_handler,
    raze_jav_qris_callback_handler,
    raze_ometv_callback_handler,
    raze_ometv_qris_callback_handler,
    raze_permanen_callback_handler,
    raze_permanen_qris_callback_handler,
    raze_permanen_trakteer_callback_handler,
    raze_promo_handler,
    raze_promo_indo_vvip_qris_callback_handler,
    raze_promo_monthly_qris_callback_handler,
    raze_promo_permanent_qris_callback_handler,
    raze_subscribe_callback_handler,
    refresh_callback,
    start_handler,
    order_handler,
    status_handler,
    tos_handler,
    back_callback_handler,
    qris_cancel_handler,
    qris_callback_handler,
    trakteer_callback_handler,
    admin_handler,
    broadcast_handler,
    vipbroadcast_and_pin_handler,
    vipbroadcast_handler,
    cekuser_handler,
    add_handler,
    handle_chat_join_request
)

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(Config.BOT_TOKEN).build()
    
    def register_handlers(self):
        self.app.add_handler(CommandHandler("start", start_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("order", order_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("status", status_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("tos", tos_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("admin", admin_handler, filters=filters.ChatType.PRIVATE))
        
        self.app.add_handler(CommandHandler("broadcastpin", broadcast_and_pin_handler, filters=filters.ChatType.PRIVATE, block=False))
        self.app.add_handler(CommandHandler("vipbroadcastpin", vipbroadcast_and_pin_handler, filters=filters.ChatType.PRIVATE, block=False))
        
        self.app.add_handler(CommandHandler("broadcast", broadcast_handler, filters=filters.ChatType.PRIVATE, block=False))
        self.app.add_handler(CommandHandler("vipbroadcast", vipbroadcast_handler, filters=filters.ChatType.PRIVATE, block=False))
        
        self.app.add_handler(CommandHandler("cekuser", cekuser_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("add", add_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("addindo", add_indo_handler, filters=filters.ChatType.PRIVATE))

        self.app.add_handler(CommandHandler("addcctv", add_cctv_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("addometv", add_ometv_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CommandHandler("addjav", add_jav_handler, filters=filters.ChatType.PRIVATE))

        self.app.add_handler(CallbackQueryHandler(raze_group_callback_handler, pattern="^raze_group$"))
        self.app.add_handler(CallbackQueryHandler(raze_subscribe_callback_handler, pattern="^raze_subscribe_[0-9]+_[0-9]+_[0-9]+$"))
        self.app.add_handler(CallbackQueryHandler(raze_permanen_callback_handler, pattern="^raze_permanen$"))
        self.app.add_handler(CallbackQueryHandler(raze_permanen_qris_callback_handler, pattern="^raze_permanen_qris$"))
        self.app.add_handler(CallbackQueryHandler(raze_permanen_trakteer_callback_handler, pattern="^raze_permanen_trakteer$"))
        self.app.add_handler(CallbackQueryHandler(raze_indo_vvip_callback_handler, pattern="^raze_indo_vvip$"))
        self.app.add_handler(CallbackQueryHandler(raze_indo_vvip_qris_callback_handler, pattern="^raze_indo_vvip_qris$"))

        self.app.add_handler(CallbackQueryHandler(raze_cctv_callback_handler, pattern="^raze_cctv$"))
        self.app.add_handler(CallbackQueryHandler(raze_cctv_qris_callback_handler, pattern="^raze_cctv_qris$"))
        self.app.add_handler(CallbackQueryHandler(raze_ometv_callback_handler, pattern="^raze_ometv$"))
        self.app.add_handler(CallbackQueryHandler(raze_ometv_qris_callback_handler, pattern="^raze_ometv_qris$"))
        self.app.add_handler(CallbackQueryHandler(raze_jav_callback_handler, pattern="^raze_jav$"))
        self.app.add_handler(CallbackQueryHandler(raze_jav_qris_callback_handler, pattern="^raze_jav_qris$"))

        self.app.add_handler(CommandHandler("promo", raze_promo_handler, filters=filters.ChatType.PRIVATE))

        self.app.add_handler(CallbackQueryHandler(raze_promo_monthly_qris_callback_handler, pattern="^raze_promo_monthly_qris$"))
        self.app.add_handler(CallbackQueryHandler(raze_promo_permanent_qris_callback_handler, pattern="^raze_promo_permanent_qris$"))
        self.app.add_handler(CallbackQueryHandler(raze_promo_indo_vvip_qris_callback_handler, pattern="^raze_promo_indo_vvip_qris$"))

        self.app.add_handler(CommandHandler("cancel", qris_cancel_handler, filters=filters.ChatType.PRIVATE))
        self.app.add_handler(CallbackQueryHandler(qris_callback_handler, pattern="^raze_qris_[0-9]+_[0-9]+$"))

        self.app.add_handler(CallbackQueryHandler(trakteer_callback_handler, pattern="^raze_trakteer_[0-9]+_[0-9]+$"))
        
        self.app.add_handler(CallbackQueryHandler(back_callback_handler, pattern="^raze_back$"))

        self.app.add_handler(CallbackQueryHandler(refresh_callback, pattern="^refresh$"))

        self.app.add_handler(ChatJoinRequestHandler(handle_chat_join_request))

    def run(self):
        self.app.run_polling()

bot = TelegramBot()
