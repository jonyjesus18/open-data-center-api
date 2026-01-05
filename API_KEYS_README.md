# API Keys Authentication

A simple API key authentication system has been implemented to protect write operations (POST, PUT, DELETE).

## Setup

1. **Run the migration to create the API keys table:**
   ```bash
   python migrate_add_api_keys.py
   ```

2. **Create your first API key:**
   ```bash
   python create_api_key.py "My Frontend App"
   ```
   
   Or use the API endpoint:
   ```bash
   curl -X POST "http://localhost:8000/api/admin/keys?name=My%20Frontend%20App"
   ```

3. **Save the API key** - it will only be shown once!

4. **Add the API key to your frontend `.env` file:**
   ```env
   VITE_API_KEY=your-api-key-here
   ```

## How It Works

- **Read operations (GET)** are **public** - no API key required
- **Write operations (POST, PUT, DELETE)** require an API key in the `X-API-Key` header
- The frontend automatically includes the API key from `VITE_API_KEY` environment variable

## Protected Endpoints

All write operations require API key:
- `POST /api/datacenters` - Create data center
- `PUT /api/datacenters/{public_id}` - Update data center
- `DELETE /api/datacenters/{public_id}` - Delete data center
- `POST /api/metadata` - Create metadata
- `PUT /api/metadata/{public_id}` - Update metadata
- `DELETE /api/metadata/{public_id}` - Delete metadata
- `POST /api/datacenters/{public_id}/history` - Create change history
- `POST /api/users/profile` - Create user profile
- `PUT /api/users/{email}/profile` - Update user profile

## Public Endpoints (No API Key Required)

- `GET /api/datacenters` - List all data centers
- `GET /api/datacenters/{public_id}` - Get specific data center
- `GET /api/datacenters/count` - Get count
- `GET /api/metadata` - List all metadata
- `GET /api/datacenters/{public_id}/metadata` - Get metadata
- `GET /api/datacenters/{public_id}/history` - Get change history
- `GET /api/users/{email}/profile` - Get user profile

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit API keys to version control** - Use environment variables
2. **Rotate keys regularly** - If a key is compromised, deactivate it and create a new one
3. **Limit key access** - Only share keys with trusted applications
4. **Monitor usage** - Check `last_used` timestamp in the database
5. **Protect admin endpoints** - The `/api/admin/keys` endpoints should be protected in production (add authentication or IP whitelist)

## Managing API Keys

**List all keys (masked):**
```bash
curl http://localhost:8000/api/admin/keys
```

**Create a new key:**
```bash
curl -X POST "http://localhost:8000/api/admin/keys?name=MyApp"
```

## Deployment

When deploying:

1. Set `VITE_API_KEY` as an environment variable in your deployment platform
2. Never expose the API key in client-side code if possible (though with API keys in frontend, they can be extracted)
3. Consider using a backend proxy for sensitive operations
4. Use HTTPS to protect keys in transit

## Limitations

- API keys in frontend code can be extracted by anyone viewing the source
- This is a simple solution suitable for basic protection
- For production, consider:
  - JWT tokens with expiration
  - OAuth 2.0
  - Backend proxy for sensitive operations
  - Rate limiting per API key

