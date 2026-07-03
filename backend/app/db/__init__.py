"""Storage client factories for external services.

Each module provides a lazy factory that reads from centralized settings.
No connections are established at import time — factories return
configured clients/sessions that connect only when used.
"""
