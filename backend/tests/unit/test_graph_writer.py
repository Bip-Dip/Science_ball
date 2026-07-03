import pytest
from unittest.mock import AsyncMock, MagicMock
from app.graph.graph_writer import GraphWriter

# A robust mock for the Neo4j driver and its async session context manager
class MockNeo4jDriver:
    def __init__(self):
        self.session_mock = AsyncMock()
        # Setup the async context manager: async with driver.session() as session
        self.session_cm = MagicMock()
        # The aenter method must be an async function that returns the session_mock
        self.session_cm.__aenter__ = AsyncMock(return_value=self.session_mock)
        self.session_cm.__aexit__ = AsyncMock(return_value=None)

    def session(self, **kwargs):
        return self.session_cm

@pytest.mark.asyncio
async def test_write_node_calls_correct_cypher():
    driver_mock = MockNeo4jDriver()

    import app.db.neo4j
    original_get_driver = app.db.neo4j.get_neo4j_driver
    app.db.neo4j.get_neo4j_driver = MagicMock(return_value=driver_mock)

    try:
        writer = GraphWriter()
        await writer.write_node(
            label="Material",
            node_id="mat_nickel",
            properties={"name": "никель"}
        )

        # Verify the call to session.run
        driver_mock.session_mock.run.assert_called_once()
        args, kwargs = driver_mock.session_mock.run.call_args
        query = args[0]
        assert "MERGE (n:Material {id: $id})" in query
        assert kwargs["id"] == "mat_nickel"
        assert kwargs["props"] == {"name": "никель"}
    finally:
        app.db.neo4j.get_neo4j_driver = original_get_driver

@pytest.mark.asyncio
async def test_write_relationship_calls_correct_cypher():
    driver_mock = MockNeo4jDriver()

    import app.db.neo4j
    original_get_driver = app.db.neo4j.get_neo4j_driver
    app.db.neo4j.get_neo4j_driver = MagicMock(return_value=driver_mock)

    try:
        writer = GraphWriter()
        await writer.write_relationship(
            from_node={"id": "proc_1", "label": "Process"},
            to_node={"id": "mat_1", "label": "Material"},
            rel_type="USES_MATERIAL",
            properties={"confidence": 0.8}
        )

        driver_mock.session_mock.run.assert_called_once()
        args, kwargs = driver_mock.session_mock.run.call_args
        query = args[0]
        assert "MATCH (a:Process {id: $from_id})" in query
        assert "MATCH (b:Material {id: $to_id})" in query
        assert "MERGE (a)-[r:USES_MATERIAL]->(b)" in query
        assert kwargs["from_id"] == "proc_1"
        assert kwargs["to_id"] == "mat_1"
        assert kwargs["props"] == {"confidence": 0.8}
    finally:
        app.db.neo4j.get_neo4j_driver = original_get_driver

@pytest.mark.asyncio
async def test_write_nodes_batch():
    driver_mock = MockNeo4jDriver()

    import app.db.neo4j
    original_get_driver = app.db.neo4j.get_neo4j_driver
    app.db.neo4j.get_neo4j_driver = MagicMock(return_value=driver_mock)

    try:
        writer = GraphWriter()
        nodes = [
            {"label": "Material", "id": "m1", "props": {"n": "name1"}},
            {"label": "Material", "id": "m2", "props": {"n": "name2"}},
            {"label": "Process", "id": "p1", "props": {"n": "proc1"}},
        ]
        await writer.write_nodes_batch(nodes)

        # Should be called once for Material and once for Process
        assert driver_mock.session_mock.run.call_count == 2
    finally:
        app.db.neo4j.get_neo4j_driver = original_get_driver

@pytest.mark.asyncio
async def test_write_relationships_batch():
    driver_mock = MockNeo4jDriver()

    import app.db.neo4j
    original_get_driver = app.db.neo4j.get_neo4j_driver
    app.db.neo4j.get_neo4j_driver = MagicMock(return_value=driver_mock)

    try:
        writer = GraphWriter()
        rels = [
            {
                "from": {"id": "p1", "label": "Process"},
                "to": {"id": "m1", "label": "Material"},
                "type": "USES_MATERIAL",
                "props": {"conf": 0.9}
            },
            {
                "from": {"id": "p1", "label": "Process"},
                "to": {"id": "m2", "label": "Material"},
                "type": "USES_MATERIAL",
                "props": {"conf": 0.8}
            },
        ]
        await writer.write_relationships_batch(rels)

        # All rels have same from/to labels and type -> 1 call
        driver_mock.session_mock.run.assert_called_once()
    finally:
        app.db.neo4j.get_neo4j_driver = original_get_driver
