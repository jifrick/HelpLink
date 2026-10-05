import sys
import os
import random
import string
from sqlalchemy import text
from app.db.session import SessionLocal, engine, Base
from app.models.gamification import PointTransaction, FraudEvent, ModerationEvent, AdminAuditLog, Badge, UserBadge, Reward, RewardRedemption

def generate_contributor_id():
    # HL-XXXXXX (no confusing characters)
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    suffix = "".join(random.choices(chars, k=6))
    return f"HL-{suffix}"

def run_migration():
    db = SessionLocal()
    print("Running gamification migration...")
    
    # 1. Alter Users Table
    print("Updating users table...")
    try:
        bind = db.get_bind()
        dialect_name = bind.dialect.name
        
        cols = [
            ("contributor_id", "VARCHAR(20)"),
            ("helppoints_balance", "INTEGER DEFAULT 0"),
            ("level", "VARCHAR(50) DEFAULT 'New Contributor'"),
            ("trust_score", "INTEGER DEFAULT 50"),
            ("fraud_risk_score", "INTEGER DEFAULT 0"),
            ("account_status", "VARCHAR(20) DEFAULT 'ACTIVE'")
        ]
        
        for col_name, col_type in cols:
            try:
                db.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Skipping or handled {col_name}: {e}")
                
        # Unique constraint on contributor_id
        try:
            db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_contributor_id ON users (contributor_id);"))
            db.commit()
        except Exception:
            db.rollback()
            
    except Exception as e:
        print(f"Error updating users table: {e}")
        
    # 2. Alter Resources Table
    print("Updating resources table...")
    try:
        db.execute(text("ALTER TABLE resources ADD COLUMN IF NOT EXISTS risk_score INTEGER DEFAULT 0;"))
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Skipping risk_score: {e}")
        
    # 3. Create new tables
    print("Creating new gamification tables...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Error creating tables: {e}")
        
    # 4. Backfill contributor IDs
    print("Backfilling contributor IDs...")
    try:
        users_no_id = db.execute(text("SELECT id FROM users WHERE contributor_id IS NULL")).fetchall()
        for u in users_no_id:
            user_id = u[0]
            new_id = generate_contributor_id()
            db.execute(text("UPDATE users SET contributor_id = :cid WHERE id = :uid"), {"cid": new_id, "uid": user_id})
        db.commit()
        print(f"Backfilled {len(users_no_id)} users.")
    except Exception as e:
        db.rollback()
        print(f"Error backfilling: {e}")
        
    db.close()
    print("Migration complete!")

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_migration()
