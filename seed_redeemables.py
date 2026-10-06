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
    # Check if we already have it
    res = conn.execute(text("SELECT id FROM rewards WHERE name = 'HelpLink Premium Creator Kit'")).first()
    if not res:
        print("Inserting HelpLink Premium Creator Kit...")
        conn.execute(text("""
            INSERT INTO rewards (
                name, description, cost_hp, reward_type, status, 
                asset_reference, thumbnail, is_active, is_milestone, redemption_limit,
                created_at, updated_at
            ) VALUES (
                'HelpLink Premium Creator Kit',
                'Downloadable community templates, social media banner templates, and exclusive profile highlight assets.',
                500,
                'DIGITAL_DOWNLOAD',
                'READY',
                'static/rewards/premium_creator_kit.zip',
                'static/img/creator_kit_thumb.png',
                TRUE, FALSE, 1,
                NOW(), NOW()
            )
        """))
    else:
        print("Creator kit already exists.")
        
    res2 = conn.execute(text("SELECT id FROM rewards WHERE name = 'Exclusive Profile Frames'")).first()
    if not res2:
        print("Inserting Exclusive Profile Frames...")
        conn.execute(text("""
            INSERT INTO rewards (
                name, description, cost_hp, reward_type, status, 
                asset_reference, thumbnail, is_active, is_milestone, redemption_limit,
                created_at, updated_at
            ) VALUES (
                'Exclusive Profile Frames',
                'Unlock exclusive digital profile frames to stand out as a top contributor in the community.',
                250,
                'DIGITAL_DOWNLOAD',
                'READY',
                'static/rewards/profile_frames.zip',
                'static/img/frames_thumb.png',
                TRUE, FALSE, 1,
                NOW(), NOW()
            )
        """))
    else:
        print("Profile frames already exists.")

    conn.commit()
    print("Redeemable rewards seeded successfully.")

# Create dummy zip files for testing
os.makedirs("app/static/rewards", exist_ok=True)
with open("app/static/rewards/premium_creator_kit.zip", "wb") as f:
    f.write(b"PK\x05\x06" + b"\x00"*18) # Empty valid zip
with open("app/static/rewards/profile_frames.zip", "wb") as f:
    f.write(b"PK\x05\x06" + b"\x00"*18) # Empty valid zip
    
os.makedirs("app/static/img", exist_ok=True)
# Create dummy images
with open("app/static/img/creator_kit_thumb.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")
with open("app/static/img/frames_thumb.png", "wb") as f:
    f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82")

print("Dummy assets created.")
