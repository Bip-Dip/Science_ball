from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.db.neo4j import get_neo4j_driver
from app.graph.schema import CONSTRAINTS, NODE_LABELS

logger = logging.getLogger(__name__)

class GraphWriter:
    """
    Handles idempotent writing of knowledge graph nodes and relationships to Neo4j.
    """

    def __init__(self):
        self.driver = get_neo4j_driver()

    async def initialize_schema(self) -> None:
        """Apply unique constraints for the core node labels."""
        async with self.driver.session() as session:
            for constraint_query in CONSTRAINTS:
                try:
                    await session.run(constraint_query)
                except Exception as e:
                    logger.warning(f"Could not create constraint: {e}")

    async def write_node(self, label: str, node_id: str, properties: Dict[str, Any]) -> None:
        """
        Idempotently writes a node with the given label and properties.
        """
        if label not in NODE_LABELS:
            # Fallback to generic Node or raise error; SDD defines specific labels
            label = "Entity"

        query = (
            f"MERGE (n:{label} {{id: $id}}) "
            f"SET n += $props "
            f"RETURN n"
        )

        async with self.driver.session() as session:
            await session.run(query, id=node_id, props=properties)

    async def write_relationship(
        self,
        from_node: Dict[str, Any],
        to_node: Dict[str, Any],
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Idempotently writes a relationship between two nodes.

        from_node/to_node should contain at least 'id' and 'label'.
        """
        # Sanitize rel_type to prevent Cypher injection (though it should come from internal constants)
        safe_rel = "".join(c for c in rel_type if c.isalnum() or c == '_')

        query = (
            f"MATCH (a:{from_node['label']} {{id: $from_id}}) "
            f"MATCH (b:{to_node['label']} {{id: $to_id}}) "
            f"MERGE (a)-[r:{safe_rel}]->(b) "
            f"SET r += $props "
            f"RETURN r"
        )

        async with self.driver.session() as session:
            await session.run(
                query,
                from_id=from_node['id'],
                to_id=to_node['id'],
                props=properties or {}
            )

    async def write_nodes_batch(self, nodes: List[Dict[str, Any]]) -> None:
        """
        Write multiple nodes of the same label efficiently using UNWIND.
        Expected format: [{'label': '...', 'id': '...', 'props': {...}}, ...]
        """
        if not nodes:
            return

        # Group by label since UNWIND requires a single label per query
        nodes_by_label = {}
        for n in nodes:
            label = n['label']
            nodes_by_label.setdefault(label, []).append({"id": n['id'], "props": n['props']})

        async with self.driver.session() as session:
            for label, data in nodes_by_label.items():
                query = (
                    f"UNWIND $batch AS row "
                    f"MERGE (n:{label} {{id: row.id}}) "
                    f"SET n += row.props"
                )
                await session.run(query, batch=data)

    async def write_relationships_batch(self, rels: List[Dict[str, Any]]) -> None:
        """
        Write multiple relationships efficiently using UNWIND.
        Expected format: [{'from': {...}, 'to': {...}, 'type': '...', 'props': {...}}, ...]
        """
        if not rels:
            return

        # Group by relationship type and node label pair
        rels_by_key = {}
        for r in rels:
            key = (r['from']['label'], r['to']['label'], r['type'])
            rels_by_key.setdefault(key, []).append({
                "from_id": r['from']['id'],
                "to_id": r['to']['id'],
                "props": r['props']
            })

        async with self.driver.session() as session:
            for (f_label, t_label, rel_type), data in rels_by_key.items():
                safe_rel = "".join(c for c in rel_type if c.isalnum() or c == '_')
                query = (
                    f"UNWIND $batch AS row "
                    f"MATCH (a:{f_label} {{id: row.from_id}}) "
                    f"MATCH (b:{t_label} {{id: row.to_id}}) "
                    f"MERGE (a)-[r:{safe_rel}]->(b) "
                    f"SET r += row.props"
                )
                await session.run(query, batch=data)
