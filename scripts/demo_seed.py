import asyncio
import httpx
import os
from pathlib import Path

# Configuration - adjust to match your environment
BACKEND_URL = "http://localhost:8000"
DEMO_DOCS_DIR = Path("demo/sample_documents")

SAMPLE_DATA = [
    {
        "file": "doc1_electrowinning.md",
        "title": "Technical Review of Nickel Electrowinning Processes",
        "source_type": "publication",
        "access_level": "internal",
        "language": "en",
        "year": 2023,
    },
    {
        "file": "doc2_water_desalination.md",
        "title": "Water Desalination in Mining Operations",
        "source_type": "publication",
        "access_level": "public",
        "language": "en",
        "year": 2022,
    },
    {
        "file": "doc3_au_recovery.md",
        "title": "Gold and Silver Recovery from Refractory Ores",
        "source_type": "report",
        "access_level": "internal",
        "language": "en",
        "year": 2024,
    },
]

async def upload_document(client: httpx.AsyncClient, doc_info: dict):
    file_path = DEMO_DOCS_DIR / doc_info["file"]
    if not file_path.exists():
        print(f"File {file_path} not found, skipping...")
        return

    files = {"file": (doc_info["file"], open(file_path, "rb"), "text/markdown")}
    data = {
        "title": doc_info["title"],
        "source_type": doc_info["source_type"],
        "access_level": doc_info["access_level"],
        "language": doc_info["language"],
        "year": doc_info["year"],
    }

    try:
        response = await client.post(f"{BACKEND_URL}/api/v1/documents/upload", data=data, files=files)
        response.raise_for_status()
        print(f"Successfully uploaded {doc_info['file']}")
    except Exception as e:
        print(f"Failed to upload {doc_info['file']}: {e}")

async def main():
    async with httpx.AsyncClient(timeout=30.0) as client:
        for doc in SAMPLE_DATA:
            await upload_document(client, doc)

if __name__ == "__main__":
    asyncio.run(main())
