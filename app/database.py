from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pathlib import Path

# Use a database file located at the project root so the path is
# consistent regardless of the current working directory when running.
DB_PATH = Path(__file__).resolve().parent.parent / "cyber_ai.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()