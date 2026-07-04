#!/bin/bash

# Configuration
BACKEND_URL="http://localhost:8000"

echo "--- Starting Smoke Test ---"

# 1. Health Check
echo -n "Checking Backend Health... "
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/api/v1/health)
if [ "$RESPONSE" == "200" ]; then
    echo "OK"
else
    echo "FAILED ($RESPONSE)"
    exit 1
fi

# 2. Search Test (Simple keyword search)
echo -n "Testing Basic Search... "
SEARCH_RESP=$(curl -s -X POST $BACKEND_URL/api/v1/search     -H "Content-Type: application/json"     -d '{"query": "nickel electrowinning", "filters": {}}')

if [[ "$SEARCH_RESP" == *"evidence"* ]]; then
    echo "OK"
else
    echo "FAILED (No evidence found)"
    exit 1
fi

# 3. Answer Test (RAG flow)
echo -n "Testing RAG Answer... "
ANSWER_RESP=$(curl -s -X POST $BACKEND_URL/api/v1/answers     -H "Content-Type: application/json"     -d '{"query": "What is the optimal catholyte circulation rate for nickel electrowinning?", "options": {}}')

if [[ "$ANSWER_RESP" == *"short_answer"* ]]; then
    echo "OK"
else
    echo "FAILED (No answer generated)"
    exit 1
fi

echo "--- Smoke Test Passed! ---"
