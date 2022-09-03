from sqlalchemy import Column, Integer, String, MetaData, Table
from sqlalchemy import create_engine
from config import DB_STRING_CONNECTION_TO_ALCHEMY


engine = create_engine(DB_STRING_CONNECTION_TO_ALCHEMY, echo=True)
meta = MetaData()
telegram_users = Table("telegram_users", meta, Column("id", Integer, primary_key=True),
                       Column("telegram_id", String(50)))
meta.create_all(engine)


