"""Example day-2 operations migration

Revision ID: 001
Revises: 
Create Date: 2025-07-09 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Day-2 operations: Create app users and roles"""
    
    # Create application role
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_role') THEN
                CREATE ROLE app_role;
            END IF;
        END
        $$;
    """)
    
    # Create application user
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
                CREATE USER app_user WITH PASSWORD 'app_password';
                GRANT app_role TO app_user;
            END IF;
        END
        $$;
    """)
    
    # Remove public schema access
    op.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC;")
    
    # Create a custom schema for the application
    op.execute("CREATE SCHEMA IF NOT EXISTS app_schema;")
    op.execute("GRANT ALL ON SCHEMA app_schema TO app_role;")
    
    print("✅ Day-2 operations completed: Created app_user, app_role, and app_schema")


def downgrade() -> None:
    """Reverse day-2 operations"""
    
    # Drop custom schema
    op.execute("DROP SCHEMA IF EXISTS app_schema CASCADE;")
    
    # Restore public schema access
    op.execute("GRANT ALL ON SCHEMA public TO PUBLIC;")
    
    # Drop application user and role
    op.execute("DROP USER IF EXISTS app_user;")
    op.execute("DROP ROLE IF EXISTS app_role;")
    
    print("✅ Day-2 operations reversed")
