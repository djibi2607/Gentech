from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError ("Database url not found")

engine = create_engine (DATABASE_URL)

SessionLocal = sessionmaker(autoflush= False, autocommit = False, bind = engine)

def get_db():
    db = SessionLocal()

    try: 
        yield db
    
    finally:
        db.close()

base = declarative_base()
