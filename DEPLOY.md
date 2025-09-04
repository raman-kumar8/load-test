# Google Cloud Run Deployment Guide

## Deploy to Google Cloud Run

### Prerequisites
1. Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
2. Authenticate: `gcloud auth login`
3. Set project: `gcloud config set project YOUR_PROJECT_ID`
4. Enable required APIs:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   ```

### Quick Deploy Commands

```bash
# Build and deploy in one command
gcloud run deploy fastapi-load-test \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 100 \
  --concurrency 80 \
  --timeout 300

# Alternative: Build image first, then deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/fastapi-load-test
gcloud run deploy fastapi-load-test \
  --image gcr.io/YOUR_PROJECT_ID/fastapi-load-test \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 100 \
  --concurrency 80 \
  --timeout 300
```

### Autoscaling Configuration

Cloud Run automatically scales based on:
- **CPU utilization**: Target 60% CPU utilization
- **Concurrency**: Number of concurrent requests per instance
- **Request rate**: Incoming request volume

Key parameters for testing autoscaling:
- `--min-instances`: Minimum number of instances (0 for cost optimization)
- `--max-instances`: Maximum number of instances (adjust based on expected load)
- `--concurrency`: Max concurrent requests per instance (default: 80)
- `--cpu`: CPU allocation (1, 2, 4, 6, 8)
- `--memory`: Memory allocation (128Mi to 32Gi)

### Environment Variables for Production

```bash
gcloud run deploy fastapi-load-test \
  --set-env-vars="ENVIRONMENT=production,LOG_LEVEL=info"
```

### Load Testing Endpoints

After deployment, test these endpoints:

1. **Health Check**: `GET /health`
2. **Light Load**: `GET /load/light`
3. **Medium Load**: `GET /load/medium/5`
4. **Heavy Load**: `POST /load/heavy`
5. **Memory Test**: `GET /memory/allocate/50`
6. **Concurrent Test**: `GET /concurrent/20`

### Sample Load Testing Commands

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe fastapi-load-test --region=us-central1 --format="value(status.url)")

# Light load test
curl "$SERVICE_URL/load/light"

# Medium load test (5 seconds)
curl "$SERVICE_URL/load/medium/5"

# Heavy load test
curl -X POST "$SERVICE_URL/load/heavy" \
  -H "Content-Type: application/json" \
  -d '{"task_name":"stress_test","processing_time":10,"complexity":"complex"}'

# Memory allocation test
curl "$SERVICE_URL/memory/allocate/50"

# Concurrent processing test
curl "$SERVICE_URL/concurrent/20"

# Check stats
curl "$SERVICE_URL/stats"
```

### Monitoring Autoscaling

1. **Cloud Console**: Go to Cloud Run → Your Service → Metrics
2. **Command Line**: 
   ```bash
   gcloud logging read "resource.type=cloud_run_revision" --limit=50
   ```

Watch for:
- Instance count changes
- CPU and memory utilization
- Request latency
- Cold start times

### Load Testing with Artillery.js

Create a load testing script:

```bash
npm install -g artillery
```

Create `load-test.yml`:
```yaml
config:
  target: 'YOUR_CLOUD_RUN_URL'
  phases:
    - duration: 60
      arrivalRate: 5
    - duration: 120
      arrivalRate: 20
    - duration: 60
      arrivalRate: 50

scenarios:
  - name: "Mixed Load Test"
    weight: 100
    flow:
      - get:
          url: "/load/light"
      - get:
          url: "/load/medium/3"
      - post:
          url: "/load/heavy"
          json:
            task_name: "load_test"
            processing_time: 5
            complexity: "medium"
```

Run: `artillery run load-test.yml`
