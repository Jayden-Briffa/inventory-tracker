from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from migrations import init_db

DATABASE_URL = "sqlite:///./db.sqlite"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()