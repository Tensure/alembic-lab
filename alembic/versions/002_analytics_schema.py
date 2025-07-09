"""Create analytics schema and read-only user

Revision ID: 002
Revises: 001
Create Date: 2025-07-09 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create analytics schema and read-only user"""
    
    # Create analytics schema
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    
    # Create analytics role
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_role') THEN
                CREATE ROLE analytics_role;
            END IF;
        END
        $$;
    """)
    
    # Create read-only analytics user
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_user') THEN
                CREATE USER analytics_user WITH PASSWORD 'analytics_password';
                GRANT analytics_role TO analytics_user;
            END IF;
        END
        $$;
    """)
    
    # Grant read-only permissions to analytics schema
    op.execute("GRANT USAGE ON SCHEMA analytics TO analytics_role;")
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO analytics_role;")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA analytics GRANT SELECT ON TABLES TO analytics_role;")
    
    # Also grant read access to public schema
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_role;")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_role;")
    
    print("✅ Analytics schema and read-only user created")


def downgrade() -> None:
    """Remove analytics schema and user"""
    op.execute("DROP SCHEMA IF EXISTS analytics CASCADE;")
    op.execute("DROP USER IF EXISTS analytics_user;")
    op.execute("DROP ROLE IF EXISTS analytics_role;")
    print("❌ Analytics schema and user removed")
