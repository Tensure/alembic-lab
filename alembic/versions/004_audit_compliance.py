"""Create audit logging and compliance tables

Revision ID: 004
Revises: 003
Create Date: 2025-07-09 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create audit logging and compliance infrastructure"""
    
    # Create audit schema
    op.execute("CREATE SCHEMA IF NOT EXISTS audit;")
    
    # Create audit role
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'audit_role') THEN
                CREATE ROLE audit_role;
            END IF;
        END
        $$;
    """)
    
    # Create audit table for tracking database changes
    op.execute("""
        CREATE TABLE IF NOT EXISTS audit.database_changes (
            id SERIAL PRIMARY KEY,
            table_name VARCHAR(100) NOT NULL,
            operation VARCHAR(20) NOT NULL,
            old_values JSONB,
            new_values JSONB,
            changed_by VARCHAR(100),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create compliance table for regulatory tracking
    op.execute("""
        CREATE TABLE IF NOT EXISTS audit.compliance_events (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR(50) NOT NULL,
            event_data JSONB,
            compliance_status VARCHAR(20) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            reviewed_by VARCHAR(100)
        );
    """)
    
    # Grant permissions to audit role
    op.execute("GRANT USAGE ON SCHEMA audit TO audit_role;")
    op.execute("GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA audit TO audit_role;")
    op.execute("GRANT USAGE ON ALL SEQUENCES IN SCHEMA audit TO audit_role;")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT SELECT, INSERT, UPDATE ON TABLES TO audit_role;")
    op.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA audit GRANT USAGE ON SEQUENCES TO audit_role;")
    
    # Grant audit role to app_role for audit logging
    op.execute("GRANT audit_role TO app_role;")
    
    print("✅ Audit logging and compliance infrastructure created")


def downgrade() -> None:
    """Remove audit logging and compliance infrastructure"""
    op.execute("DROP SCHEMA IF EXISTS audit CASCADE;")
    op.execute("DROP ROLE IF EXISTS audit_role;")
    print("❌ Audit logging and compliance infrastructure removed")
