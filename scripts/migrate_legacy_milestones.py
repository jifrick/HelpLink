import os
import sys
from dotenv import load_dotenv

# Add app to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.db.session import SessionLocal
from app.models.user import User
from app.models.gamification import PointTransaction, RewardRedemption
from app.services.gamification_service import evaluate_milestones

def migrate(db: Session = None):
    load_dotenv()
    
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True
    
    print("==================================================")
    print("HELP-LINK MIGRATION: LEGACY USER MILESTONES")
    print("==================================================")
    
    users_processed = 0
    users_updated = 0
    stickers_granted_total = 0
    users_100_plus = 0
    users_500_plus = 0
    users_1000_plus = 0
    
    try:
        users = db.query(User).all()
        for user in users:
            users_processed += 1
            
            # 1. Calculate true historical lifetime HP based on all positive transactions
            total_earned = db.query(func.sum(PointTransaction.amount)).filter(
                PointTransaction.user_id == user.id,
                PointTransaction.amount > 0
            ).scalar() or 0
            
            # Ensure it's correctly mapped
            user_needs_update = False
            if user.lifetime_helppoints != total_earned:
                user.lifetime_helppoints = total_earned
                user_needs_update = True
                
            # 2. Count existing redemptions before evaluation
            existing_redemptions = db.query(RewardRedemption).filter_by(user_id=user.id).count()
            
            # 3. Evaluate milestones based on the updated lifetime HP
            evaluate_milestones(db, user)
            db.commit() # Evaluate milestones performs a flush/commit, let's commit here safely
            
            # 4. Check new redemptions count
            new_redemptions = db.query(RewardRedemption).filter_by(user_id=user.id).count()
            stickers_granted = new_redemptions - existing_redemptions
            
            if stickers_granted > 0:
                stickers_granted_total += stickers_granted
                user_needs_update = True
                
            if user_needs_update:
                users_updated += 1
                
            if total_earned >= 1000:
                users_1000_plus += 1
                users_500_plus += 1
                users_100_plus += 1
            elif total_earned >= 500:
                users_500_plus += 1
                users_100_plus += 1
            elif total_earned >= 100:
                users_100_plus += 1
                
        print(f"\nMigration completed successfully.")
        print(f"Users processed: {users_processed}")
        print(f"Users updated: {users_updated}")
        print(f"Sticker milestones granted: {stickers_granted_total}")
        print(f"Users with 100+ HP: {users_100_plus}")
        print(f"Users with 500+ HP: {users_500_plus}")
        print(f"Users with 1000+ HP: {users_1000_plus}")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    migrate()
