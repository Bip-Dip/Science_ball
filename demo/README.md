# MVP Demo Guide

This directory contains sample data and instructions for demonstrating the R&D Knowledge Map MVP.

## Sample Dataset
- `doc1_electrowinning.md`: Focuses on nickel electrowinning parameters (ideal for testing numeric extraction and RAG).
- `doc2_water_desalination.md`: General mining water treatment.
- `doc3_au_recovery.md`: Gold/Silver recovery processes.

## Demo Scenario
1. **Upload**: Use the frontend or `scripts/demo_seed.py` to upload documents.
2. **Search**: Search for "nickel electrowinning" to see hybrid search results.
3. **Answer**: Ask "What is the optimal catholyte circulation rate for nickel electrowinning?" to demonstrate RAG capabilities (evidence-based answer).
4. **Export**: Export the result to Markdown.

## Limitations
- Sample data is in Markdown for simplicity; PDF/DOCX can be uploaded similarly.
- YandexGPT API key must be configured in `.env` for Answer generation to work.
