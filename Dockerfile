FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies with uv (much faster than pip)
RUN uv pip install --system -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Expose port (Render will set PORT env var)
EXPOSE ${PORT:-8000}

# Run the application
CMD uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

