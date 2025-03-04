import os
from sqlalchemy import create_engine, Column, Integer, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SQLAlchemy database URL from environment variable
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a configured "SessionLocal" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for models to inherit from
Base = declarative_base()

# Define the Prediction model
class Prediction(Base):
    __tablename__ = "past_predictions"

    id = Column(Integer, primary_key=True, index=True)
    features = Column(JSON, nullable=False)
    insertion_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    prediction = Column(Float, nullable=False)

# Create the database tables
Base.metadata.create_all(bind=engine)
