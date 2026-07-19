import os
from dotenv import load_dotenv
from database.connection import SessionLocal
from models.table_model import User
from auth.security import hash_password

load_dotenv()

db = SessionLocal()

admin = User(
    full_name="Wahid Naseem[Admin]",
    email=os.getenv("ADMIN_EMAIL"),
    password_hash=hash_password(os.getenv("ADMIN_PASSWORD")),
    role="admin",
    is_active=True
)

db.add(admin)
db.commit()
db.close()

print("Admin created!")