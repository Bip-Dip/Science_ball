import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Sequence

from app.search.indexing_service import IndexingService
from app.models.document import Document
from app.models.chunk import Chunk
from app.models.entity import Entity
from app.models.fact import Fact, NumericCondition
import uuid

@pytest.fixture
def mock_es():
    return AsyncMock()

@pytest.fixture
def indexing_service(monkeypatch, mock_es):
    monkeypatch.setattr("app.search.indexing_service.get_elasticsearch", lambda: mock_es)
    return IndexingService()

@pytest.fixture
def sample_doc():
    return Document(
        id=uuid.uuid4(),
        title="Test Doc",
        source_type="publication",
        language="en",
        year=2023,
        access_level="internal",
        minio_bucket="test-bucket",
        minio_object_key="test-key",
        checksum="sum"
    )

@pytest.fixture
def sample_chunks(sample_doc):
    return [
        Chunk(
            id=uuid.uuid4(),
            document_id=sample_doc.id,
            chunk_index=0,
            text="Chunk 1 text",
            language="en",
            page=1,
            section="Intro",
            access_level="internal"
        ),
        Chunk(
            id=uuid.uuid4(),
            document_id=sample_doc.id,
            chunk_index=1,
            text="Chunk 2 text",
            language="en",
            page=1,
            section="Intro",
            access_level="internal"
        )
    ]

@pytest.fixture
def sample_entities(sample_doc):
    return [
        Entity(
            id=uuid.uuid4(),
            document_id=sample_doc.id,
            entity_type="Material",
            name="Nickel",
            canonical_name="nickel",
            aliases={"Ni": "nickel"},
            confidence=1.0
        )
    ]

@pytest.fixture
def sample_facts(sample_doc):
    return [
        Fact(
            id=uuid.uuid4(),
            subject_id="proc_1",
            subject_type="Process",
            predicate="USES_MATERIAL",
            object_id="mat_1",
            object_type="Material",
            source_document_id=sample_doc.id,
            source_chunk_id=None,
            confidence=0.9,
            verification_status="machine_extracted"
        )
    ]

@pytest.mark.asyncio
async def test_index_document(indexing_service, mock_es, sample_doc):
    await indexing_service.index_document(sample_doc)

    mock_es.index.assert_called_once()
    args = mock_es.index.call_args.kwargs
    assert args["index"] == "rd_docs_v1"
    assert args["id"] == str(sample_doc.id)
    assert args["document"]["title"] == "Test Doc"
    assert args["document"]["access_level"] == "internal"

@pytest.mark.asyncio
async def test_index_chunks(indexing_service, sample_chunks, sample_doc):
    with patch("app.search.indexing_service.async_bulk", new_callable=AsyncMock) as mock_bulk:
        doc_meta = {"year": 2023, "source_type": "publication", "access_level": "internal"}
        await indexing_service.index_chunks(sample_chunks, doc_meta)

        mock_bulk.assert_called_once()
        actions = mock_bulk.call_args[0][1]
        assert len(actions) == 2
        assert actions[0]["_index"] == "rd_chunks_v1"
        assert actions[0]["_source"]["text"] == "Chunk 1 text"
        assert actions[0]["_source"]["access_level"] == "internal"

@pytest.mark.asyncio
async def test_index_entities(indexing_service, sample_entities):
    with patch("app.search.indexing_service.async_bulk", new_callable=AsyncMock) as mock_bulk:
        doc_meta = {"access_level": "internal"}
        await indexing_service.index_entities(sample_entities, doc_meta)

        mock_bulk.assert_called_once()
        actions = mock_bulk.call_args[0][1]
        assert len(actions) == 1
        assert actions[0]["_index"] == "rd_entities_v1"
        assert actions[0]["_source"]["name"] == "Nickel"
        assert actions[0]["_source"]["access_level"] == "internal"

@pytest.mark.asyncio
async def test_index_facts(indexing_service, sample_facts):
    with patch("app.search.indexing_service.async_bulk", new_callable=AsyncMock) as mock_bulk:
        doc_meta = {"access_level": "internal"}
        numeric_conditions = []
        await indexing_service.index_facts(sample_facts, numeric_conditions, doc_meta)

        mock_bulk.assert_called_once()
        actions = mock_bulk.call_args[0][1]
        assert len(actions) == 1
        assert actions[0]["_index"] == "rd_facts_v1"
        assert actions[0]["_source"]["predicate"] == "USES_MATERIAL"
        assert actions[0]["_source"]["access_level"] == "internal"
