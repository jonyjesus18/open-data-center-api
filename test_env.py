#!/usr/bin/env python3
"""Test script to verify environment variables are loaded correctly"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory where this file is located
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

print("=" * 60)
print("Environment Variable Test")
print("=" * 60)

# Load .env file
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
    print(f"✓ Found .env file at: {ENV_FILE}")
else:
    load_dotenv()
    print(f"⚠ .env file not found at {ENV_FILE}, trying default location...")

print("\nChecking environment variables:")
print("-" * 60)

# Check DATABASE_URL
database_url = os.getenv("DATABASE_URL")
if database_url:
    # Mask password for display
    if "@" in database_url:
        parts = database_url.split("@")
        if ":" in parts[0]:
            user_part = parts[0].split(":")[0]
            masked_url = f"{user_part}:***@{parts[1]}"
        else:
            masked_url = f"***@{parts[1]}"
    else:
        masked_url = database_url
    print(f"✓ DATABASE_URL: {masked_url}")
else:
    print("✗ DATABASE_URL: Not set")

# Check individual parameters (prefer DB_ prefix to avoid system variable conflicts)
user = os.getenv("DB_USER") or os.getenv("USER")
password = os.getenv("DB_PASSWORD") or os.getenv("PASSWORD")
host = os.getenv("DB_HOST") or os.getenv("HOST")
port = os.getenv("DB_PORT") or os.getenv("PORT")
dbname = os.getenv("DB_NAME") or os.getenv("DBNAME")

print(f"\nIndividual parameters:")
print(f"  DB_USER:     {user or '✗ Not set'}")
print(f"  DB_PASSWORD: {'✓ Set' if password else '✗ Not set'}")
print(f"  DB_HOST:     {host or '✗ Not set'}")
print(f"  DB_PORT:     {port or '✗ Not set'}")
print(f"  DB_NAME:     {dbname or '✗ Not set'}")
print(f"\n  Note: System USER={os.getenv('USER', 'N/A')} (this may conflict!)")

# Check other required vars
print(f"\nOther environment variables:")
print(f"  ALLOWED_ORIGINS: {os.getenv('ALLOWED_ORIGINS', '✗ Not set')}")
print(f"  ADMIN_API_KEY:   {'✓ Set' if os.getenv('ADMIN_API_KEY') else '✗ Not set'}")
print(f"  ENVIRONMENT:     {os.getenv('ENVIRONMENT', 'development (default)')}")

print("\n" + "=" * 60)

# Determine which connection method will be used
if user and password and host and port and dbname:
    print("✓ Will use individual parameters to construct connection string")
elif database_url:
    print("✓ Will use DATABASE_URL connection string")
else:
    print("✗ ERROR: No database connection configuration found!")
    print("   Set either DATABASE_URL or all of: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME")
    print("   (Using DB_ prefix avoids conflicts with system variables like USER)")

print("=" * 60)

