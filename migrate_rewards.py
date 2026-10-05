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
    try:
        conn.execute(text("ALTER TABLE rewards ADD COLUMN status VARCHAR(50) DEFAULT 'DRAFT' NOT NULL;"))
        conn.execute(text("ALTER TABLE rewards ADD COLUMN asset_reference VARCHAR(255);"))
        conn.execute(text("ALTER TABLE rewards ADD COLUMN thumbnail VARCHAR(255);"))
        conn.execute(text("ALTER TABLE rewards ADD COLUMN inventory INTEGER;"))
        conn.execute(text("ALTER TABLE rewards ADD COLUMN redemption_limit INTEGER DEFAULT 1 NOT NULL;"))
        conn.execute(text("ALTER TABLE rewards ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL;"))
        conn.commit()
        print("Columns added successfully.")
    except Exception as e:
        print(f"Error: {e}")

