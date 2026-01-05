#!/bin/bash
# Run the API from project root
cd "$(dirname "$0")"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

