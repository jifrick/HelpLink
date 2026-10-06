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
    for i in range(1, 11):
        pack_num = f"{i:02d}"
        threshold = i * 100
        print(f"Updating Sticker Pack {pack_num} to milestone {threshold}...")
        
        # We need to make sure we don't accidentally update test data if it's there, but we match exactly on name
        # For example, "HelpLink Sticker Pack 01 - Discover"
        
        conn.execute(text("""
            UPDATE rewards
            SET is_milestone = TRUE,
                milestone_threshold = :threshold,
                cost_hp = 0
            WHERE name LIKE :name_pattern
        """), {"threshold": threshold, "name_pattern": f"HelpLink Sticker Pack {pack_num}%"})
        
    conn.commit()
    print("All sticker packs updated to milestone rewards.")
