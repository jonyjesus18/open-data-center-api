# Load environment variables from .env file FIRST
import os
from pathlib import Path

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

try:
    from dotenv import load_dotenv
    # Load .env file from the project root
    if ENV_FILE.exists():
        load_dotenv(dotenv_path=ENV_FILE)
        print(f"✓ Loaded environment variables from {ENV_FILE}")
    else:
        # Try loading from current directory as fallback
        load_dotenv()
        print("✓ Loaded environment variables (using default .env location)")
except ImportError:
    # If python-dotenv is not installed, environment variables must be set manually
    print("⚠ python-dotenv not installed. Using system environment variables only.")
except Exception as e:
    print(f"⚠ Warning: Could not load .env file: {e}")
    print("   Using system environment variables only.")

from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Support both DATABASE_URL and individual connection parameters
# Method 1: Use individual parameters (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME env vars)
# Note: Using DB_ prefix to avoid conflicts with system variables like USER
user = os.getenv("DB_USER") or os.getenv("USER")
password = os.getenv("DB_PASSWORD") or os.getenv("PASSWORD")
host = os.getenv("DB_HOST") or os.getenv("HOST")
port = os.getenv("DB_PORT") or os.getenv("PORT")
dbname = os.getenv("DB_NAME") or os.getenv("DBNAME")

# Method 2: Use DATABASE_URL connection string
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Debug: Show what we found (without exposing passwords)
if user or password or host or port or dbname:
    print(f"✓ Found individual DB parameters: DB_USER={'*' if user else 'None'}, DB_HOST={host or 'None'}, DB_PORT={port or 'None'}, DB_NAME={dbname or 'None'}")
if SQLALCHEMY_DATABASE_URL:
    # Mask password in connection string for logging
    masked_url = SQLALCHEMY_DATABASE_URL
    if "@" in masked_url:
        parts = masked_url.split("@")
        if ":" in parts[0]:
            user_part = parts[0].split(":")[0]
            masked_url = f"{user_part}:***@{parts[1]}"
    print(f"✓ Found DATABASE_URL: {masked_url}")

# Build connection URL from individual parameters if available
if user and password and host and port and dbname:
    # Construct connection string from individual parameters
    SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    print("✓ Using individual parameters to construct DATABASE_URL")
elif SQLALCHEMY_DATABASE_URL:
    # Use DATABASE_URL if provided
    print("✓ Using DATABASE_URL connection string")
else:
    raise ValueError(
        "Database connection configuration is required. "
        "Either set DATABASE_URL or set individual parameters (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)."
    )

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    raise ValueError(
        "SQLite is not supported. Please use Supabase (PostgreSQL)."
    )

if not SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
    raise ValueError(
        f"Unsupported database type. Expected PostgreSQL connection string starting with 'postgresql://', "
        f"but got: {SQLALCHEMY_DATABASE_URL[:50]}..."
    )

# For Supabase/PostgreSQL - use connection pooling
# Add SSL parameters if not already in the connection string
connect_args = {}
if "sslmode" not in SQLALCHEMY_DATABASE_URL and "ssl=" not in SQLALCHEMY_DATABASE_URL:
    # Supabase requires SSL connections
    connect_args = {"sslmode": "require"}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    connect_args=connect_args,
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DataCenter(Base):
    __tablename__ = "data_centers"

    id = Column(String, primary_key=True, index=True)
    dc_name = Column(String, nullable=True)
    coordinates = Column(String, nullable=True)
    date_added = Column(String, nullable=True)
    
    # Relationships
    data_center_metadata = relationship("DataCenterMetadata", back_populates="data_center", uselist=False)
    change_history = relationship("DataCenterChangeHistory", back_populates="data_center")


class DataCenterMetadata(Base):
    __tablename__ = "data_centers_metadata"

    id = Column(String, ForeignKey("data_centers.id", ondelete="CASCADE"), primary_key=True, index=True)
    category = Column(String, nullable=True)
    development_stage = Column(Text, nullable=True)
    facility_status = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)
    coordinates = Column(String, nullable=True)
    overview = Column(Text, nullable=True)
    installed_power_capacity_mw = Column(Float, nullable=True)
    installed_area_sq_ft = Column(Float, nullable=True)
    tenants = Column(Text, nullable=True)
    connectivity_providers = Column(Text, nullable=True)
    operation_start_date = Column(String, nullable=True)
    update_date_time = Column(String, nullable=True)
    sources = Column(Text, nullable=True)
    num_buildings = Column(Integer, nullable=True)
    
    # Relationships
    data_center = relationship("DataCenter", back_populates="data_center_metadata")


class DataCenterChangeHistory(Base):
    __tablename__ = "data_center_change_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    data_center_id = Column(String, ForeignKey("data_centers.id"), nullable=False, index=True)
    field_name = Column(String, nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by_email = Column(String, nullable=False)
    changed_by_name = Column(String, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="approved", nullable=False)  # approved, pending, rejected
    
    # Relationships
    data_center = relationship("DataCenter", back_populates="change_history")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    email = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=True)
    company = Column(String, nullable=True)
    date_of_birth = Column(String, nullable=True)
    role = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ApiKey(Base):
    __tablename__ = "api_keys"

    key = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)  # Description/name for the key
    is_active = Column(String, default="active", nullable=False)  # active, inactive
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used = Column(DateTime, nullable=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

