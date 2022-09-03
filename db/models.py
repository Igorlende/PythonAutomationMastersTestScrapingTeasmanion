from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from config import DB_STRING_CONNECTION_TO_ALCHEMY


engine = create_engine(DB_STRING_CONNECTION_TO_ALCHEMY, echo=True)
Base = declarative_base()


class TelegramUsers(Base):
    __tablename__ = "telegram_users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String)

    def __repr__(self):
        return "TelegramUser(id={0}, telegram_id={1})".format(self.id, self.telegram_id)

