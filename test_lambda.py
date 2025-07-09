#!/usr/bin/env python3
"""
Simple test script for the database day-2 operations Lambda function
"""
import json
import os
import sys
import logging
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_lambda(target_revision="head"):
    """Test the Lambda function with a local database"""
    from lambda_function import lambda_handler
    
    print("🚀 Database Day-2 Operations Lambda Test")
    print("=" * 45)
    
    # Check database connection first
    database_url = "postgresql://alembic_user:alembic_pass@localhost:5432/alembic_db"
    
    print("🔌 Checking database connection...")
    try:
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("💡 Make sure to run 'make db-up' first")
        return False
    
    # Test event
    event = {
        "secret_name": "test-rds-secret",
        "action": "migrate",
        "target_revision": target_revision
    }
    
    print(f"🧪 Testing Lambda function with target revision: {target_revision}")
    print(f"Event: {json.dumps(event, indent=2)}")
    print("=" * 40)
    
    # Mock AWS context
    class MockContext:
        def __init__(self):
            self.function_name = "test-day2-operations"
            self.aws_request_id = "test-request-id"
    
    context = MockContext()
    
    # Mock boto3
    import unittest.mock
    
    mock_secret = {
        'username': 'alembic_user',
        'password': 'alembic_pass',
        'host': 'localhost',
        'port': 5432,
        'dbname': 'alembic_db'
    }
    
    with unittest.mock.patch('boto3.client') as mock_boto3:
        mock_secrets_client = unittest.mock.MagicMock()
        mock_secrets_client.get_secret_value.return_value = {
            'SecretString': json.dumps(mock_secret)
        }
        mock_boto3.return_value = mock_secrets_client
        
        try:
            # Call the Lambda function
            response = lambda_handler(event, context)
            
            print("📊 Response:")
            print(json.dumps(response, indent=2))
            
            if response.get('statusCode') == 200:
                body = json.loads(response['body'])
                if body.get('success'):
                    print(f"\n✅ Success: {body.get('message')}")
                    if 'applied_migrations' in body:
                        print(f"Applied migrations: {body['applied_migrations']}")
                    if 'final_revision' in body:
                        print(f"Final revision: {body['final_revision']}")
                else:
                    print(f"\n❌ Failed: {body.get('error')}")
            else:
                body = json.loads(response['body'])
                print(f"\n❌ Failed: {body.get('error')}")
                
        except Exception as e:
            print(f"\n❌ Exception: {e}")
            return False
    
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test Lambda function with different migration targets')
    parser.add_argument('--target', '-t', default='head', 
                       help='Target revision to migrate to (default: head)')
    parser.add_argument('--list-migrations', '-l', action='store_true',
                       help='List available migrations')
    
    args = parser.parse_args()
    
    if args.list_migrations:
        print("📋 Available migrations:")
        print("  001 - Example day-2 operations migration")
        print("  002 - Create analytics schema and read-only user") 
        print("  003 - Create backup user and maintenance procedures")
        print("  004 - Create audit logging and compliance tables")
        print("  head - Apply all migrations (default)")
        sys.exit(0)
    
    print(f"🧪 Testing with target revision: {args.target}")
    success = test_lambda(args.target)
    
    if success:
        print("\n✨ Test complete!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
