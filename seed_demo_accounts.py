"""Seed demo accounts for portfolio demonstrations"""
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.db.session import SessionLocal
from app.models.user import User
from app.models.organization import Organization

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_demo_accounts():
    """Create 3 demo accounts for portfolio"""
    db: Session = SessionLocal()

    try:
        # Create demo organizations
        orgs = [
            {
                "org_id": uuid.uuid4(),
                "name": "Acme Corporation",
                "plan": "professional"
            },
            {
                "org_id": uuid.uuid4(),
                "name": "TechStart Inc",
                "plan": "professional"
            },
            {
                "org_id": uuid.uuid4(),
                "name": "Global Ventures",
                "plan": "enterprise"
            }
        ]

        # Check if orgs already exist, if not create them
        for org_data in orgs:
            existing_org = db.query(Organization).filter(Organization.name == org_data["name"]).first()
            if not existing_org:
                org = Organization(**org_data)
                db.add(org)
                print(f"Created organization: {org_data['name']}")
            else:
                org_data["org_id"] = existing_org.org_id
                print(f"Organization already exists: {org_data['name']}")

        db.commit()

        # Create demo users
        demo_users = [
            {
                "user_id": uuid.uuid4(),
                "org_id": orgs[0]["org_id"],
                "email": "demo@acme.com",
                "name": "Sarah Anderson",
                "password_hash": hash_password("Demo123!"),
                "role": "admin",
                "is_active": True
            },
            {
                "user_id": uuid.uuid4(),
                "org_id": orgs[1]["org_id"],
                "email": "demo@techstart.com",
                "name": "Michael Chen",
                "password_hash": hash_password("Demo123!"),
                "role": "admin",
                "is_active": True
            },
            {
                "user_id": uuid.uuid4(),
                "org_id": orgs[2]["org_id"],
                "email": "demo@global.com",
                "name": "Emily Rodriguez",
                "password_hash": hash_password("Demo123!"),
                "role": "admin",
                "is_active": True
            }
        ]

        for user_data in demo_users:
            existing_user = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing_user:
                user = User(**user_data)
                db.add(user)
                print(f"Created user: {user_data['email']} (Password: Demo123!)")
            else:
                print(f"User already exists: {user_data['email']}")

        db.commit()

        print("\n" + "="*60)
        print("DEMO ACCOUNTS CREATED SUCCESSFULLY!")
        print("="*60)
        print("\nYou can use these credentials for portfolio demonstrations:\n")
        print("1. Email: demo@acme.com")
        print("   Password: Demo123!")
        print("   Organization: Acme Corporation\n")

        print("2. Email: demo@techstart.com")
        print("   Password: Demo123!")
        print("   Organization: TechStart Inc\n")

        print("3. Email: demo@global.com")
        print("   Password: Demo123!")
        print("   Organization: Global Ventures\n")
        print("="*60)

    except Exception as e:
        print(f"Error creating demo accounts: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_accounts()
