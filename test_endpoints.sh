#!/bin/bash

# Test script for local development
echo "Starting FastAPI Load Testing..."

BASE_URL="http://localhost:8080"

echo "1. Health Check..."
curl -s "$BASE_URL/health" | python -m json.tool

echo -e "\n2. Light Load Test..."
curl -s "$BASE_URL/load/light" | python -m json.tool

echo -e "\n3. Medium Load Test (3 seconds)..."
curl -s "$BASE_URL/load/medium/3" | python -m json.tool

echo -e "\n4. Heavy Load Test..."
curl -s -X POST "$BASE_URL/load/heavy" \
  -H "Content-Type: application/json" \
  -d '{"task_name":"test_heavy","processing_time":5,"complexity":"medium"}' | python -m json.tool

echo -e "\n5. Memory Allocation Test (20MB)..."
curl -s "$BASE_URL/memory/allocate/20" | python -m json.tool

echo -e "\n6. Concurrent Processing Test (10 tasks)..."
curl -s "$BASE_URL/concurrent/10" | python -m json.tool

echo -e "\n7. Background Task Test..."
curl -s -X POST "$BASE_URL/background/start" \
  -H "Content-Type: application/json" \
  -d '{"id":"test_bg_task","duration":5,"description":"Test background task"}' | python -m json.tool

echo -e "\n8. Server Statistics..."
curl -s "$BASE_URL/stats" | python -m json.tool

echo -e "\n9. Clear Memory..."
curl -s -X DELETE "$BASE_URL/memory/clear" | python -m json.tool

echo -e "\nLoad testing completed!"
