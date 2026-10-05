import sys
import os
from app.db.session import SessionLocal
from app.models.gamification import Reward

def run_seed():
    db = SessionLocal()
    print("Seeding initial rewards...")
    
    rewards = [
        {"name": "HelpLink Sticker Pack", "cost_hp": 100, "description": "Exclusive digital sticker pack for your messaging apps.", "reward_type": "DIGITAL_DOWNLOAD"},
        {"name": "Contributor Profile Badge", "cost_hp": 150, "description": "A shiny badge for your public HelpLink profile.", "reward_type": "BADGE"},
        {"name": "HelpLink Wallpaper Pack", "cost_hp": 150, "description": "High-quality desktop and mobile wallpapers.", "reward_type": "DIGITAL_DOWNLOAD"},
        {"name": "LinkedIn Contributor Banner", "cost_hp": 200, "description": "Official HelpLink banner for your LinkedIn profile.", "reward_type": "DIGITAL_DOWNLOAD"},
        {"name": "Resource Sharing Templates", "cost_hp": 250, "description": "Canva templates to share your resources on social media.", "reward_type": "DIGITAL_DOWNLOAD"},
        {"name": "Contributor Certificate", "cost_hp": 300, "description": "Official certificate of contribution to the HelpLink community.", "reward_type": "DIGITAL_DOWNLOAD"}
    ]
    
    count = 0
    for r in rewards:
        existing = db.query(Reward).filter_by(name=r["name"]).first()
        if not existing:
            reward = Reward(
                name=r["name"],
                description=r["description"],
                cost_hp=r["cost_hp"],
                reward_type=r["reward_type"]
            )
            db.add(reward)
            count += 1
            
    db.commit()
    db.close()
    print(f"Seeded {count} new rewards.")

if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_seed()
