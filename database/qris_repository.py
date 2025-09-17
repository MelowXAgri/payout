from datetime import datetime
from database.mongo import mongo

class QrisRepository:
    def __init__(self):
        self.qris = mongo.db.qris

    async def add_qris(self, user_id: int, msg_id: int, duration: int, qris_code: str, qris_url: str, expiry: datetime) -> None:
        if not await self.qris.find_one({"user_id": user_id}):
            await self.qris.update_one(
                {"user_id": user_id},
                {"$set": {"user_id": user_id, "msg_id": msg_id, "duration": duration, "qris": qris_code, "qris_url": qris_url, "expiry": expiry}},
                upsert=True
            )

    async def remove_qris(self, user_id: int) -> None:
        if await self.qris.find_one({"user_id": user_id}):
            await self.qris.delete_one({"user_id": user_id})
