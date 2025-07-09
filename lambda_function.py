"""
Minimal Lambda function for database day-2 operations
"""
import json
import logging
import boto3
from typing import Dict, Any
from src.simple_migration_runner import apply_day2_operations

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_database_connection_from_secret(secret_name: str) -> str:
    """
    Get database connection string from AWS Secrets Manager
    
    Args:
        secret_name: Name of the secret in Secrets Manager
        
    Returns:
        Database connection string
    """
    try:
        secrets_client = boto3.client('secretsmanager')
        response = secrets_client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        # Extract connection details
        username = secret['username']
        password = secret['password']
        host = secret['host']
        port = secret['port']
        dbname = secret['dbname']
        
        # Build connection string
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{dbname}"
        
        logger.info(f"Retrieved database connection for host: {host}")
        return connection_string
        
    except Exception as e:
        logger.error(f"Error retrieving secret {secret_name}: {e}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for database day-2 operations
    
    Expected event structure:
    {
        "secret_name": "rds-master-secret-name",
        "action": "migrate"  # Optional, defaults to "migrate"
    }
    """
    try:
        # Get secret name from event
        secret_name = event.get('secret_name')
        if not secret_name:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'secret_name is required'
                })
            }
        
        # Get database connection string
        database_url = get_database_connection_from_secret(secret_name)
        
        # Get action (default to migrate)
        action = event.get('action', 'migrate')
        target_revision = event.get('target_revision', 'head')
        
        # Execute action
        if action == 'migrate':
            result = apply_day2_operations(database_url, target_revision)
        elif action == 'status':
            # For status, just check connection
            from src.simple_migration_runner import SimpleMigrationRunner
            runner = SimpleMigrationRunner(database_url)
            result = runner.check_connection()
        else:
            result = {
                'success': False,
                'error': f'Unknown action: {action}',
                'message': 'Valid actions are: migrate, status'
            }
        
        return {
            'statusCode': 200 if result.get('success', False) else 500,
            'body': json.dumps(result, default=str)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': str(e)
            })
        }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'secret_name': 'test-rds-secret',
        'action': 'migrate'
    }
    
    # Mock the secrets manager for local testing
    import unittest.mock
    
    mock_secret = {
        'username': 'postgres',
        'password': 'password',
        'host': 'localhost',
        'port': 5432,
        'dbname': 'testdb'
    }
    
    with unittest.mock.patch('boto3.client') as mock_boto3:
        mock_secrets_client = unittest.mock.MagicMock()
        mock_secrets_client.get_secret_value.return_value = {
            'SecretString': json.dumps(mock_secret)
        }
        mock_boto3.return_value = mock_secrets_client
        
        result = lambda_handler(test_event, None)
        print(json.dumps(result, indent=2))
