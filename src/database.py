from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

if 'POSTGRES_DATABASE_URL' in os.environ:
    SQLALCHEMY_DATABASE_URL = os.environ.get("POSTGRES_DATABASE_URL")
else:    
    SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()