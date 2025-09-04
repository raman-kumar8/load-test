@echo off
REM Test script for Windows PowerShell
echo Starting FastAPI Load Testing...

set BASE_URL=http://localhost:8080

echo 1. Health Check...
curl -s "%BASE_URL%/health"

echo.
echo 2. Light Load Test...
curl -s "%BASE_URL%/load/light"

echo.
echo 3. Medium Load Test (3 seconds)...
curl -s "%BASE_URL%/load/medium/3"

echo.
echo 4. Heavy Load Test...
curl -s -X POST "%BASE_URL%/load/heavy" -H "Content-Type: application/json" -d "{\"task_name\":\"test_heavy\",\"processing_time\":5,\"complexity\":\"medium\"}"

echo.
echo 5. Memory Allocation Test (20MB)...
curl -s "%BASE_URL%/memory/allocate/20"

echo.
echo 6. Concurrent Processing Test (10 tasks)...
curl -s "%BASE_URL%/concurrent/10"

echo.
echo 7. Background Task Test...
curl -s -X POST "%BASE_URL%/background/start" -H "Content-Type: application/json" -d "{\"id\":\"test_bg_task\",\"duration\":5,\"description\":\"Test background task\"}"

echo.
echo 8. Server Statistics...
curl -s "%BASE_URL%/stats"

echo.
echo 9. Clear Memory...
curl -s -X DELETE "%BASE_URL%/memory/clear"

echo.
echo Load testing completed!
