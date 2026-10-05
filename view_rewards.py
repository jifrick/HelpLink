import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
db_url = os.environ.get("DATABASE_URL")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://")
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, name, status, reward_type, asset_reference FROM rewards;"))
    for row in result:
        print(row)
