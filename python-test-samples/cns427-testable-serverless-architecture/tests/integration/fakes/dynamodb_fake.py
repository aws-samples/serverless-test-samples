"""
DynamoDB Fake for Error Simulation

Used only for testing AWS service errors without affecting real data.
Enhanced with conditional update simulation and version token tracking.
"""

from typing import Any, Dict, Optional

from boto3.dynamodb.types import TypeDeserializer
from botocore.exceptions import ClientError


class DynamoDBFake:
    """Fake DynamoDB client for error simulation and conflict testing."""

    def __init__(self, error_type: str = None):
        """
        Initialize fake with specific error type.

        Args:
            error_type: Type of error to simulate (throttling, iam, timeout, conditional_check)
        """
        self.error_type = error_type
        self.table_name = 'cns427-task-api-core-tasks'
        self.task_store = {}  # In-memory task storage for conflict testing
        self._deserializer = TypeDeserializer()

    def _deserialize_item(self, dynamo_item: Dict[str, Any]) -> Dict[str, Any]:
        """Convert DynamoDB format to Python dict."""
        return {k: self._deserializer.deserialize(v) for k, v in dynamo_item.items()}

    def put_item(self, **kwargs) -> Dict[str, Any]:
        """Simulate put_item with errors and data storage."""
        # Simple error simulation (but NOT conditional_check - that's only for updates)
        if self.error_type == 'throttling':
            raise ClientError({'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Rate exceeded'}}, 'PutItem')
        elif self.error_type == 'iam':
            raise ClientError({'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}}, 'PutItem')
        elif self.error_type == 'timeout':
            raise ClientError({'Error': {'Code': 'RequestTimeout', 'Message': 'Request timeout'}}, 'PutItem')
        # Note: conditional_check errors only apply to update_item, not put_item

        # Store item in fake data store for conflict testing
        if 'Item' in kwargs:
            item = self._deserialize_item(kwargs['Item'])
            task_id = item.get('task_id')
            if task_id:
                self.task_store[task_id] = item

        return {}

    def get_item(self, **kwargs) -> Dict[str, Any]:
        """Simulate get_item with errors and data retrieval."""
        # Simple error simulation
        if self.error_type == 'throttling':
            raise ClientError({'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Rate exceeded'}}, 'GetItem')
        elif self.error_type == 'iam':
            raise ClientError({'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}}, 'GetItem')
        elif self.error_type == 'timeout':
            raise ClientError({'Error': {'Code': 'RequestTimeout', 'Message': 'Request timeout'}}, 'GetItem')

        # Retrieve item from fake data store
        if 'Key' in kwargs:
            key = self._deserialize_item(kwargs['Key'])
            task_id = key.get('task_id')
            if task_id and task_id in self.task_store:
                # Convert back to DynamoDB format for response
                from boto3.dynamodb.types import TypeSerializer

                serializer = TypeSerializer()
                item = {k: serializer.serialize(v) for k, v in self.task_store[task_id].items()}
                return {'Item': item}

        return {}  # Item not found

    def update_item(self, **kwargs) -> Dict[str, Any]:
        """Simulate update_item with errors and conditional update logic."""
        # Simple error simulation
        if self.error_type == 'throttling':
            raise ClientError({'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Rate exceeded'}}, 'UpdateItem')
        elif self.error_type == 'iam':
            raise ClientError({'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}}, 'UpdateItem')
        elif self.error_type == 'timeout':
            raise ClientError({'Error': {'Code': 'RequestTimeout', 'Message': 'Request timeout'}}, 'UpdateItem')

        # Handle conditional updates for conflict testing
        if 'ConditionExpression' in kwargs and 'Key' in kwargs:
            key = self._deserialize_item(kwargs['Key'])
            task_id = key.get('task_id')

            if task_id and task_id in self.task_store:
                current_item = self.task_store[task_id]

                # Check version condition
                if 'ExpressionAttributeValues' in kwargs:
                    expression_values = self._deserialize_item(kwargs['ExpressionAttributeValues'])
                    expected_version = expression_values.get(':expected_version')
                    current_version = current_item.get('version')

                    # Simulate conditional check failure if versions don't match
                    if expected_version and current_version and expected_version != current_version:
                        raise ClientError(
                            {'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'The conditional request failed'}}, 'UpdateItem'
                        )

                    # Update the item with new values
                    if ':new_version' in expression_values:
                        current_item['version'] = expression_values[':new_version']
                    if ':updated_at' in expression_values:
                        current_item['updated_at'] = expression_values[':updated_at']

                    # Apply other updates based on expression values
                    for key, value in expression_values.items():
                        if key.startswith(':') and key not in [':expected_version', ':new_version', ':updated_at']:
                            field_name = key[1:]  # Remove ':' prefix
                            current_item[field_name] = value
            elif self.error_type == 'conditional_check':
                # Force conditional check failure for testing
                raise ClientError({'Error': {'Code': 'ConditionalCheckFailedException', 'Message': 'Condition not met'}}, 'UpdateItem')

        return {}

    def scan(self, **kwargs) -> Dict[str, Any]:
        """Simulate scan operation for listing all items."""
        # Simple error simulation
        if self.error_type == 'throttling':
            raise ClientError({'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Rate exceeded'}}, 'Scan')
        elif self.error_type == 'iam':
            raise ClientError({'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}}, 'Scan')
        elif self.error_type == 'timeout':
            raise ClientError({'Error': {'Code': 'RequestTimeout', 'Message': 'Request timeout'}}, 'Scan')

        # Return all items from task store
        from boto3.dynamodb.types import TypeSerializer

        serializer = TypeSerializer()

        items = []
        for task_data in self.task_store.values():
            # Convert back to DynamoDB format for response
            item = {k: serializer.serialize(v) for k, v in task_data.items()}
            items.append(item)

        return {'Items': items}

    def set_task_data(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Set task data in the fake store for testing."""
        self.task_store[task_id] = task_data.copy()

    def get_task_data(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task data from the fake store."""
        return self.task_store.get(task_id)

    def clear_task_store(self) -> None:
        """Clear all task data from the fake store."""
        self.task_store.clear()

    def simulate_concurrent_access(self, task_id: str, version: int) -> None:
        """Simulate concurrent access by updating version."""
        if task_id in self.task_store:
            self.task_store[task_id]['version'] = version
