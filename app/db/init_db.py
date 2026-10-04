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

SAMPLE_RESOURCES = [
    {
        "title": "National Post-Graduate Scholarship 2026",
        "description": "The National Scholarship Portal offers financial support to meritorious post-graduate students across India. Covers tuition fees, books, and living stipend for eligible candidates.",
        "category_name": "Scholarships",
        "resource_type": "Scholarship",
        "location": "India",
        "url": "https://scholarships.gov.in",
        "contact": "helpdesk@scholarships.gov.in",
        "tags": ["scholarship", "higher-education", "grants", "india"]
    },
    {
        "title": "Free Full-Stack Python & FastAPI Bootcamp",
        "description": "A comprehensive self-paced open course teaching modern Python, FastAPI backend development, database architecture, and frontend integration. Ideal for beginners and intermediate developers.",
        "category_name": "Education",
        "resource_type": "Course",
        "location": "Remote",
        "url": "https://fastapi.tiangolo.com/tutorial/",
        "contact": "info@fastapi-learn.org",
        "tags": ["python", "fastapi", "webdev", "free-course"]
    },
    {
        "title": "Kozhikode Tech Community Mentorship Program",
        "description": "Local Kozhikode developer community offering free 1-on-1 mentorship for students preparing for software engineering internships and tech careers.",
        "category_name": "Internships",
        "resource_type": "Internship",
        "location": "Kozhikode, Kerala",
        "url": "https://example.org/kozhikode-mentorship",
        "contact": "mentors@kozhikodetech.org",
        "tags": ["kozhikode", "kerala", "mentorship", "tech-jobs"]
    },
    {
        "title": "Free Design & Prototyping Tools for Non-Profits",
        "description": "Collection of open-source and free graphic design, UI prototyping, and vector graphic software available for students and civic non-profit organizations.",
        "category_name": "Free Tools",
        "resource_type": "Tool",
        "location": "Remote",
        "url": "https://penpot.app",
        "contact": "community@penpot.app",
        "tags": ["design", "free-tools", "open-source", "ui-ux"]
    },
    {
        "title": "Kerala Flood Relief & Community Volunteer Network",
        "description": "Statewide volunteer group organizing community support, emergency kit distribution, and local relief coordination across districts in Kerala.",
        "category_name": "Volunteering",
        "resource_type": "Community Service",
        "location": "Kerala",
        "url": "https://kerala.gov.in",
        "contact": "volunteer@keralarelief.org",
        "tags": ["volunteering", "kerala", "community-support"]
    },
    {
        "title": "Junior Python Web Developer Remote Internship",
        "description": "3-month remote internship for computer science students and self-taught developers. Learn REST API development, Git workflows, and database optimization.",
        "category_name": "Jobs",
        "resource_type": "Job",
        "location": "Remote",
        "url": "https://example.org/python-job",
        "contact": "careers@techstart.io",
        "tags": ["python", "entry-level", "remote-job"]
    }
]

def init_db(db: Session):
    # Create tables
    Base.metadata.create_all(bind=engine)

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

    # 3. Seed Sample Published Resources
    for res_data in SAMPLE_RESOURCES:
        cat_id = category_map.get(res_data["category_name"])
        if cat_id:
            existing_res = db.query(Resource).filter(Resource.title == res_data["title"]).first()
            if not existing_res:
                slug = generate_slug(res_data["title"])
                resource = Resource(
                    title=res_data["title"],
                    slug=slug,
                    description=res_data["description"],
                    category_id=cat_id,
                    resource_type=res_data["resource_type"],
                    location=res_data["location"],
                    url=res_data["url"],
                    contact=res_data["contact"],
                    user_id=admin.id,
                    status="published"
                )
                db.add(resource)
                db.flush()
                
                # Tags
                for tag_name in res_data.get("tags", []):
                    tag = db.query(Tag).filter(Tag.name == tag_name).first()
                    if not tag:
                        tag = Tag(name=tag_name)
                        db.add(tag)
                        db.flush()
                    resource.tags.append(tag)

    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    print("Database initialized & seeded successfully!")
