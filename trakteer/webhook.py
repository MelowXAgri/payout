import asyncio
from fastapi import APIRouter, Request, HTTPException, Header
from config import Config
from helpers.pricing import pricing, life_time
from helpers.notifications import notify_telegram
from bot.bot import bot

router = APIRouter()

@router.post("/trakteer/callback")
async def trakteer_callback(request: Request, x_webhook_token: str = Header(None)):
    if x_webhook_token != Config.TRAKTEER_WEBHOOK_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")
    data = await request.json()
    if not data:
        raise HTTPException(status_code=400, detail="Invalid data")
    name = data.get("supporter_name")
    amount = data.get("quantity")
    supporter_message = data.get("supporter_message", "")
    user_id = None
    lifetime = False
    if "_" in supporter_message:
        parts = supporter_message.split("_")
        if len(parts) > 2:
            try:
                user_id = int(parts[2])
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid user ID format")
        if len(parts) > 3:
            try:
                if parts[3] == "lifetime" and amount == life_time['trakteer']:
                    lifetime = True
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid amount format")
    if user_id is None:
        raise HTTPException(status_code=400, detail="User ID not found in supporter message")
    plan = next((p for p in pricing if p['price']['trakteer'] == amount), None)
    if plan and not lifetime:
        # Gunakan application.create_task() sehingga task dijalankan di loop bot
        try:
            bot.app.create_task(notify_telegram(bot.app.bot, user_id, plan['duration']))
        except:
            asyncio.create_task(notify_telegram(bot.app.bot, user_id, plan['duration']))
    elif lifetime and amount == life_time['trakteer']:
        # Gunakan application.create_task() sehingga task dijalankan di loop bot
        try:
            bot.app.create_task(notify_telegram(bot.app.bot, user_id, "lifetime", name))
        except:
            asyncio.create_task(notify_telegram(bot.app.bot, user_id, "lifetime", name))
    else:
        raise HTTPException(status_code=400, detail="Invalid amount")
    return {"status": "success", "message": "Webhook received"}
