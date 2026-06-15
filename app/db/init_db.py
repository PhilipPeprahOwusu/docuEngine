"""Initialize database with initial data"""
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash


def init_db(db: Session) -> None:
    """
    Initialize database with default data
    Create initial superuser if it doesn't exist
    """
    # Check if superuser already exists
    user = db.query(User).filter(User.email == "admin@example.com").first()

    if not user:
        # Create superuser
        user = User(
            email="admin@example.com",
            username="admin",
            hashed_password=get_password_hash("admin123"),
            is_active=True,
            is_superuser=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print("Superuser created successfully")
    else:
        print("Superuser already exists")
