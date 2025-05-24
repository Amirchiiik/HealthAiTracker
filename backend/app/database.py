import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database

# Database URL - using SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./health_tracker.db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

# Base class for models
Base = declarative_base()

# Async database connection
database = Database(DATABASE_URL)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    # Import all models to ensure they're registered with Base
    from app.models import User, HealthAnalysis, ChatInteraction, ChatMessage
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

async def connect_db():
    """Connect to the database"""
    try:
        create_tables()
        await database.connect()
        print("🔗 Database connected successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

async def disconnect_db():
    """Disconnect from the database"""
    try:
        await database.disconnect()
        print("📤 Database connections closed")
    except Exception as e:
        print(f"❌ Database disconnection error: {e}") 