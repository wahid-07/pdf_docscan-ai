from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()     # .env file load karo


DATABASE_URL = os.getenv("DATABASE_URL")        # Database URL ko  .env file  se lo

# SQLite directory ensure karo agar SQLite use ho raha hai
if DATABASE_URL and DATABASE_URL.startswith("sqlite:///"):
    db_path = Path(DATABASE_URL.replace("sqlite:///", ""))
    db_path.parent.mkdir(parents=True, exist_ok=True)

# Engine banao — ye actual DB connection hai
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)
# Session factory — har DB operation ke liye use hoga
SessionLocal = sessionmaker(bind=engine)

# Base class — models isse inherit karenge
Base = declarative_base()


def ensure_pdf_master_columns():
    try:
        inspector = inspect(engine)
        if "pdf_master" not in inspector.get_table_names():
            return

        columns = {column["name"] for column in inspector.get_columns("pdf_master")}
        if "file_hash" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE pdf_master ADD COLUMN file_hash VARCHAR"))
        if "progress" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE pdf_master ADD COLUMN progress INTEGER DEFAULT 0"))
        if "processing_message" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE pdf_master ADD COLUMN processing_message VARCHAR"))
    except Exception:
        pass


def ensure_user_columns():
    try:
        inspector = inspect(engine)
        if "users" not in inspector.get_table_names():
            return

        columns = {column["name"] for column in inspector.get_columns("users")}
        if "token_version" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE users ADD COLUMN token_version INTEGER DEFAULT 0"))
    except Exception:
        pass


ensure_pdf_master_columns()
ensure_user_columns()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()