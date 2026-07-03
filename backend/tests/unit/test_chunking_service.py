import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.ingestion.chunking_service import ChunkingService
from app.repositories.chunks import ChunksRepository
from app.settings import settings


@pytest.fixture
def mock_repo():
    return MagicMock(spec=ChunksRepository)


@pytest.fixture
def service(mock_repo):
    return ChunkingService(chunks_repository=mock_repo)


def test_split_text_basic(service):
    # Setup: 10 chars size, 2 overlap -> step = 8
    settings.chunk_size = 10
    settings.chunk_overlap = 2

    text = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ" # 36 chars
    # Chunk 1: [0:10] "0123456789"
    # Chunk 2: [8:18] "89ABCDEFGH"
    # Chunk 3: [16:26] "PQRSTUVWXY" ... wait, let's calculate exactly.
    # start=0, end=10; start=8, end=18; start=16, end=26; start=24, end=34; start=32, end=42(end)

    chunks = service.split_text(text)
    assert len(chunks) == 5
    assert chunks[0] == "0123456789"
    assert chunks[1] == "89ABCDEFGH"
    assert chunks[-1].endswith("YZ")


def test_split_text_overlap_exact(service):
    settings.chunk_size = 10
    settings.chunk_overlap = 5

    text = "abcdefghij" + "klmno" + "pqrst" # 20 chars
    # Chunk 1: [0:10] abcdefghij
    # start = 10 - 5 = 5. end = 5 + 10 = 15.
    # Chunk 2: [5:15] fghij klmno
    # start = 15 - 5 = 10. end = 10 + 10 = 20.
    # Chunk 3: [10:20] klmnopqrst

    chunks = service.split_text(text)
    assert len(chunks) == 3
    assert chunks[0] == "abcdefghij"
    assert chunks[1] == "fghijklmno"
    assert chunks[2] == "klmnopqrst"


def test_split_text_empty_and_short(service):
    settings.chunk_size = 100
    settings.chunk_overlap = 20

    assert service.split_text("") == []
    assert service.split_text("short") == ["short"]


def test_split_text_exact_size(service):
    settings.chunk_size = 10
    settings.chunk_overlap = 2
    text = "0123456789"
    assert service.split_text(text) == ["0123456789"]


@pytest.mark.asyncio
async def test_process_document_integration(service, mock_repo):
    session = AsyncMock()
    doc_id = uuid4()
    text = "This is a long text that should be chunked into multiple pieces."
    access_level = "internal"

    # Set small size to force chunks
    settings.chunk_size = 10
    settings.chunk_overlap = 2

    await service.process_document(session, doc_id, text, access_level)

    # Verify idempotency: delete first
    mock_repo.delete_by_document.assert_called_once_with(session, doc_id)

    # Verify bulk creation
    mock_repo.create_many.assert_called_once()
    args, _ = mock_repo.create_many.call_args
    chunks_data = args[1]
    assert len(chunks_data) > 1
    assert chunks_data[0]["document_id"] == doc_id
    assert chunks_data[0]["access_level"] == access_level
    assert chunks_data[0]["chunk_index"] == 0
