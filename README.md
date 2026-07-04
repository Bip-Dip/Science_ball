# R&D Knowledge Map

A system for searching, analyzing, and building a knowledge map of mining and metallurgical research.

## Quick Start (One-Machine Setup)

### 1. Environment Configuration
Copy `.env.example` to `.env` and fill in your Yandex Cloud credentials:
```bash
YANDEX_API_KEY=your_key
YANDEX_FOLDER_ID=your_folder_id
```

### 2. Infrastructure Startup
Launch all services using Docker Compose:
```bash
docker compose up -d
```

### 3. Seed Demo Data
Run the seed script to populate the system with a few sample documents:
```bash
# Install dependencies for seed script
pip install httpx
python scripts/demo_seed.py
```

### 4. Verify MVP Flow
Run the smoke test script to ensure core components are working:
```bash
./scripts/demo_smoke.sh
```

### 5. Access the Application
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000` (Swagger docs at `/docs`)

## Demo Scenario
1. Upload a technical document via the UI.
2. Search for specific metallurgical processes.
3. Ask complex questions and get answers with citations.
4. Export results to Markdown.
