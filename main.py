import asyncio
import uvicorn
from fastapi import FastAPI
from bot.bot import bot
from bot.job_queue import setup_jobs
from telegram import BotCommand
from trakteer.webhook import router

app = FastAPI()

# Tambahkan webhook Trakteer ke FastAPI
app.include_router(router)

web_server = uvicorn.Server(
    config=uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
)

async def main():
    bot.register_handlers()
    setup_jobs(bot.app.job_queue)
    async with bot.app:
        await bot.app.initialize()
        await bot.app.start()
        await bot.app.bot.set_my_commands([
            BotCommand("start", "Menampilkan menu"),
            BotCommand("order", "Untuk join group VIP"),
            BotCommand("status", "Untuk melihat status VIP anda"),
            BotCommand("promo", "Untuk melihat promo yang tersedia"),
            BotCommand("tos", "Untuk melihat syarat dan ketentuan VIP"),
        ])
        await bot.app.updater.start_polling()
        await web_server.serve()
        await bot.app.updater.stop()
        await bot.app.stop()

if __name__ == "__main__":
    asyncio.run(main())