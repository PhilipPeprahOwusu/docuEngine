"""Activate demo user account"""
import sys
sys.path.insert(0, '/app')

from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Use raw SQL to avoid model import issues
    result = db.execute(
        text("UPDATE users SET is_active = true WHERE email = 'demo@example.com' RETURNING email, is_active, role")
    )
    db.commit()

    row = result.first()
    if row:
        print(f"✅ Activated user: {row[0]}")
        print(f"   Active: {row[1]}")
        print(f"   Role: {row[2]}")
    else:
        print("❌ Demo user not found")

except Exception as e:
    print(f"❌ Error: {str(e)}")
    db.rollback()
finally:
    db.close()
