"""Create backup user and maintenance procedures

Revision ID: 003
Revises: 002
Create Date: 2025-07-09 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create backup user and maintenance procedures"""
    
    # Create backup role
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'backup_role') THEN
                CREATE ROLE backup_role;
            END IF;
        END
        $$;
    """)
    
    # Create backup user
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'backup_user') THEN
                CREATE USER backup_user WITH PASSWORD 'backup_password';
                GRANT backup_role TO backup_user;
            END IF;
        END
        $$;
    """)
    
    # Grant backup permissions
    op.execute("GRANT USAGE ON SCHEMA public, analytics TO backup_role;")
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public, analytics TO backup_role;")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public, analytics GRANT SELECT ON TABLES TO backup_role;")
    
    # Create maintenance schema for cleanup procedures
    op.execute("CREATE SCHEMA IF NOT EXISTS maintenance;")
    op.execute("GRANT USAGE ON SCHEMA maintenance TO app_role;")
    op.execute("GRANT CREATE ON SCHEMA maintenance TO app_role;")
    
    print("✅ Backup user and maintenance schema created")


def downgrade() -> None:
    """Remove backup user and maintenance procedures"""
    op.execute("DROP SCHEMA IF EXISTS maintenance CASCADE;")
    op.execute("DROP USER IF EXISTS backup_user;")
    op.execute("DROP ROLE IF EXISTS backup_role;")
    print("❌ Backup user and maintenance schema removed")
