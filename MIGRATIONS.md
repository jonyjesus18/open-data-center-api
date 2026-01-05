# Database Migrations Guide

This project uses **Alembic** for database schema migrations, which is the standard migration tool for SQLAlchemy.

## Overview

Alembic allows you to:
- Track database schema changes in version-controlled migration files
- Automatically generate migrations from model changes
- Apply migrations to update database schema
- Rollback migrations if needed

## Quick Start

### Running Migrations

When you run `init_db.py`, migrations are automatically applied:

```bash
conda activate open-data-center-api
python init_db.py
```

This will:
1. Run all pending migrations to bring the database schema up to date
2. Load data from CSV files

### Manual Migration Commands

You can also run migrations manually:

```bash
# Apply all pending migrations
alembic upgrade head

# Apply migrations one step at a time
alembic upgrade +1

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Check current migration status
alembic current

# View migration history
alembic history
```

## Creating New Migrations

### Auto-generate Migration from Model Changes

When you modify models in `database.py`, create a new migration:

```bash
# Auto-generate migration based on model changes
alembic revision --autogenerate -m "Description of changes"

# Example:
alembic revision --autogenerate -m "Add new column to data_centers_metadata"
```

**Important**: Always review the generated migration file before applying it!

### Manual Migration

For complex changes, create an empty migration and write it manually:

```bash
alembic revision -m "Description of changes"
```

Then edit the generated file in `alembic/versions/` to add your migration logic.

## Migration Files

Migration files are stored in `alembic/versions/` and follow the naming pattern:
- `{revision_id}_{description}.py`

Each migration file contains:
- `upgrade()`: Function to apply the migration
- `downgrade()`: Function to rollback the migration

## Configuration

- **Alembic config**: `alembic.ini`
- **Migration environment**: `alembic/env.py`
- **Database connection**: Automatically uses `DATABASE_URL` from `.env` file

## Best Practices

1. **Always review auto-generated migrations** before applying them
2. **Test migrations** on a development database first
3. **Commit migration files** to version control
4. **Never edit existing migrations** that have been applied to production
5. **Create a new migration** for any schema changes

## Troubleshooting

### Migration conflicts
If you have conflicts between local and remote migrations:
```bash
# Check current state
alembic current

# View history
alembic history

# Resolve conflicts manually or use alembic merge
alembic merge -m "Merge migrations" head1 head2
```

### Database out of sync
If your database schema doesn't match your models:
```bash
# Generate a migration to sync
alembic revision --autogenerate -m "Sync schema"
```

### Reset database (development only)
⚠️ **Warning**: This will delete all data!
```bash
alembic downgrade base
alembic upgrade head
```

## Example Workflow

1. Modify a model in `database.py` (e.g., add a new column)
2. Generate migration: `alembic revision --autogenerate -m "Add new column"`
3. Review the generated migration file
4. Apply migration: `alembic upgrade head`
5. Test your changes
6. Commit migration file to git

## Integration with init_db.py

The `init_db.py` script automatically runs migrations before loading data:

```python
def init_database():
    # Run Alembic migrations to create/update database schema
    run_migrations()
    
    # Then load data from CSV files
    # ...
```

This ensures your database schema is always up to date before loading data.

