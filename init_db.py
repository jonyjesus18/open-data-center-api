"""
Script to initialize the database from CSV files
"""
# Load environment variables from .env file FIRST, before any database imports
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, environment variables must be set manually
    pass

import pandas as pd
import database
from database import DataCenter, DataCenterMetadata
from sqlalchemy import text
import ast
import os

def run_migrations():
    """Run Alembic migrations to bring database schema up to date"""
    print("Running database migrations...")
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("✓ Database migrations completed\n")
    except Exception as e:
        print(f"⚠ Error running migrations: {e}")
        raise

def init_database():
    """Initialize database from CSV files"""
    # Run Alembic migrations to create/update database schema
    run_migrations()
    
    # Create a session
    db = database.SessionLocal()
    
    try:
        # Clear existing data
        db.query(DataCenterMetadata).delete()
        db.query(DataCenter).delete()
        db.commit()
        
        # Load data centers table
        print("Loading data_centers_table.csv...")
        df_centers = pd.read_csv("data_centers_table.csv")
        print(f"Found columns: {list(df_centers.columns)}")
        
        for _, row in df_centers.iterrows():
            # Use 'id' column directly
            dc_id = row.get('id')
            if not dc_id or pd.isna(dc_id):
                print(f"⚠ Warning: Row missing ID, skipping: {row}")
                continue
                
            dc = DataCenter(
                id=str(dc_id),
                dc_name=row.get('dc_name') if pd.notna(row.get('dc_name')) else None,
                coordinates=str(row.get('coordinates')) if pd.notna(row.get('coordinates')) else None,
                date_added=str(row.get('date_added')) if pd.notna(row.get('date_added')) else None
            )
            db.add(dc)
        
        db.commit()
        print(f"Loaded {len(df_centers)} data centers")
        
        # Load metadata table
        print("Loading data_centers_metadata.csv...")
        df_metadata = pd.read_csv("data_centers_metadata.csv")
        print(f"Found columns: {list(df_metadata.columns)}")
        
        for _, row in df_metadata.iterrows():
            # Use 'id' column directly
            meta_id = row.get('id')
            if not meta_id or pd.isna(meta_id):
                print(f"⚠ Warning: Metadata row missing ID, skipping: {row}")
                continue
            
            # Handle coordinates - could be tuple string or regular string
            coordinates_value = None
            if pd.notna(row.get('coordinates')):
                coords = row.get('coordinates')
                # If it's already a string representation of tuple, keep it
                if isinstance(coords, str):
                    coordinates_value = coords
                else:
                    # Try to convert to string
                    coordinates_value = str(coords)
            
            # Handle installed_power_capacity_mw - try to convert to float safely
            power_capacity = None
            if pd.notna(row.get('installed_power_capacity_mw')):
                try:
                    power_capacity = float(row.get('installed_power_capacity_mw'))
                except (ValueError, TypeError):
                    power_capacity = None
            
            # Handle installed_area_sq_ft - try to convert to float safely
            area_sq_ft = None
            if pd.notna(row.get('installed_area_sq_ft')):
                try:
                    area_sq_ft = float(row.get('installed_area_sq_ft'))
                except (ValueError, TypeError):
                    area_sq_ft = None
            
            # Handle num_buildings - try to convert to int safely
            num_buildings = None
            if pd.notna(row.get('num_buildings')):
                try:
                    num_buildings = int(float(row.get('num_buildings')))  # Convert via float first in case it's stored as float
                except (ValueError, TypeError):
                    num_buildings = None
            
            # Handle sources - keep as string (could be JSON array string)
            sources_value = None
            if pd.notna(row.get('sources')):
                sources_value = str(row.get('sources'))
            
            metadata = DataCenterMetadata(
                id=str(meta_id),
                category=row.get('category') if pd.notna(row.get('category')) else None,
                development_stage=str(row.get('development_stage')) if pd.notna(row.get('development_stage')) else None,
                facility_status=row.get('facility_status') if pd.notna(row.get('facility_status')) else None,
                company_name=row.get('company_name') if pd.notna(row.get('company_name')) else None,
                city=row.get('city') if pd.notna(row.get('city')) else None,
                country=row.get('country') if pd.notna(row.get('country')) else None,
                coordinates=coordinates_value,
                overview=row.get('overview') if pd.notna(row.get('overview')) else None,
                installed_power_capacity_mw=power_capacity,
                installed_area_sq_ft=area_sq_ft,
                tenants=str(row.get('tenants')) if pd.notna(row.get('tenants')) else None,
                connectivity_providers=str(row.get('connectivity_providers')) if pd.notna(row.get('connectivity_providers')) else None,
                operation_start_date=str(row.get('operation_start_date')) if pd.notna(row.get('operation_start_date')) else None,
                update_date_time=str(row.get('update_date_time')) if pd.notna(row.get('update_date_time')) else None,
                sources=sources_value,
                num_buildings=num_buildings
            )
            db.add(metadata)
        
        db.commit()
        print(f"Loaded {len(df_metadata)} metadata records")
        print("Database initialization complete!")
        
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()

