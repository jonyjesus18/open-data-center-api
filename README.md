# Data Center API

A simple REST API built with FastAPI for CRUD operations on data center tables.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database from CSV files:
```bash
python init_db.py
```

3. Run the API server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Endpoints

### Data Centers

- `GET /api/datacenters` - Get all data centers (with pagination: `?skip=0&limit=100`)
- `GET /api/datacenters/{public_id}` - Get a specific data center
- `POST /api/datacenters` - Create a new data center
- `PUT /api/datacenters/{public_id}` - Update a data center
- `DELETE /api/datacenters/{public_id}` - Delete a data center

### Data Center Metadata

- `GET /api/metadata` - Get all metadata (with pagination: `?skip=0&limit=100`)
- `GET /api/datacenters/{public_id}/metadata` - Get metadata for a specific data center
- `POST /api/metadata` - Create new metadata
- `PUT /api/metadata/{public_id}` - Update metadata
- `DELETE /api/metadata/{public_id}` - Delete metadata

### Combined

- `GET /api/datacenters/{public_id}/full` - Get data center with its metadata combined

## Example Usage

### Create a data center:
```bash
curl -X POST "http://localhost:8000/api/datacenters" \
  -H "Content-Type: application/json" \
  -d '{
    "public_id": "TEST123",
    "dc_name": "Test Data Center",
    "coordinates": "[0.0, 0.0]",
    "date_added": "2025-01-01"
  }'
```

### Get all data centers:
```bash
curl "http://localhost:8000/api/datacenters"
```

### Get a specific data center:
```bash
curl "http://localhost:8000/api/datacenters/RYKZ4w"
```

### Update a data center:
```bash
curl -X PUT "http://localhost:8000/api/datacenters/RYKZ4w" \
  -H "Content-Type: application/json" \
  -d '{
    "dc_name": "Updated Name"
  }'
```

### Delete a data center:
```bash
curl -X DELETE "http://localhost:8000/api/datacenters/RYKZ4w"
```

