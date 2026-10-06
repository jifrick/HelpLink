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
    # 1. Add lifetime_helppoints to users if not exists
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN lifetime_helppoints INTEGER NOT NULL DEFAULT 0;"))
        print("Added lifetime_helppoints to users.")
    except Exception as e:
        print("lifetime_helppoints may already exist:", e)
    
    # 2. Add is_milestone and milestone_threshold to rewards
    try:
        conn.execute(text("ALTER TABLE rewards ADD COLUMN is_milestone BOOLEAN NOT NULL DEFAULT FALSE;"))
        conn.execute(text("ALTER TABLE rewards ADD COLUMN milestone_threshold INTEGER;"))
        print("Added is_milestone and milestone_threshold to rewards.")
    except Exception as e:
        print("reward milestone columns may already exist:", e)
        
    conn.commit()

# Now populate the lifetime_helppoints based on point_transactions (sum of amounts where amount > 0)
with engine.connect() as conn:
    conn.execute(text("""
        UPDATE users u
        SET lifetime_helppoints = COALESCE((
            SELECT SUM(amount) FROM point_transactions p 
            WHERE p.user_id = u.id AND p.amount > 0
        ), 0)
    """))
    conn.commit()
    print("Populated lifetime_helppoints for users.")
