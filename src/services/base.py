from src.db.manager import DBManager


class BaseService:
    def __init__(self, db: DBManager):
        self.db = db
