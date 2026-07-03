from __future__ import annotations

from typing import List, Dict, Any

# Node Labels mapping to ensure consistency across the app
NODE_LABELS = {
    "Material": "Material",
    "Process": "Process",
    "Equipment": "Equipment",
    "Property": "Property",
    "Organization": "Organization",
    "Location": "Location",
    "Document": "Document",
    "Chunk": "Chunk",
    "Condition": "Condition",
}

# Constraints to be applied on startup or via a setup script
CONSTRAINTS = [
    f"CREATE CONSTRAINT {label}_id IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE"
    for label in NODE_LABELS.values()
]
