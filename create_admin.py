"""
create_admin.py
Script to create the first admin user and set up database tables.
Run this once to initialize your application.
"""
from app.models.user import User, Base
from app.utils.db import engine, SessionLocal

def create_admin_user():
    """Create the first admin user and set up database."""
    
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            username="admin",
            hashed_password=User.get_password_hash("admin123")
        )
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")
        print("⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 