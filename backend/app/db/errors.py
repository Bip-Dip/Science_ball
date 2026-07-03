"""Shared errors for storage clients."""


class StorageClientError(Exception):
    """Base error for storage client operations."""


class StorageClientConfigError(StorageClientError):
    """Raised when client configuration is invalid or incomplete."""
