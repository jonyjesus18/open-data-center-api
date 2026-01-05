# Open Data Center API

FastAPI backend for the Open Data Center platform.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`:
   ```
   DB_USER=postgres.pvyrexbrwybiphajgiei
   DB_PASSWORD=your-password
   DB_HOST=aws-1-eu-west-2.pooler.supabase.com
   DB_PORT=6543
   DB_NAME=postgres
   ALLOWED_ORIGINS=https://your-frontend.vercel.app
   ADMIN_API_KEY=your-admin-key
   ENVIRONMENT=production
   ```

   Alternatively, use `DATABASE_URL` instead of individual DB parameters.

3. Initialize database:
   ```bash
   python db/init_db.py
   ```

4. Run the API:
   ```bash
   # From project root (recommended)
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or use the run script
   ./run.sh
   
   # Or from src directory
   cd src && uvicorn main:app --reload
   ```

## Deployment

### Render

The project is configured for Render deployment:

- Root Directory: `src`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Set environment variables in Render dashboard:
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME` (or `DATABASE_URL`)
- `ALLOWED_ORIGINS`
- `ADMIN_API_KEY`
- `ENVIRONMENT=production`

### Other Platforms

For other platforms, ensure:
- Root directory is set to `src`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- All environment variables are set

## Project Structure

```
.
├── src/              # API source code
│   ├── main.py      # FastAPI application
│   ├── database.py  # Database models and connection
│   └── schemas.py   # Pydantic schemas
├── db/              # Database initialization scripts
│   ├── init_db.py   # Database initialization
│   └── *.csv        # Data files
├── alembic/         # Database migrations
├── requirements.txt # Python dependencies
└── render.yaml      # Render deployment config
```

## API Documentation

Once running, access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
