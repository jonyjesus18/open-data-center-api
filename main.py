from fastapi import FastAPI, Depends, HTTPException, Header, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import List, Optional
import database
import schemas
from database import DataCenter, DataCenterMetadata, DataCenterChangeHistory, UserProfile, ApiKey
from datetime import datetime
import os
import logging

# Load environment variables from .env file
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
    else:
        # Try loading from current directory as fallback
        load_dotenv()
except ImportError:
    # If python-dotenv is not installed, environment variables must be set manually
    pass
except Exception:
    # Silently fail if .env file doesn't exist
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO if os.getenv("ENVIRONMENT", "development") == "production" else logging.DEBUG
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Center API", version="1.0.0")

# Validate database connection on startup
@app.on_event("startup")
async def startup_event():
    """Validate database connection on startup"""
    import database
    try:
        # Try to connect to the database
        with database.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Successfully connected to Supabase PostgreSQL database")
    except Exception as e:
        logger.error(f"✗ Failed to connect to database: {e}")
        # Check which connection method is being used
        import database
        has_db_url = bool(os.getenv("DATABASE_URL"))
        has_individual = bool(
            os.getenv("DB_USER") or os.getenv("USER")
        ) and bool(
            os.getenv("DB_PASSWORD") or os.getenv("PASSWORD")
        ) and bool(
            os.getenv("DB_HOST") or os.getenv("HOST")
        )
        
        if has_individual and not has_db_url:
            error_msg = (
                "Cannot connect to Supabase database. "
                "Please check your database connection parameters (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME). "
                f"Error: {str(e)}"
            )
        elif has_db_url:
            error_msg = (
                "Cannot connect to Supabase database. "
                "Please check your DATABASE_URL environment variable. "
                f"Error: {str(e)}"
            )
        else:
            error_msg = (
                "Cannot connect to Supabase database. "
                "Please set either DATABASE_URL or individual parameters (DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME). "
                f"Error: {str(e)}"
            )
        raise RuntimeError(error_msg)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error" if os.getenv("ENVIRONMENT") == "production" else str(exc)
        }
    )

# Configure CORS from environment variables
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# API Key Security
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header), db: Session = Depends(get_db)):
    """Verify API key is valid and active"""
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Please provide X-API-Key header."
        )
    
    # Check if key exists and is active
    db_key = db.query(ApiKey).filter(ApiKey.key == api_key).first()
    if not db_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    if db_key.is_active != "active":
        raise HTTPException(
            status_code=401,
            detail="API key is inactive"
        )
    
    # Update last used timestamp
    db_key.last_used = datetime.utcnow()
    db.commit()
    
    return api_key


# Data Center CRUD endpoints
@app.get("/")
def root():
    return {"message": "Data Center API - Use /docs for API documentation"}


@app.get("/api/datacenters", response_model=List[schemas.DataCenter])
def get_data_centers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all data centers with pagination"""
    try:
        # Allow fetching all data centers - increase max limit significantly
        # For very large datasets, consider implementing cursor-based pagination
        limit = min(limit, 50000)  # Increased from 1000 to 50000
        data_centers = db.query(DataCenter).offset(skip).limit(limit).all()
        return data_centers
    except SQLAlchemyError as e:
        logger.error(f"Database error in get_data_centers: {e}")
        raise HTTPException(status_code=500, detail="Database error")


@app.get("/api/datacenters/count")
def get_data_centers_count(db: Session = Depends(get_db)):
    """Get total count of data centers"""
    count = db.query(DataCenter).count()
    return {"count": count}


@app.get("/api/datacenters/{id}", response_model=schemas.DataCenter)
def get_data_center(id: str, db: Session = Depends(get_db)):
    """Get a specific data center by id"""
    data_center = db.query(DataCenter).filter(DataCenter.id == id).first()
    if data_center is None:
        raise HTTPException(status_code=404, detail="Data center not found")
    return data_center


@app.post("/api/datacenters", response_model=schemas.DataCenter, status_code=201)
def create_data_center(
    data_center: schemas.DataCenterCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new data center"""
    db_data_center = DataCenter(**data_center.model_dump())
    db.add(db_data_center)
    db.commit()
    db.refresh(db_data_center)
    return db_data_center


@app.put("/api/datacenters/{id}", response_model=schemas.DataCenter)
def update_data_center(
    id: str, 
    data_center: schemas.DataCenterUpdate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update an existing data center"""
    db_data_center = db.query(DataCenter).filter(DataCenter.id == id).first()
    if db_data_center is None:
        raise HTTPException(status_code=404, detail="Data center not found")
    
    update_data = data_center.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_data_center, field, value)
    
    db.commit()
    db.refresh(db_data_center)
    return db_data_center


@app.delete("/api/datacenters/{id}", status_code=204)
def delete_data_center(
    id: str, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete a data center"""
    db_data_center = db.query(DataCenter).filter(DataCenter.id == id).first()
    if db_data_center is None:
        raise HTTPException(status_code=404, detail="Data center not found")
    
    db.delete(db_data_center)
    db.commit()
    return None


# Data Center Metadata CRUD endpoints
@app.get("/api/datacenters/{id}/metadata", response_model=schemas.DataCenterMetadata)
def get_data_center_metadata(id: str, db: Session = Depends(get_db)):
    """Get metadata for a specific data center"""
    metadata = db.query(DataCenterMetadata).filter(DataCenterMetadata.id == id).first()
    if metadata is None:
        raise HTTPException(status_code=404, detail="Data center metadata not found")
    return metadata


@app.get("/api/metadata", response_model=List[schemas.DataCenterMetadata])
def get_all_metadata(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all data center metadata with pagination"""
    # Allow fetching all metadata - increase max limit significantly
    limit = min(limit, 50000)  # Increased to match data centers endpoint
    metadata = db.query(DataCenterMetadata).offset(skip).limit(limit).all()
    return metadata


@app.post("/api/metadata", response_model=schemas.DataCenterMetadata, status_code=201)
def create_data_center_metadata(
    metadata: schemas.DataCenterMetadataCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create new data center metadata"""
    db_metadata = DataCenterMetadata(**metadata.model_dump())
    db.add(db_metadata)
    db.commit()
    db.refresh(db_metadata)
    return db_metadata


@app.put("/api/metadata/{id}", response_model=schemas.DataCenterMetadata)
def update_data_center_metadata(
    id: str, 
    metadata: schemas.DataCenterMetadataUpdate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update existing data center metadata"""
    db_metadata = db.query(DataCenterMetadata).filter(DataCenterMetadata.id == id).first()
    if db_metadata is None:
        raise HTTPException(status_code=404, detail="Data center metadata not found")
    
    update_data = metadata.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_metadata, field, value)
    
    db.commit()
    db.refresh(db_metadata)
    return db_metadata


@app.delete("/api/metadata/{id}", status_code=204)
def delete_data_center_metadata(
    id: str, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Delete data center metadata"""
    db_metadata = db.query(DataCenterMetadata).filter(DataCenterMetadata.id == id).first()
    if db_metadata is None:
        raise HTTPException(status_code=404, detail="Data center metadata not found")
    
    db.delete(db_metadata)
    db.commit()
    return None


# Combined endpoint to get data center with metadata
@app.get("/api/datacenters/{id}/full", response_model=schemas.DataCenterFull)
def get_data_center_full(id: str, db: Session = Depends(get_db)):
    """Get a data center with its metadata"""
    data_center = db.query(DataCenter).filter(DataCenter.id == id).first()
    if data_center is None:
        raise HTTPException(status_code=404, detail="Data center not found")
    
    metadata = db.query(DataCenterMetadata).filter(DataCenterMetadata.id == id).first()
    
    result = schemas.DataCenterFull(
        id=data_center.id,
        dc_name=data_center.dc_name,
        coordinates=data_center.coordinates,
        date_added=data_center.date_added,
        metadata=schemas.DataCenterMetadata.model_validate(metadata) if metadata else None
    )
    return result


# Data Center Change History endpoints
@app.get("/api/datacenters/{id}/history", response_model=List[schemas.DataCenterChangeHistory])
def get_data_center_history(id: str, db: Session = Depends(get_db)):
    """Get change history for a specific data center"""
    history = db.query(DataCenterChangeHistory).filter(
        DataCenterChangeHistory.data_center_id == id
    ).order_by(DataCenterChangeHistory.changed_at.desc()).all()
    return history


@app.get("/api/changes/recent", response_model=List[schemas.DataCenterChangeHistory])
def get_recent_changes(limit: int = 20, db: Session = Depends(get_db)):
    """Get recent changes across all data centers"""
    changes = db.query(DataCenterChangeHistory).order_by(
        DataCenterChangeHistory.changed_at.desc()
    ).limit(limit).all()
    return changes


@app.post("/api/datacenters/{id}/history", response_model=List[schemas.DataCenterChangeHistory], status_code=201)
def create_change_history(
    id: str, 
    changes: List[schemas.DataCenterChangeHistoryCreate], 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create change history entries for a data center"""
    created_entries = []
    for change in changes:
        change_data = change.model_dump()
        change_data["data_center_id"] = id
        db_history = DataCenterChangeHistory(**change_data)
        db.add(db_history)
        created_entries.append(db_history)
    db.commit()
    for entry in created_entries:
        db.refresh(entry)
    return created_entries


# User Profile endpoints
@app.get("/api/users/{email}/profile", response_model=schemas.UserProfile)
def get_user_profile(email: str, db: Session = Depends(get_db)):
    """Get user profile by email, returns default profile if not found"""
    profile = db.query(UserProfile).filter(UserProfile.email == email).first()
    if profile is None:
        # Return a default profile instead of 404
        return schemas.UserProfile(
            email=email,
            username=None,
            company=None,
            date_of_birth=None,
            role=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    return profile


@app.post("/api/users/profile", response_model=schemas.UserProfile, status_code=201)
def create_user_profile(
    profile: schemas.UserProfileCreate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new user profile"""
    db_profile = UserProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


@app.put("/api/users/{email}/profile", response_model=schemas.UserProfile)
def update_user_profile(
    email: str, 
    profile: schemas.UserProfileUpdate, 
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Update user profile"""
    db_profile = db.query(UserProfile).filter(UserProfile.email == email).first()
    if db_profile is None:
        # Create if doesn't exist
        db_profile = UserProfile(email=email, **profile.model_dump(exclude_unset=True))
        db.add(db_profile)
    else:
        update_data = profile.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        db_profile.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_profile)
    return db_profile


# Admin API Key - protect admin endpoints
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

def verify_admin_key(admin_key: str = Header(None, alias="X-Admin-Key")):
    """Verify admin API key for protected endpoints"""
    if not ADMIN_API_KEY:
        # In development, allow if no admin key is set
        if os.getenv("ENVIRONMENT", "development") == "development":
            return True
        raise HTTPException(
            status_code=500,
            detail="Admin API key not configured. Set ADMIN_API_KEY environment variable."
        )
    
    if not admin_key or admin_key != ADMIN_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing admin API key"
        )
    return True


# API Key Management endpoints
@app.post("/api/admin/keys", status_code=201)
def create_api_key(
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """Create a new API key (protected - requires admin key)"""
    import secrets
    api_key = secrets.token_urlsafe(32)  # Generate a secure random key
    
    db_key = ApiKey(key=api_key, name=name or "Generated key", is_active="active")
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    
    return {
        "key": api_key,
        "name": db_key.name,
        "created_at": db_key.created_at,
        "message": "⚠️ IMPORTANT: Save this key now. It won't be shown again!"
    }


@app.get("/api/admin/keys")
def list_api_keys(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin_key)
):
    """List all API keys (protected - requires admin key)"""
    keys = db.query(ApiKey).all()
    return [
        {
            "key": k.key[:8] + "..." + k.key[-4:] if len(k.key) > 12 else "***",  # Mask key
            "name": k.name,
            "is_active": k.is_active,
            "created_at": k.created_at,
            "last_used": k.last_used
        }
        for k in keys
    ]

