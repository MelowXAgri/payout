from datetime import datetime
from database.mongo import mongo

class UserRepository:
    def __init__(self):
        self.users = mongo.db.users
        self.vip_users = mongo.db.members
        self.indo_vvip_users = mongo.db.indo_vvip_users
        self.cctv_ngintip_users = mongo.db.cctv_ngintip_users
        self.ometv_users = mongo.db.ometv_users
        self.asean_jav_users = mongo.db.asean_jav_users

    async def add_user(self, user_id: int) -> None:
        user = await self.users.find_one({"user_id": user_id})
        if not user:
            await self.users.update_one(
                {"user_id": user_id},
                {"$set": {"user_id": user_id}},
                upsert=True
            )

    async def remove_user(self, user_id: int) -> None:
        user = await self.users.find_one({"user_id": user_id})
        if user:
            await self.users.delete_one({"user_id": user_id})

    async def add_vip_user(self, user_id: int, expiry: datetime) -> None:
        await self.vip_users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "expiry": expiry}},
            upsert=True
        )
    
    async def remove_vip_user(self, user_id: int) -> None:
        user = await self.vip_users.find_one({"user_id": user_id})
        if user:
            await self.vip_users.delete_one({"user_id": user_id})

    async def add_indo_vip_user(self, user_id: int) -> None:
        await self.indo_vvip_users.update_one(
            {"user_id": user_id},
            {"$set": {
                    "user_id": user_id
                }
            },
            upsert=True
        )
    
    async def remove_indo_vip_user(self, user_id: int) -> None:
        user = await self.indo_vvip_users.find_one({"user_id": user_id})
        if user:
            await self.indo_vvip_users.delete_one({"user_id": user_id})
    
    async def add_cctv_vip_user(self, user_id: int) -> None:
        await self.cctv_ngintip_users.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id
            }},
            upsert=True
        )

    async def add_ometv_vip_user(self, user_id: int) -> None:
        await self.ometv_users.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id
            }},
            upsert=True
        )
        
    async def add_jav_vip_user(self, user_id: int) -> None:
        await self.asean_jav_users.update_one(
            {"user_id": user_id},
            {"$set": {
                "user_id": user_id
            }},
            upsert=True
        )