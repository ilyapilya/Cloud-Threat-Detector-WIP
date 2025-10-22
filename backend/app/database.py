import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load .env from project root (adjust if you keep .env in backend/)
project_root = Path(__file__).resolve().parents[2]
load_dotenv(project_root / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/cloudscanner")

# sync engine for simple FastAPI integration (swap to async + asyncpg if needed)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()