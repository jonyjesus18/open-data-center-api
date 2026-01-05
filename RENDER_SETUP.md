# Render Deployment Setup

## Option 1: Use Root Directory (Recommended)

In your Render dashboard:
1. Go to your service settings
2. Under "Build & Deploy" → "Root Directory"
3. Set it to: `.` (dot) or leave it empty
4. Save changes

This tells Render to use the root directory instead of `src`.

## Option 2: Use src Directory

If you prefer to use the `src` convention, you can:

1. **Move your Python files to `src/`:**
   ```bash
   mkdir -p src
   mv main.py database.py schemas.py init_db.py src/
   mv alembic src/
   ```

2. **Update imports** - All imports will need to be relative or you'll need to add `src` to Python path

3. **Update Render settings:**
   - Root Directory: `src`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Recommended: Use Root Directory

Since your project structure is already set up with files in the root, it's easier to configure Render to use the root directory.

### Render Dashboard Settings:

- **Root Directory**: `.` (or leave empty)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment**: `Python 3`

### Environment Variables in Render:

Set these in Render's Environment Variables section:

```
DB_USER=postgres.pvyrexbrwybiphajgiei
DB_PASSWORD=your-password
DB_HOST=aws-1-eu-west-2.pooler.supabase.com
DB_PORT=6543
DB_NAME=postgres
ALLOWED_ORIGINS=https://open-data-center.vercel.app
ADMIN_API_KEY=your-admin-key
ENVIRONMENT=production
```

## Using render.yaml (Alternative)

If you're using `render.yaml`, the configuration is already set up. Just make sure:
- Your `render.yaml` is in the root directory
- Render is connected to your GitHub repo
- Environment variables are set in Render dashboard

