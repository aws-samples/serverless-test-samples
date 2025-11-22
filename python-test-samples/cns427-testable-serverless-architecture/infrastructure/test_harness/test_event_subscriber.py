"""
Test Subscriber Lambda Function

Captures EventBridge test events and stores them in the test results table
for integration test verification.
"""

import json
import os
import time
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

# Get configuration from environment
table_name = os.environ.get('TEST_RESULTS_TABLE_NAME', 'cns427-task-api-test-results')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table(table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    EventBridge test event subscriber handler.

    Captures TEST-* events and stores them in the test results table
    for integration test verification.
    """
    print(f'Received EventBridge event: {json.dumps(event, default=str)}')

    try:
        # Extract event details directly from EventBridge event
        source = event.get('source', '')
        detail_type = event.get('detail-type', '')
        detail = event.get('detail', {})

        # Only process TEST events
        if not source.startswith('TEST-') or not detail_type.startswith('TEST-'):
            print(f'Skipping non-test event: source={source}, detail_type={detail_type}')
            return {'statusCode': 200, 'body': json.dumps({'message': 'Skipped non-test event', 'processed_count': 0})}

        # Title is test run ID
        test_run_id = detail.get('title', '')
        if not test_run_id.startswith('TEST-'):
            print(f'Skipping event without test run id: {test_run_id}')
            return {'statusCode': 200, 'body': json.dumps({'message': 'Skipped event without test run id', 'processed_count': 0})}

        # Create timestamp for sorting
        event_timestamp = str(time.time())

        # Store event in test results table
        item = {
            'test_run_id': test_run_id,
            'event_timestamp': event_timestamp,
            'event_type': detail_type.replace('TEST-', ''),  # Remove TEST- prefix
            'event_data': json.dumps(detail),
            'source': source,
            'ttl': int(time.time()) + 3600,  # Auto-cleanup after 1 hour
        }

        table.put_item(Item=item)

        print(f'Stored test event: test_run_id={test_run_id}, event_type={item["event_type"]}')

        return {
            'statusCode': 200,
            'body': json.dumps(
                {'message': 'Processed test event successfully', 'processed_count': 1, 'test_run_id': test_run_id, 'event_type': item['event_type']}
            ),
        }

    except ClientError as e:
        print(f'DynamoDB error: {e}')
        return {'statusCode': 500, 'body': json.dumps({'error': f'DynamoDB error: {str(e)}'})}

    except Exception as e:
        print(f'Unexpected error: {e}')
        return {'statusCode': 500, 'body': json.dumps({'error': f'Unexpected error: {str(e)}'})}
