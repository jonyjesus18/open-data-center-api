# Supabase Database Setup Guide

**Important**: This application requires Supabase (PostgreSQL). SQLite is not supported. The application will fail to start if DATABASE_URL is not set to a PostgreSQL connection string.

## Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com) and sign up/login
2. Click "New Project"
3. Fill in your project details:
   - **Name**: Your project name (e.g., "open-data-center")
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the closest region to your users
4. Wait for the project to be created (takes ~2 minutes)

## Step 2: Get Your Database Connection String

1. In your Supabase project dashboard, go to **Settings** → **Database**
2. Scroll down to **Connection string** section
3. Select **URI** tab
4. Copy the connection string - it will look like:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
   ```
5. Replace `[YOUR-PASSWORD]` with the password you set when creating the project

## Step 3: Configure Your Environment

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update the `.env` file with your Supabase connection string:
   ```env
   DATABASE_URL=postgresql://postgres:your-password@db.xxxxx.supabase.co:5432/postgres
   ```

   **Important**: Make sure to URL-encode your password if it contains special characters:
   - `@` becomes `%40`
   - `#` becomes `%23`
   - `%` becomes `%25`
   - etc.

3. Update other environment variables as needed:
   ```env
   ALLOWED_ORIGINS=http://localhost:5173,https://yourdomain.com
   ADMIN_API_KEY=your-secure-api-key
   ENVIRONMENT=production
   ```

## Step 4: Install Dependencies

Make sure you have the PostgreSQL driver installed:

```bash
pip install -r requirements.txt
```

This will install `psycopg2-binary` which is required for PostgreSQL connections.

## Step 5: Initialize the Database

1. **Create tables** (this will create all tables in Supabase):
   ```bash
   python -c "from database import init_db; init_db()"
   ```

2. **Load your data** from CSV files:
   ```bash
   python init_db.py
   ```

   This will:
   - Run migrations to add any missing columns
   - Create all tables
   - Load data from `data_centers_table.csv` and `data_centers_metadata.csv`

## Step 6: Verify Connection

Test your connection by running your API:

```bash
uvicorn main:app --reload
```

Check the logs to ensure there are no connection errors.

## Connection Pooling (Optional but Recommended)

For better performance in production, Supabase offers connection pooling:

1. In Supabase dashboard, go to **Settings** → **Database**
2. Find the **Connection pooling** section
3. Use the **Session mode** connection string for your application
4. It will look like:
   ```
   postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```

## Troubleshooting

### Connection Errors

- **"password authentication failed"**: 
  - Double-check your password in the connection string
  - Make sure special characters in your password are URL-encoded
  - Verify you're using the correct password from your Supabase project settings

- **"connection refused"**: 
  - **Most Common Cause**: Your IP address is not whitelisted in Supabase
    - Go to Supabase Dashboard → Settings → Database → Connection Pooling
    - Check if your IP needs to be whitelisted (some Supabase plans require this)
    - Try using the **Connection Pooling URL** instead of the direct connection URL
    - Connection Pooling URL format: `postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres`
  - Verify your Supabase project is active (not paused)
  - Check if your network/firewall is blocking port 5432 or 6543
  - Try using port 6543 (connection pooling) instead of 5432 (direct connection)

- **"SSL required"**: 
  - Supabase requires SSL connections
  - The code automatically adds `sslmode=require` if not present
  - If you still get SSL errors, manually add `?sslmode=require` to the end of your DATABASE_URL

### Special Characters in Password

If your password contains special characters, URL-encode them:
- Use Python to encode: `python -c "import urllib.parse; print(urllib.parse.quote('your-password'))"`

### Migration Issues

If you get errors about existing columns:
- The migration script will skip columns that already exist
- This is safe to run multiple times

## Security Best Practices

1. **Never commit your `.env` file** - it contains sensitive credentials
2. **Use environment variables** in production (not `.env` files)
3. **Rotate your database password** regularly
4. **Use connection pooling** for production workloads
5. **Enable Row Level Security (RLS)** in Supabase if you need additional security

## Next Steps

Once your database is set up:
- Your API will automatically use the Supabase database
- All existing functionality will work the same way
- You can monitor your database in the Supabase dashboard
- Consider setting up database backups in Supabase settings

