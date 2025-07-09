# Lambda Migration Workflow Guide

This guide shows you how to add new database migrations to your Lambda function.

## 🔄 Complete Workflow

### 1. Local Development

```bash
# Enter development environment
nix develop

# Start local database
make db-up

# Make changes to your models (e.g., src/models.py)
# Add new fields, tables, etc.
```

### 2. Create Migration Locally

**Option A: Create and test separately**
```bash
# Create migration
make revision m="Add phone number to user"

# Test migration
make migrate
```

**Option B: Create and run in one step**
```bash
# Create and run migration immediately
make revision-and-run m="Add phone number to user"
```

### 3. Test Your Changes

```bash
# Run your application to test
python src/main.py

# Run tests
make test
```

### 4. Deploy to Lambda

```bash
# Create deployment package with your new migration
make lambda-deploy

# Deploy infrastructure
cd terraform
terraform apply
```

### 5. Run Migration in Lambda

**Option A: AWS CLI**
```bash
aws lambda invoke \
  --function-name alembic-migrations \
  --payload '{"action":"migrate"}' \
  response.json && cat response.json
```

**Option B: Lambda Function URL**
```bash
curl -X POST https://your-lambda-url \
  -H "Content-Type: application/json" \
  -d '{"action":"migrate"}'
```

**Option C: From Python**
```python
import boto3
import json

lambda_client = boto3.client('lambda')
response = lambda_client.invoke(
    FunctionName='alembic-migrations',
    Payload=json.dumps({'action': 'migrate'})
)
result = json.loads(response['Payload'].read())
print(result)
```

## 📋 Available Lambda Actions

### Migration Actions
```json
// Run all pending migrations
{"action": "migrate"}

// Check migration status
{"action": "status"}

// Upgrade to specific revision
{"action": "upgrade", "target_revision": "head"}

// Downgrade to previous revision
{"action": "downgrade", "target_revision": "-1"}

// Create new migration (development only)
{"action": "create", "message": "Add new field", "autogenerate": true}

// Create and run migration (development only)
{"action": "create_and_run", "message": "Add new field", "autogenerate": true}

// Stamp database (mark as migrated without running)
{"action": "stamp", "revision": "head"}
```

## 🎯 Quick Commands

### Development
```bash
# Quick migration creation and testing
make revision-and-run m="Add phone number to user"

# Test Lambda handler locally
make lambda-test-migration
```

### Production
```bash
# Deploy and get migration command
make lambda-deploy-and-migrate
```

## 🔍 Checking Migration Status

### Local
```bash
python src/migration_runner.py
```

### Lambda
```bash
aws lambda invoke \
  --function-name alembic-migrations \
  --payload '{"action":"status"}' \
  response.json && cat response.json
```

## 🚨 Troubleshooting

### If Migration Fails
```bash
# Check what went wrong
aws lambda invoke \
  --function-name alembic-migrations \
  --payload '{"action":"status"}' \
  response.json && cat response.json

# Manual downgrade if needed
aws lambda invoke \
  --function-name alembic-migrations \
  --payload '{"action":"downgrade", "target_revision": "-1"}' \
  response.json && cat response.json
```

### If Database is Out of Sync
```bash
# Stamp database to current state
aws lambda invoke \
  --function-name alembic-migrations \
  --payload '{"action":"stamp", "revision": "head"}' \
  response.json && cat response.json
```

## 📁 File Structure After Migration

```
alembic/versions/
├── 20250709_1430_abc123_initial_migration.py
├── 20250709_1500_def456_add_user_table.py
└── 20250709_1530_ghi789_add_phone_number_to_user.py  # Your new migration
```

## 🔄 CI/CD Integration

### GitHub Actions Example
```yaml
name: Deploy Lambda Migrations

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Nix
        uses: nixbuild/nix-quick-install-action@v1
        
      - name: Build Lambda package
        run: |
          nix develop --command make lambda-package
          
      - name: Deploy with Terraform
        run: |
          cd terraform
          terraform init
          terraform apply -auto-approve
          
      - name: Run migrations
        run: |
          aws lambda invoke \
            --function-name alembic-migrations \
            --payload '{"action":"migrate"}' \
            response.json
```

This workflow ensures your migrations are properly versioned, tested locally, and deployed safely to your Lambda environment!
