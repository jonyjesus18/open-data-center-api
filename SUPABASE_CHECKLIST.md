# Supabase Connection Setup Checklist

## ✅ Required Steps on Supabase Dashboard

### 1. Check Project Status
- [ ] Go to https://app.supabase.com
- [ ] Select your project
- [ ] **Check if project is PAUSED** (common on free tier after inactivity)
- [ ] If paused, click "Restore Project" and wait 2-3 minutes

### 2. Check for IP Bans
- [ ] Go to **Settings** → **Database**
- [ ] Scroll to **Connection Pooling** section
- [ ] Check if there's an "Unban IP" option
- [ ] If your IP is banned, click "Unban IP"
- [ ] Wait a few minutes for the ban to clear

### 3. Get the Correct Connection String
- [ ] Go to **Settings** → **Database**
- [ ] Scroll to **Connection Pooling** section
- [ ] **Use "Transaction Mode"** (recommended) instead of "Session Mode"
- [ ] Copy the connection string - it should look like:
  ```
  postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
  ```
- [ ] **Important**: Use the connection string directly from Supabase dashboard, don't construct it manually

### 4. Verify Connection Pooling is Enabled
- [ ] Connection pooling should be enabled by default on all Supabase projects
- [ ] If you don't see a "Connection Pooling" section, your project might be on a plan that doesn't support it
- [ ] In that case, you'll need to use the direct connection (port 5432) and ensure your IP is whitelisted

### 5. Restart Database (if needed)
- [ ] Go to **Settings** → **Database**
- [ ] Scroll to the bottom
- [ ] Click **"Restart Database"** if other steps don't work
- [ ] Wait 1-2 minutes for restart to complete

## 🔍 Troubleshooting Steps

### If Connection Pooling Doesn't Work:
1. Try the **direct connection** (port 5432) from **Settings** → **Database** → **Connection string** → **URI** tab
2. Make sure your IP is whitelisted (if required by your plan)
3. Check if your network supports IPv6 (Supabase direct connections use IPv6 by default)

### If You Get "Connection Refused":
1. **Most Common**: Project is paused - restore it
2. **Second Most Common**: IP is banned - unban it
3. Check firewall/network settings
4. Try restarting the database

### Connection String Formats:

**Direct Connection (port 5432):**
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

**Connection Pooling - Transaction Mode (port 6543) - RECOMMENDED:**
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

**Connection Pooling - Session Mode (port 6543):**
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres?pgbouncer=true
```

## 📝 Next Steps After Supabase Setup

1. Copy the connection string from Supabase dashboard
2. Update your `.env` file with the exact connection string
3. Make sure password is URL-encoded if it contains special characters
4. Run `python init_db.py` again

