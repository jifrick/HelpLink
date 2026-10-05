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
    conn.execute(text("UPDATE rewards SET status = 'READY', asset_reference = 'app/static/images/sticker-pack.zip' WHERE name = 'HelpLink Sticker Pack'"))
    conn.commit()
    print("Updated HelpLink Sticker Pack.")
