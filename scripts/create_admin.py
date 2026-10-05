import os
import sys

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal
from app.services.auth_service import create_user, get_user_by_email
from app.schemas.user import UserCreate

def main():
    email = "admin@helplink.org"
    password = "AdminPassword123!"
    full_name = "System Administrator"

    db = SessionLocal()
    try:
        existing_user = get_user_by_email(db, email)
        if existing_user:
            if existing_user.role != "admin":
                existing_user.role = "admin"
                db.commit()
                print(f"User {email} already existed. Updated their role to 'admin'.")
            else:
                print(f"Admin user {email} already exists.")
            print(f"You can log in at /admin/login with:\nEmail: {email}\nPassword: {password}")
            return
            
        user_in = UserCreate(email=email, password=password, full_name=full_name)
        user = create_user(db, user_in, role="admin")
        print("✅ Successfully created Admin User!")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print("This account is saved directly to your Supabase database.")
        print("You can now log in at the /admin/login page.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
