from motor.motor_asyncio import AsyncIOMotorClient
from config import Config

class MongoDB:
    def __init__(self) -> None:
        self.client = AsyncIOMotorClient(Config.MONGO_URI)
        self.db     = self.client["khie_vip_subscription_bot"]
        # self.db     = self.client["tes_vip_subscription_bot"]
    
    async def close(self) -> None:
        self.client.close()

mongo = MongoDB()