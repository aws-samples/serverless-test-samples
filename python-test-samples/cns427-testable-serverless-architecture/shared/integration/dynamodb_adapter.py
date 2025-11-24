"""DynamoDB adapter for task persistence."""

import json
import os
from datetime import datetime
from typing import List, Optional

import boto3
from aws_lambda_powertools import Logger
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError

from services.task_service.domain.exceptions import ConflictError, RepositoryError, ResourceNotFoundError, ThrottlingError
from services.task_service.models.task import Task
from shared.integration.interfaces import TaskRepository

logger = Logger()

# Initialize AWS clients at module level
AWS_REGION = os.environ.get('AWS_REGION', 'us-west-2')
dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)

# Type serializer/deserializer for DynamoDB client
_serializer = TypeSerializer()
_deserializer = TypeDeserializer()


# Helper functions
def python_to_dynamo(python_object: dict) -> dict:
    """Convert Python dict to DynamoDB format."""
    return {k: _serializer.serialize(v) for k, v in python_object.items()}


def dynamo_to_python(dynamo_object: dict) -> dict:
    """Convert DynamoDB format to Python dict."""
    return {k: _deserializer.deserialize(v) for k, v in dynamo_object.items()}


def _handle_dynamodb_error(e: ClientError, operation: str, current_task: Optional[dict] = None) -> None:
    """Convert DynamoDB ClientError to domain exceptions."""
    error_code = e.response['Error']['Code']

    if error_code in ['ProvisionedThroughputExceededException', 'ThrottlingException']:
        raise ThrottlingError(f'DynamoDB capacity exceeded during {operation}: {error_code}') from e
    elif error_code == 'ResourceNotFoundException':
        raise ResourceNotFoundError(f'DynamoDB table not found during {operation}') from e
    elif error_code in ['AccessDeniedException', 'UnrecognizedClientException']:
        raise RepositoryError(f'Permission error accessing DynamoDB during {operation}: {error_code}') from e
    elif error_code in ['RequestTimeout', 'RequestTimeoutException']:
        raise ThrottlingError(f'DynamoDB request timeout during {operation}: {error_code}') from e
    elif error_code == 'ConditionalCheckFailedException':
        raise ConflictError('The resource has been updated by another process. Please refresh and try again.', current_task=current_task) from e
    else:
        raise RepositoryError(f'Database error during {operation}: {error_code}') from e


class DynamoDBTaskRepository(TaskRepository):
    """DynamoDB implementation of TaskRepository."""

    def __init__(self, table_name: str):
        """Initialize DynamoDB repository."""
        self.table_name = table_name
        self.dynamodb = dynamodb

    def create_task(self, task: Task) -> Task:
        """Create a new task in DynamoDB."""
        try:
            # Convert Task to dict with enum values as strings
            item = task.model_dump(mode='json')
            # Convert datetime objects to ISO format strings
            item['created_at'] = task.created_at.isoformat()
            item['updated_at'] = task.updated_at.isoformat()

            dynamo_item = python_to_dynamo(item)

            # Use condition to prevent overwriting existing task
            self.dynamodb.put_item(TableName=self.table_name, Item=dynamo_item, ConditionExpression='attribute_not_exists(task_id)')

            logger.info(f'Created task: {task.task_id}')
            return task

        except ClientError as e:
            _handle_dynamodb_error(e, 'create_task')
            raise  # This line is unreachable but satisfies type checker

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID from DynamoDB."""
        try:
            key = python_to_dynamo({'task_id': task_id})
            response = self.dynamodb.get_item(TableName=self.table_name, Key=key)

            if 'Item' not in response:
                logger.info(f'Task not found: {task_id}')
                return None

            item = dynamo_to_python(response['Item'])
            # Convert ISO strings back to datetime objects
            item['created_at'] = datetime.fromisoformat(item['created_at'])
            item['updated_at'] = datetime.fromisoformat(item['updated_at'])
            return Task(**item)

        except ClientError as e:
            _handle_dynamodb_error(e, 'get_task')
            raise  # This line is unreachable but satisfies type checker

    def list_tasks(self, limit: int = 50, next_token: Optional[str] = None) -> tuple[List[Task], Optional[str]]:
        """List tasks with pagination."""
        try:
            scan_kwargs = {'TableName': self.table_name, 'Limit': limit}

            if next_token:
                scan_kwargs['ExclusiveStartKey'] = json.loads(next_token)

            response = self.dynamodb.scan(**scan_kwargs)

            tasks = []
            for dynamo_item in response.get('Items', []):
                item = dynamo_to_python(dynamo_item)
                # Convert ISO strings back to datetime objects
                item['created_at'] = datetime.fromisoformat(item['created_at'])
                item['updated_at'] = datetime.fromisoformat(item['updated_at'])
                tasks.append(Task(**item))

            # Handle pagination
            next_token_result: Optional[str] = None
            if 'LastEvaluatedKey' in response:
                next_token_result = json.dumps(response['LastEvaluatedKey'])

            logger.info(f'Listed {len(tasks)} tasks')
            return tasks, next_token_result

        except ClientError as e:
            _handle_dynamodb_error(e, 'list_tasks')
            raise  # This line is unreachable but satisfies type checker

    def update_task(self, task: Task, expected_version: int) -> Task:
        """
        Update an existing task with optimistic locking using conditional update.

        Args:
            task: The task object with updated fields and NEW version
            expected_version: The OLD version to check against (for optimistic locking)

        Returns:
            The updated task
        """
        try:
            logger.debug(f'DynamoDB update_task called: task_id={task.task_id}, expected_version={expected_version}, new_version={task.version}')

            # Build update expression dynamically
            update_expression_parts = []
            expression_attribute_values: dict = {}
            expression_attribute_names: dict = {}

            # Use the version and updated_at from the task object (set by domain service)
            # Always update these fields
            update_expression_parts.append('#updated_at = :updated_at')
            expression_attribute_names['#updated_at'] = 'updated_at'
            expression_attribute_values[':updated_at'] = task.updated_at.isoformat()

            update_expression_parts.append('#version = :new_version')
            expression_attribute_names['#version'] = 'version'
            expression_attribute_values[':new_version'] = task.version  # NEW version from domain

            logger.debug(f'Setting new version in DynamoDB: {task.version}')

            # Update other fields
            update_expression_parts.append('title = :title')
            expression_attribute_values[':title'] = task.title

            if task.description is not None:
                update_expression_parts.append('description = :description')
                expression_attribute_values[':description'] = task.description

            # Status is a reserved keyword
            update_expression_parts.append('#status = :status')
            expression_attribute_names['#status'] = 'status'
            expression_attribute_values[':status'] = task.status.value

            update_expression_parts.append('priority = :priority')
            expression_attribute_values[':priority'] = task.priority.value

            update_expression_parts.append('dependencies = :dependencies')
            expression_attribute_values[':dependencies'] = task.dependencies

            # Build the complete update expression
            update_expression = 'SET ' + ', '.join(update_expression_parts)

            # Condition: check that current version matches expected version (OLD version)
            condition_expression = '#version = :expected_version'
            expression_attribute_values[':expected_version'] = expected_version

            logger.debug(f'Condition: version must equal {expected_version}')
            logger.debug(f'Update expression: {update_expression}')

            # Convert to DynamoDB format
            key = python_to_dynamo({'task_id': task.task_id})
            dynamo_expression_values = python_to_dynamo(expression_attribute_values)

            logger.debug(f'Calling DynamoDB update_item for task {task.task_id}')

            self.dynamodb.update_item(
                TableName=self.table_name,
                Key=key,
                UpdateExpression=update_expression,
                ConditionExpression=condition_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=dynamo_expression_values,
            )

            logger.info(f'Updated task: {task.task_id}')
            logger.debug(f'DynamoDB update successful for task {task.task_id}')

            # Task already has the new version and updated_at from domain service
            return task

        except ClientError as e:
            # For conflict errors, fetch current task state
            current_task = None
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                try:
                    current = self.get_task(task.task_id)
                    if current:
                        current_task = current.model_dump()
                except Exception:
                    pass  # If we can't get current task, proceed without it
            _handle_dynamodb_error(e, 'update_task', current_task=current_task)
            raise  # This line is unreachable but satisfies type checker

    def delete_task(self, task_id: str, version: int) -> None:
        """Delete a task with version check."""
        try:
            key = python_to_dynamo({'task_id': task_id})
            expression_values = python_to_dynamo({':version': version})

            self.dynamodb.delete_item(
                TableName=self.table_name,
                Key=key,
                ConditionExpression='#version = :version',
                ExpressionAttributeNames={'#version': 'version'},
                ExpressionAttributeValues=expression_values,
            )

            logger.info(f'Deleted task: {task_id}')

        except ClientError as e:
            _handle_dynamodb_error(e, 'delete_task')
