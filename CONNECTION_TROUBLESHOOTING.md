# Supabase Connection Troubleshooting

## "Connection Refused" Error

If you're getting a "connection refused" error, try these solutions in order:

### Solution 1: Use Connection Pooling URL (Recommended)

The direct connection (port 5432) may require IP whitelisting. Use the connection pooling URL instead:

1. Go to your Supabase Dashboard: https://app.supabase.com
2. Select your project
3. Go to **Settings** → **Database**
4. Scroll to **Connection Pooling** section
5. Copy the **Session mode** connection string
6. It will look like:
   ```
   postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
   ```
7. Update your `.env` file with this connection string

### Solution 2: Whitelist Your IP Address

If you must use the direct connection (port 5432):

1. Go to Supabase Dashboard → **Settings** → **Database**
2. Find **Connection string** section
3. Check if there's an IP whitelist option
4. Add your current IP address
5. You can find your IP at: https://whatismyipaddress.com/

### Solution 3: Check Project Status

1. Verify your Supabase project is **active** (not paused)
2. Check your Supabase project dashboard for any warnings
3. Free tier projects may pause after inactivity

### Solution 4: Verify Connection String Format

Your connection string should be in one of these formats:

**Direct Connection:**
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Connection Pooling (Recommended):**
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Important Notes:**
- Replace `[PASSWORD]` with your actual database password
- Replace `[PROJECT-REF]` with your project reference ID
- Replace `[REGION]` with your region (e.g., `us-east-1`)
- If your password contains special characters, URL-encode them:
  - `@` → `%40`
  - `#` → `%23`
  - `%` → `%25`
  - `&` → `%26`

### Solution 5: Test Connection Manually

You can test your connection string with `psql`:

```bash
# Install psql if needed (macOS)
brew install postgresql

# Test connection
psql "postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres"
```

Or use Python to test:

```python
import psycopg2
import os

conn_string = os.getenv("DATABASE_URL")
try:
    conn = psycopg2.connect(conn_string)
    print("✅ Connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
```

### Solution 6: Check Network/Firewall

- Ensure your network allows outbound connections on ports 5432 or 6543
- If you're on a corporate network, check with IT about firewall rules
- Try from a different network (e.g., mobile hotspot) to rule out network issues

## Quick Fix Checklist

- [ ] Using connection pooling URL (port 6543) instead of direct connection (port 5432)
- [ ] Password is correctly URL-encoded if it contains special characters
- [ ] Supabase project is active (not paused)
- [ ] Connection string format is correct
- [ ] Network/firewall allows connections to Supabase

## Still Having Issues?

1. Check Supabase status page: https://status.supabase.com/
2. Review Supabase logs in your project dashboard
3. Try creating a new connection string from Supabase dashboard
4. Contact Supabase support if the issue persists

