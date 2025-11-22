"""
EventBridge Fake for Error Simulation

Simulates AWS EventBridge service errors without affecting real events.
"""

from botocore.exceptions import ClientError


class EventBridgeFake:
    """Fake EventBridge client for simulating AWS service errors."""

    def __init__(self, error_type: str):
        self.error_type = error_type

    def put_events(self, **kwargs):
        """Simulate put_events with various error types."""
        if self.error_type == 'throttling':
            raise ClientError({'Error': {'Code': 'ThrottlingException', 'Message': 'Rate exceeded'}}, 'PutEvents')
        elif self.error_type == 'permission':
            raise ClientError({'Error': {'Code': 'AccessDeniedException', 'Message': 'Not authorized'}}, 'PutEvents')
        elif self.error_type == 'service':
            raise ClientError({'Error': {'Code': 'InternalException', 'Message': 'Service error'}}, 'PutEvents')
