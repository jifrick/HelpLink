from sqlalchemy.orm import Session
from app.db.session import engine, Base, SessionLocal
from app.models.category import Category
from app.models.user import User
from app.models.resource import Resource
from app.models.tag import Tag
from app.core.config import settings
from app.core.security import get_password_hash
from app.services.utils import generate_slug

INITIAL_CATEGORIES = [
    {
        "name": "Education",
        "description": "Courses, tutorials, learning materials, and educational programs.",
        "icon": "book-open"
    },
    {
        "name": "Jobs",
        "description": "Full-time, entry-level, remote, and local job opportunities.",
        "icon": "briefcase"
    },
    {
        "name": "Internships",
        "description": "Internships, fellowships, and practical student programs.",
        "icon": "academic-cap"
    },
    {
        "name": "Scholarships",
        "description": "Scholarships, grants, and educational funding opportunities.",
        "icon": "gift"
    },
    {
        "name": "Volunteering",
        "description": "Volunteer opportunities and social-impact community participation.",
        "icon": "heart"
    },
    {
        "name": "Community Support",
        "description": "Essential community services, public aid, and support programs.",
        "icon": "user-group"
    },
    {
        "name": "Free Tools",
        "description": "Free developer tools, software, design assets, and digital utilities.",
        "icon": "wrench-screwdriver"
    },
    {
        "name": "Events",
        "description": "Workshops, public hackathons, community meetups, and webinars.",
        "icon": "calendar"
    }
]



from sqlalchemy import text

def ensure_schema_migrations(db: Session):
    """Ensure newly added columns (supabase_uid, avatar_url) exist on existing tables."""
    try:
        bind = db.get_bind()
        dialect_name = bind.dialect.name if bind else ""
        if dialect_name == "postgresql":
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS supabase_uid VARCHAR(255);"))
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(512);"))
            db.execute(text("ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;"))
            db.commit()
        elif dialect_name == "sqlite":
            for col, col_type in [("supabase_uid", "VARCHAR(255)"), ("avatar_url", "VARCHAR(512)")]:
                try:
                    db.execute(text(f"ALTER TABLE users ADD COLUMN {col} {col_type};"))
                    db.commit()
                except Exception:
                    db.rollback()
    except Exception as e:
        db.rollback()

def init_db(db: Session):
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    ensure_schema_migrations(db)


    # 1. Seed Categories
    category_map = {}
    for cat_data in INITIAL_CATEGORIES:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            slug = generate_slug(cat_data["name"])
            cat = Category(
                name=cat_data["name"],
                slug=slug,
                description=cat_data["description"],
                icon=cat_data["icon"]
            )
            db.add(cat)
            db.flush()
            category_map[cat_data["name"]] = cat.id
        else:
            category_map[existing.name] = existing.id

    # 2. Seed Admin User
    admin = db.query(User).filter(User.email == settings.ADMIN_INITIAL_EMAIL.lower()).first()
    if not admin:
        if settings.ENV == "production" and settings.ADMIN_INITIAL_PASSWORD == "AdminDevPassword123!":
            raise ValueError("CRITICAL: Production environment detected, but default ADMIN_INITIAL_PASSWORD is in use. Set a secure ADMIN_INITIAL_PASSWORD in environment variables.")
        admin = User(
            email=settings.ADMIN_INITIAL_EMAIL.lower(),
            full_name="HelpLink Administrator",
            password_hash=get_password_hash(settings.ADMIN_INITIAL_PASSWORD),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.flush()



    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    print("Database initialized & seeded successfully!")
