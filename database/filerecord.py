from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://shahrul2001hidayat:JVEY3ZBuwxYKSKA4@cluster0.5fvzpgj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

class DBBotContent:
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db     = self.client["bot-content"]
        self.users  = self.db.users
    
    async def close(self) -> None:
        self.client.close()

    async def add_user(self, user_id: int, username: str) -> None:
        await self.users.update_one(
            {"user_id": user_id},
            {"$set": {"user_id": user_id, "username": username}},
            upsert=True
        )

    async def remove_user(self, user_id: int) -> None:
        user = await self.users.find_one({"user_id": user_id})
        if user:
            await self.users.delete_one({"user_id": user_id})