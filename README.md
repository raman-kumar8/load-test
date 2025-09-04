# FastAPI Load Testing Server

A FastAPI server designed for testing autoscaling and load handling on Google Cloud Run.

## Features

- **Multiple Load Testing Endpoints**: Light, medium, and heavy computational loads
- **Memory Allocation Testing**: Test memory-based autoscaling
- **Concurrent Processing**: Test parallel request handling
- **Background Tasks**: Async task processing
- **Health Checks**: Cloud Run compatible health endpoints
- **Request Statistics**: Monitor server performance
- **Docker Ready**: Optimized Dockerfile for Cloud Run

## Local Development

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

The server will be available at `http://localhost:8080`

### Using Docker

```bash
# Build the image
docker build -t fastapi-load-test .

# Run the container
docker run -p 8080:8080 fastapi-load-test
```

## API Endpoints

### Health & Status
- `GET /` - Basic health check
- `GET /health` - Detailed health check for Cloud Run
- `GET /stats` - Server statistics and metrics

### Load Testing
- `GET /load/light` - Light computational load (quick response)
- `GET /load/medium/{duration}` - Medium load with configurable duration
- `POST /load/heavy` - Heavy computational load with complexity options

### Memory Testing
- `GET /memory/allocate/{mb}` - Allocate specified MB of memory
- `DELETE /memory/clear` - Clear allocated memory blocks

### Concurrency Testing
- `GET /concurrent/{count}` - Test concurrent request processing
- `POST /background/start` - Start background tasks

## Load Testing Examples

### Light Load
```bash
curl http://localhost:8080/load/light
```

### Medium Load (5 seconds)
```bash
curl http://localhost:8080/load/medium/5
```

### Heavy Load
```bash
curl -X POST http://localhost:8080/load/heavy \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "stress_test",
    "processing_time": 10,
    "complexity": "complex"
  }'
```

### Memory Allocation (50MB)
```bash
curl http://localhost:8080/memory/allocate/50
```

### Concurrent Processing (20 tasks)
```bash
curl http://localhost:8080/concurrent/20
```

## Request Body Schemas

### Heavy Load Request
```json
{
  "task_name": "string",
  "processing_time": 5,
  "complexity": "simple|medium|complex"
}
```

### Background Task Request
```json
{
  "id": "string",
  "duration": 10,
  "description": "optional description"
}
```

## Environment Variables

- `PORT`: Server port (default: 8080)

## Google Cloud Run Deployment

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

Quick deploy:
```bash
gcloud run deploy fastapi-load-test \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 100 \
  --concurrency 80
```

## Autoscaling Testing Strategy

1. **Start with light load** to establish baseline
2. **Gradually increase load** using medium and heavy endpoints
3. **Test memory allocation** to trigger memory-based scaling
4. **Use concurrent endpoints** to test request concurrency limits
5. **Monitor Cloud Run metrics** for scaling behavior

## Performance Characteristics

- **Light Load**: ~1ms response time, minimal CPU usage
- **Medium Load**: Configurable duration, moderate CPU usage
- **Heavy Load**: High CPU usage, configurable complexity
- **Memory Allocation**: Tests memory-based autoscaling triggers
- **Concurrent Processing**: Tests parallel request handling

## Monitoring

Use the `/stats` endpoint to monitor:
- Total requests processed
- Memory usage
- Active background tasks
- Server uptime

Perfect for testing Google Cloud Run's autoscaling capabilities!
