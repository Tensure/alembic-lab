# Database Migrations with Alembic Lambda Function Lab

A minimal Lambda function for applying database day-2 operations (user creation, role setup, schema management) using Alembic migrations.

## 🎯 Purpose

This Lambda function:
- Connects to RDS using master credentials from AWS Secrets Manager
- Applies database day-2 operations via Alembic migrations
- Can be deployed to multiple AWS accounts (deployment method not included)
- Supports incremental migrations with detailed logging
- Relationship: 1 RDS instance → 1 Lambda function → 1 Secret

## 📁 Key Files

```
├── lambda_function.py                       # Main Lambda handler
├── test_lambda.py                           # Enhanced local testing script
├── src/simple_migration_runner.py           # Minimal migration engine
├── alembic/versions/001_day2_operations.py  # Basic user/role setup
├── alembic/versions/002_analytics_schema.py # Analytics schema and read-only user
├── alembic/versions/003_backup_maintenance.py # Backup user and maintenance
├── alembic/versions/004_audit_compliance.py # Audit logging and compliance
└── Makefile                                 # Helper commands
```

## 🧪 Local Testing

### 1. Start Local Database
```bash
nix develop
make db-up
```

### 2. Test Lambda Function

#### Test All Migrations (default)
```bash
make test-lambda
```

#### Test Specific Migration Target
```bash
make test-lambda-to TARGET=001  # Apply only migration 001
make test-lambda-to TARGET=002  # Apply migrations 001 → 002
make test-lambda-to TARGET=003  # Apply migrations 001 → 002 → 003
```

#### List Available Migrations
```bash
make list-migrations
```

### 3. Understanding Migration Behavior

The system shows you exactly what happens:

**Fresh Database → Migration 001:**
```
📋 Will apply migration 001: Example day-2 operations migration
🚀 Will apply 1 migration(s) to reach target '001': 001
✅ Success: Successfully applied 1 migration(s) to reach 001
Applied migrations: ['001']
Final revision: 001
```

**Migration 001 → 002:**
```
✅ Migration 001 already applied: Example day-2 operations migration
📋 Will apply migration 002: Create analytics schema and read-only user
🚀 Will apply 1 migration(s) to reach target '002': 002
✅ Success: Successfully applied 1 migration(s) to reach 002
Applied migrations: ['002']
Final revision: 002
```

**Running Same Migration Again:**
```
🎉 No pending migrations - database is up to date!
```

### 4. Add Your Day-2 Operations

The project includes example migrations showing different day-2 operations:

#### Migration 001 - Basic Setup
```python
def upgrade() -> None:
    # Create application role and user
    op.execute("CREATE ROLE app_role;")
    op.execute("CREATE USER app_user WITH PASSWORD 'app_password';")
    op.execute("GRANT app_role TO app_user;")
    
    # Remove public schema access
    op.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC;")
    
    # Create custom application schema
    op.execute("CREATE SCHEMA IF NOT EXISTS app_schema;")
    op.execute("GRANT ALL ON SCHEMA app_schema TO app_role;")
```

#### Migration 002 - Analytics Setup
```python
def upgrade() -> None:
    # Create analytics schema and read-only user
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics;")
    op.execute("CREATE ROLE analytics_role;")
    op.execute("CREATE USER analytics_user WITH PASSWORD 'analytics_password';")
    op.execute("GRANT analytics_role TO analytics_user;")
    
    # Grant read-only permissions
    op.execute("GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_role;")
```

#### Migration 003 - Backup & Maintenance
```python
def upgrade() -> None:
    # Create backup user and maintenance schema
    op.execute("CREATE ROLE backup_role;")
    op.execute("CREATE USER backup_user WITH PASSWORD 'backup_password';")
    op.execute("CREATE SCHEMA IF NOT EXISTS maintenance;")
```

#### Migration 004 - Audit & Compliance
```python
def upgrade() -> None:
    # Create audit schema and compliance tables
    op.execute("CREATE SCHEMA IF NOT EXISTS audit;")
    op.execute("""
        CREATE TABLE audit.database_changes (
            id SERIAL PRIMARY KEY,
            table_name VARCHAR(100) NOT NULL,
            operation VARCHAR(20) NOT NULL,
            old_values JSONB,
            new_values JSONB,
            changed_by VARCHAR(100),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
```

**To add your own operations:**
1. Create a new migration file in `alembic/versions/`
2. Follow the naming pattern: `005_your_operation.py`
3. Set `revision = '005'` and `down_revision = '004'`
4. Test locally: `make test-lambda-to TARGET=005`

##  Lambda Usage

### Event Structure
```json
{
  "secret_name": "rds-master-secret-name",
  "action": "migrate",
  "target_revision": "head"
}
```

### Parameters
- `secret_name` - **Required**: Name of the secret in AWS Secrets Manager
- `action` - **Optional**: Action to perform (default: "migrate")
  - `migrate` - Apply migrations to target revision
  - `status` - Check current migration status  
- `target_revision` - **Optional**: Target revision to migrate to (default: "head")
  - `"head"` - Apply all available migrations
  - `"001"` - Apply only migration 001
  - `"002"` - Apply migrations up to 002
  - `"003"` - Apply migrations up to 003

### Example Response
```json
{
  "statusCode": 200,
  "body": {
    "success": true,
    "message": "Successfully applied 2 migration(s) to reach 002",
    "applied_migrations": ["001", "002"],
    "final_revision": "002",
    "target_revision": "002"
  }
}
```

### Response Fields
- `success` - Boolean indicating success/failure
- `message` - Human-readable description
- `applied_migrations` - Array of migrations that were applied
- `final_revision` - Current database revision after operation
- `target_revision` - The target revision that was requested
- `previous_revision` - The revision before the operation (if applicable)

## 🔧 Development Workflow

1. **Add new day-2 operations**: Create new migration files in `alembic/versions/`
2. **Test incrementally**: 
   ```bash
   make test-lambda-to TARGET=001  # Test first migration
   make test-lambda-to TARGET=002  # Test up to second migration
   make test-lambda-to TARGET=002  # Test idempotency (should show "up to date")
   ```
3. **Test complete workflow**: `make test-lambda` (applies all migrations)
4. **Use your preferred deployment method**: Package the Lambda function code for AWS

## 📋 Available Day-2 Operations

The project includes 4 example migrations demonstrating common day-2 operations:

| Migration | Description | Creates |
|-----------|-------------|---------|
| **001** | Basic user/role setup | `app_user`, `app_role`, `app_schema` |
| **002** | Analytics infrastructure | `analytics_user`, `analytics_role`, `analytics` schema |
| **003** | Backup & maintenance | `backup_user`, `backup_role`, `maintenance` schema |
| **004** | Audit & compliance | `audit` schema, `database_changes` table, `compliance_events` table |

Each migration:
- Uses idempotent SQL (safe to run multiple times)
- Includes proper error handling
- Has corresponding downgrade functionality
- Logs completion messages for visibility

## 🎛️ Environment Variables

The Lambda function uses:
- **AWS Secrets Manager** for database credentials
- **Event payload** for secret name, action, and target revision
- **No hardcoded database connections**
- **Detailed logging** for troubleshooting and visibility

## 🔍 Troubleshooting

### Local Testing Issues
- **Database not running**: `make db-up` or `make db-reset`
- **Connection failed**: Check PostgreSQL container status with `docker ps`
- **Migration errors**: Check the specific migration file for SQL syntax

### Lambda Issues
- **Invalid secret name**: Verify secret exists in AWS Secrets Manager
- **Permission denied**: Ensure Lambda has `secretsmanager:GetSecretValue` permission
- **Database connection**: Check VPC/security group configuration
- **Migration conflicts**: Check CloudWatch logs for detailed Alembic errors

### Common Commands
```bash
make help                    # Show all available commands
make list-migrations         # List available migrations
make test-lambda-to TARGET=001  # Test specific migration
make db-reset               # Reset database to clean state
```

## 🚀 Next Steps

1. **Test the existing migrations**: 
   ```bash
   make db-reset
   make test-lambda-to TARGET=001
   make test-lambda-to TARGET=002
   make test-lambda-to TARGET=003
   make test-lambda-to TARGET=004
   ```

2. **Test idempotency**: Run the same migration twice to see "up to date" behavior

3. **Add your specific day-2 operations**: Create new migration files for your needs

4. **Deploy using your preferred method**: Package and deploy the Lambda function code

## 🏁 Summary

This is a **minimal** Lambda function for database day-2 operations that provides:

✅ **Incremental migrations** with detailed logging  
✅ **Idempotent operations** (safe to run multiple times)  
✅ **Target revision control** (apply specific migrations)  
✅ **Comprehensive examples** (user/role/schema/audit setup)  
✅ **Local testing workflow** with argument support  
✅ **AWS Secrets Manager integration**  
✅ **Minimal dependencies** (just Alembic + SQLAlchemy + boto3)  

Perfect for your database day-2 operations workflow!
