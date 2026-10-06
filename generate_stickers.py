import os
import zipfile
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Packs configuration
packs = [
    {"id": 1, "slug": "discover", "title": "HelpLink Sticker Pack 01 - Discover", "stickers": ["Nice Find!", "Useful!"], "colors": ("#2563EB", "#60A5FA"), "shape": "circle"},
    {"id": 2, "slug": "share", "title": "HelpLink Sticker Pack 02 - Share", "stickers": ["Shared!", "Spread Word!"], "colors": ("#059669", "#34D399"), "shape": "pill"},
    {"id": 3, "slug": "helpful", "title": "HelpLink Sticker Pack 03 - Helpful", "stickers": ["Happy to Help!", "You're Helpful!"], "colors": ("#7C3AED", "#A78BFA"), "shape": "rounded"},
    {"id": 4, "slug": "community", "title": "HelpLink Sticker Pack 04 - Community", "stickers": ["Community First", "Together"], "colors": ("#DB2777", "#F472B6"), "shape": "hexagon"},
    {"id": 5, "slug": "achievement", "title": "HelpLink Sticker Pack 05 - Achievement", "stickers": ["Great Work!", "Community Win!"], "colors": ("#D97706", "#FBBF24"), "shape": "star"},
    {"id": 6, "slug": "helppoints", "title": "HelpLink Sticker Pack 06 - HelpPoints", "stickers": ["+50 HelpPoints", "Points Earned!"], "colors": ("#4F46E5", "#818CF8"), "shape": "octagon"},
    {"id": 7, "slug": "level-up", "title": "HelpLink Sticker Pack 07 - Level Up", "stickers": ["Level Up!", "Keep Growing!"], "colors": ("#0284C7", "#38BDF8"), "shape": "shield"},
    {"id": 8, "slug": "thank-you", "title": "HelpLink Sticker Pack 08 - Thank You", "stickers": ["Thank You!", "Appreciated!"], "colors": ("#E11D48", "#FB7185"), "shape": "heart"},
    {"id": 9, "slug": "resource-hero", "title": "HelpLink Sticker Pack 09 - Resource Hero", "stickers": ["Resource Hero", "Great Share!"], "colors": ("#0D9488", "#2DD4BF"), "shape": "burst"},
    {"id": 10, "slug": "celebration", "title": "HelpLink Sticker Pack 10 - Celebration", "stickers": ["Well Done!", "Huge Impact!"], "colors": ("#C026D3", "#E879F9"), "shape": "badge"}
]

SIZE = 1024
PADDING = 120

def get_font(size):
    try:
        return ImageFont.truetype("segoeuib.ttf", size)
    except:
        try:
            return ImageFont.truetype("arialbd.ttf", size)
        except:
            return ImageFont.load_default(size=size)

def draw_polygon(draw, points, fill):
    draw.polygon(points, fill=fill)

def get_star_points(cx, cy, r_outer, r_inner, points_count=5):
    points = []
    angle = math.pi / 2 * 3
    step = math.pi / points_count
    for i in range(points_count * 2):
        r = r_outer if i % 2 == 0 else r_inner
        points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
        angle += step
    return points

def get_polygon_points(cx, cy, r, sides):
    points = []
    angle = math.pi / 2 * 3 if sides % 2 != 0 else math.pi / sides
    step = 2 * math.pi / sides
    for _ in range(sides):
        points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
        angle += step
    return points

def generate_sticker(text, color1, color2, shape_type, bg_transparent=True):
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Border sizes
    outer_border = 30
    cx, cy = SIZE // 2, SIZE // 2
    r_outer = SIZE // 2 - PADDING
    r_inner = r_outer - outer_border
    
    # Base shapes for sticker border (white) and inner (color)
    def draw_shape(d, fill_color, radius):
        if shape_type == "circle":
            d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=fill_color)
        elif shape_type == "pill":
            w, h = radius * 1.5, radius * 0.8
            d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=min(w,h)//2, fill=fill_color)
        elif shape_type == "rounded":
            w, h = radius, radius
            d.rounded_rectangle([cx - w, cy - h, cx + w, cy + h], radius=radius//4, fill=fill_color)
        elif shape_type == "hexagon":
            pts = get_polygon_points(cx, cy, radius, 6)
            d.polygon(pts, fill=fill_color)
        elif shape_type == "octagon":
            pts = get_polygon_points(cx, cy, radius, 8)
            d.polygon(pts, fill=fill_color)
        elif shape_type == "star":
            pts = get_star_points(cx, cy, radius, radius * 0.45, 5)
            d.polygon(pts, fill=fill_color)
        elif shape_type == "burst":
            pts = get_star_points(cx, cy, radius, radius * 0.8, 12)
            d.polygon(pts, fill=fill_color)
        elif shape_type == "badge":
            pts = get_star_points(cx, cy, radius, radius * 0.9, 20)
            d.polygon(pts, fill=fill_color)
        elif shape_type == "shield":
            w, h = radius * 0.8, radius
            pts = [
                (cx - w, cy - h), (cx + w, cy - h), 
                (cx + w, cy + h * 0.2), (cx, cy + h), (cx - w, cy + h * 0.2)
            ]
            d.polygon(pts, fill=fill_color)
        elif shape_type == "heart":
            # Simplified heart with overlapping circles and triangle
            w = radius * 0.9
            h = radius * 0.9
            # Left circle
            d.ellipse([cx - w, cy - h, cx, cy], fill=fill_color)
            # Right circle
            d.ellipse([cx, cy - h, cx + w, cy], fill=fill_color)
            # Bottom triangle
            d.polygon([(cx - w + 5, cy - w/2), (cx + w - 5, cy - w/2), (cx, cy + h)], fill=fill_color)
        else:
            d.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=fill_color)

    # 1. Draw white sticker border on a separate layer for drop shadow
    shadow_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow_layer)
    draw_shape(s_draw, (0, 0, 0, 100), r_outer)
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(25))
    
    border_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(border_layer)
    draw_shape(b_draw, (255, 255, 255, 255), r_outer)
    
    # 2. Draw inner gradient/color
    draw_shape(b_draw, color1, r_inner)
    
    # Draw smaller inner highlight
    draw_shape(b_draw, color2, r_inner - 20)
    
    # Text
    font_size = 120
    font = get_font(font_size)
    
    # Reduce font size if text is too long
    while font.getlength(text) > (r_inner * 1.8):
        font_size -= 5
        font = get_font(font_size)
    
    # Split text into two lines if it's still too wide or has space
    lines = [text]
    if " " in text and font.getlength(text) > r_inner * 1.4:
        words = text.split(" ")
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
        
    y_offset = cy - (len(lines) * font_size // 2)
    for line in lines:
        left, top, right, bottom = font.getbbox(line)
        w = right - left
        h = bottom - top
        # Drop shadow for text
        b_draw.text((cx - w/2 + 5, y_offset + 5), line, font=font, fill=(0,0,0,80))
        b_draw.text((cx - w/2, y_offset), line, font=font, fill=(255,255,255,255))
        y_offset += font_size
    
    # Combine
    img.alpha_composite(shadow_layer)
    img.alpha_composite(border_layer)
    
    return img


def create_packs():
    base_dir = "app/static/rewards/stickers"
    os.makedirs(base_dir, exist_ok=True)
    
    db_records = []

    for pack in packs:
        pack_dir = f"{base_dir}/pack-{pack['id']:02d}-{pack['slug']}"
        os.makedirs(pack_dir, exist_ok=True)
        
        # Generate stickers
        img1 = generate_sticker(pack['stickers'][0], pack['colors'][0], pack['colors'][1], pack['shape'])
        img2 = generate_sticker(pack['stickers'][1], pack['colors'][1], pack['colors'][0], pack['shape']) # Flipped colors for variety
        
        img1_path = f"{pack_dir}/sticker-01.png"
        img2_path = f"{pack_dir}/sticker-02.png"
        img1.save(img1_path)
        img2.save(img2_path)
        
        # Create preview
        preview = Image.new("RGBA", (SIZE*2, SIZE), (0,0,0,0))
        preview.paste(img1.resize((SIZE, SIZE)), (0, 0))
        preview.paste(img2.resize((SIZE, SIZE)), (SIZE, 0))
        preview_path = f"{pack_dir}/preview.png"
        preview.save(preview_path)
        
        # Create ZIP
        zip_path = f"app/static/rewards/HelpLink_Sticker_Pack_{pack['id']:02d}.zip"
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(img1_path, "sticker-01.png")
            zipf.write(img2_path, "sticker-02.png")
            
        db_records.append({
            "name": pack["title"],
            "description": f"Contains 2 exclusive digital stickers: '{pack['stickers'][0]}' and '{pack['stickers'][1]}'.",
            "cost_hp": 100 + (pack['id'] * 10), # 110 to 200 HP
            "reward_type": "DIGITAL_DOWNLOAD",
            "status": "READY",
            "asset_reference": zip_path,
            "thumbnail": preview_path,
            "is_active": True
        })
        
    return db_records

def update_db(records):
    load_dotenv()
    db_url = os.environ.get("DATABASE_URL")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://")
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://")

    engine = create_engine(db_url)
    with engine.connect() as conn:
        for r in records:
            # Check if exists
            existing = conn.execute(text("SELECT id FROM rewards WHERE name = :name"), {"name": r["name"]}).fetchone()
            if existing:
                conn.execute(text("""
                    UPDATE rewards 
                    SET description = :desc, cost_hp = :cost, status = :status, asset_reference = :asset, thumbnail = :thumb, is_active = :active
                    WHERE name = :name
                """), {
                    "name": r["name"], "desc": r["description"], "cost": r["cost_hp"], 
                    "status": r["status"], "asset": r["asset_reference"], "thumb": r["thumbnail"], "active": r["is_active"]
                })
            else:
                conn.execute(text("""
                    INSERT INTO rewards (name, description, cost_hp, reward_type, status, asset_reference, thumbnail, is_active, redemption_limit, created_at, updated_at) 
                    VALUES (:name, :desc, :cost, :type, :status, :asset, :thumb, :active, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """), {
                    "name": r["name"], "desc": r["description"], "cost": r["cost_hp"], "type": r["reward_type"],
                    "status": r["status"], "asset": r["asset_reference"], "thumb": r["thumbnail"], "active": r["is_active"]
                })
        conn.commit()
        print("Successfully updated database with 10 sticker pack rewards.")

if __name__ == "__main__":
    print("Generating stickers...")
    records = create_packs()
    print("Updating database...")
    update_db(records)
    print("Done!")
