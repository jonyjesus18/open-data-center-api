# Deployment Guide

This guide will help you deploy the Open Data Center API to production.

## Prerequisites

- Python 3.8+
- PostgreSQL (recommended for production) or SQLite (development only)
- Domain name with SSL certificate (for HTTPS)

## Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - Database connection string
- `ALLOWED_ORIGINS` - Comma-separated list of allowed frontend origins
- `ADMIN_API_KEY` - Secure key for admin endpoints (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `ENVIRONMENT` - Set to `production` for production

## Database Setup

### Option 1: PostgreSQL (Recommended for Production)

1. Install PostgreSQL
2. Create database:
   ```sql
   CREATE DATABASE datacenter_db;
   CREATE USER datacenter_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE datacenter_db TO datacenter_user;
   ```

3. Update `.env`:
   ```
   DATABASE_URL=postgresql://datacenter_user:your_password@localhost:5432/datacenter_db
   ```

4. Run migrations:
   ```bash
   python init_db.py
   ```

### Option 2: SQLite (Development Only)

SQLite is fine for development but not recommended for production due to:
- Limited concurrency
- No network access
- File-based (harder to scale)

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py
```

## Running the Server

### Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Or use a process manager like `systemd` or `supervisord`.

## Security Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong `ADMIN_API_KEY` (never commit to git)
- [ ] Configure `ALLOWED_ORIGINS` with your production domain
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS (use reverse proxy like Nginx)
- [ ] Set up firewall rules
- [ ] Regular database backups
- [ ] Monitor logs for errors

## Reverse Proxy (Nginx Example)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## API Key Management

1. Generate admin key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Set in `.env`:
   ```
   ADMIN_API_KEY=your-generated-key-here
   ```

3. Create API keys for your frontend:
   ```bash
   curl -X POST "http://localhost:8000/api/admin/keys?name=Frontend" \
     -H "X-Admin-Key: your-admin-key"
   ```

## Monitoring

- Check logs regularly
- Monitor database size and performance
- Set up alerts for errors
- Track API usage

## Backup Strategy

1. **Database backups** (daily):
   ```bash
   pg_dump datacenter_db > backup_$(date +%Y%m%d).sql
   ```

2. **Store backups** off-server (S3, etc.)

3. **Test restore** process regularly

