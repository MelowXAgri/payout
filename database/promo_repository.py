from database.mongo import mongo

class PromoRepository:
    def __init__(self):
        self.promo = mongo.db.promo