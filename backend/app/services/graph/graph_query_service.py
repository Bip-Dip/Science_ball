from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from neo4j import AsyncGraphDatabase

from app.db.neo4j import get_neo4j_driver
from app.schemas.graph import GraphNode, GraphEdge, GraphNeighborhood

logger = logging.getLogger(__name__)

class GraphQueryService:
    """
    Handles reading and traversal of the knowledge graph in Neo4j.
    """

    def __init__(self):
        self.driver = get_neo4j_driver()

    async def get_neighborhood(
        self,
        node_id: str,
        label: str,
        depth: int = 1,
        allowed_access_levels: list[str] = None
    ) -> GraphNeighborhood:
        """
        Fetches nodes and edges in the neighborhood of a given node.
        Applies access filtering to ensure no restricted data is leaked.
        """
        if allowed_access_levels is None:
            allowed_access_levels = ["public", "internal"]

        # Cypher query to find neighborhood with access control.
        # We use a variable-length path but filter nodes based on their access_level property.
        # Note: In Neo4j, we can't easily filter nodes mid-path in a simple MATCH without
        # checking each node. For MVP, we fetch the neighborhood and then filter,
        # or use a WHERE clause on all returned nodes.

        query = (
            f"MATCH (start:{label} {{id: $node_id}}) "
            f"MATCH path = (start)-[*0..{depth}]-() "
            f"UNWIND nodes(path) AS n "
            f"UNWIND relationships(path) AS r "
            f"RETURN n, r"
        )

        nodes_map = {}
        edges_set = set()

        async with self.driver.session() as session:
            result = await session.run(query, node_id=node_id)
            async for record in result:
                node = record["n"]
                rel = record["r"]

                # Access Control Check
                # We assume every node has an 'access_level' property if it's a Document/Chunk.
                # Entities might not have one (they are global), but we check for safety.
                node_access = node.get("access_level")
                if node_access and node_access not in allowed_access_levels:
                    continue

                # Process Node
                if node.element_id not in nodes_map:
                    # Find the label of the node
                    labels = list(node.labels)
                    primary_label = labels[0] if labels else "Node"
                    nodes_map[node.element_id] = GraphNode(
                        id=node.get("id", node.element_id),
                        label=primary_label,
                        properties=dict(node)
                    )

                # Process Edge
                if rel:
                    # We need the internal IDs for the edge to be consistent with our nodes map
                    edge_id = f"{rel.start_node.element_id}->{rel.end_node.element_id}:{rel.type}"
                    if edge_id not in edges_set:
                        edges_set.add(edge_id)
                        # Resolve logical IDs from the nodes map if possible, else use element_ids
                        start_node_logical_id = nodes_map.get(rel.start_node.element_id, GraphNode(id=rel.start_node.element_id, label="")).id
                        end_node_logical_id = nodes_map.get(rel.end_node.element_id, GraphNode(id=rel.end_node.element_id, label="")).id

                        # We'll store the edge here; we can refine IDs later if needed
                        # For now, let's use a temporary list and resolve at the end

            # Because relationships are processed alongside nodes in the UNWIND,
            # it's cleaner to collect all nodes first and then relationships.

        # Let's rewrite the logic slightly for better clarity and correct ID resolution.
        return await self._get_neighborhood_refined(node_id, label, depth, allowed_access_levels)

    async def _get_neighborhood_refined(self, node_id: str, label: str, depth: int, allowed_access_levels: list[str]) -> GraphNeighborhood:
        query = (
            f"MATCH (start:{label} {{id: $node_id}}) "
            f"MATCH path = (start)-[*0..{depth}]-() "
            f"RETURN path"
        )

        nodes_map = {} # internal_id -> GraphNode
        edges = []

        async with self.driver.session() as session:
            result = await session.run(query, node_id=node_id)
            async for record in result:
                path = record["path"]

                # First, check if all nodes in this path are allowed
                # (Or filter them out later). For MVP, we'll collect and then prune.
                for node in path.nodes:
                    node_access = node.get("access_level")
                    if node_access and node_access not in allowed_access_levels:
                        # If any node in the path is restricted, we might want to skip the whole path
                        # or just that node. Usually, in a graph preview, if you can't see a node,
                        # you shouldn't see edges connected to it.
                        pass # Handle pruning below

                for node in path.nodes:
                    if node.element_id not in nodes_map:
                        node_access = node.get("access_level")
                        if not node_access or node_access in allowed_access_levels:
                            labels = list(node.labels)
                            nodes_map[node.element_id] = GraphNode(
                                id=node.get("id", node.element_id),
                                label=labels[0] if labels else "Node",
                                properties=dict(node)
                            )

                for rel in path.relationships:
                    # Only add edge if both endpoints are allowed and exist in our map
                    if (rel.start_node.element_id in nodes_map and
                        rel.end_node.element_id in nodes_map):

                        edge_key = f"{rel.start_node.element_id}-{rel.end_node.element_id}-{rel.type}"
                        # Avoid duplicates across paths
                        if not any(e.source_id == nodes_map[rel.start_node.element_id].id and
                                   e.target_id == nodes_map[rel.end_node.element_id].id and
                                   e.type == rel.type for e in edges):
                            edges.append(GraphEdge(
                                source_id=nodes_map[rel.start_node.element_id].id,
                                target_id=nodes_map[rel.end_node.element_id].id,
                                type=rel.type,
                                properties=dict(rel)
                            ))

        return GraphNeighborhood(
            center_node_id=node_id,
            nodes=list(nodes_map.values()),
            edges=edges
        )
