import asyncio
import time
import random
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Load Testing FastAPI Server",
    description="A FastAPI server designed for testing autoscaling on Google Cloud Run",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demonstration
memory_store = {}
request_count = 0

class Task(BaseModel):
    id: str
    duration: int
    description: Optional[str] = None

class ProcessingRequest(BaseModel):
    task_name: str
    processing_time: int = 5
    complexity: str = "simple"

@app.get("/")
async def root():
    """Health check endpoint"""
    global request_count
    request_count += 1
    return {
        "message": "FastAPI Load Testing Server is running!",
        "status": "healthy",
        "request_count": request_count,
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """Detailed health check for Cloud Run"""
    return {
        "status": "healthy",
        "uptime": time.time(),
        "memory_usage": len(memory_store),
        "total_requests": request_count
    }

@app.get("/load/light")
async def light_load():
    """Light computational load - quick response"""
    global request_count
    request_count += 1
    
    # Simulate light work
    start_time = time.time()
    result = sum(i for i in range(1000))
    end_time = time.time()
    
    return {
        "load_type": "light",
        "result": result,
        "processing_time": end_time - start_time,
        "request_id": request_count
    }

@app.get("/load/medium/{duration}")
async def medium_load(duration: int = 3):
    """Medium computational load with configurable duration"""
    global request_count
    request_count += 1
    
    if duration > 30:
        raise HTTPException(status_code=400, detail="Duration cannot exceed 30 seconds")
    
    start_time = time.time()
    
    # Simulate medium work
    for _ in range(duration):
        await asyncio.sleep(1)
        # Some CPU work
        sum(i * i for i in range(10000))
    
    end_time = time.time()
    
    return {
        "load_type": "medium",
        "duration_requested": duration,
        "actual_processing_time": end_time - start_time,
        "request_id": request_count
    }

@app.post("/load/heavy")
async def heavy_load(request: ProcessingRequest):
    """Heavy computational load - stress test endpoint"""
    global request_count
    request_count += 1
    
    start_time = time.time()
    
    # Simulate heavy computational work
    if request.complexity == "simple":
        iterations = 50000
    elif request.complexity == "medium":
        iterations = 100000
    else:  # complex
        iterations = 200000
    
    result = 0
    for i in range(iterations):
        result += i * random.random()
        if i % 10000 == 0:
            await asyncio.sleep(0.01)  # Allow other requests to be processed
    
    # Simulate some processing time
    await asyncio.sleep(request.processing_time)
    
    end_time = time.time()
    
    # Store result in memory to simulate memory usage
    memory_store[f"task_{request_count}"] = {
        "result": result,
        "timestamp": time.time(),
        "complexity": request.complexity
    }
    
    return {
        "load_type": "heavy",
        "task_name": request.task_name,
        "complexity": request.complexity,
        "processing_time": end_time - start_time,
        "result_preview": str(result)[:50],
        "request_id": request_count,
        "memory_items": len(memory_store)
    }

@app.get("/memory/allocate/{mb}")
async def allocate_memory(mb: int):
    """Allocate memory to test memory-based autoscaling"""
    global request_count
    request_count += 1
    
    if mb > 100:
        raise HTTPException(status_code=400, detail="Cannot allocate more than 100MB")
    
    # Allocate memory
    size = mb * 1024 * 1024  # Convert MB to bytes
    data = bytearray(size)
    
    # Fill with some data
    for i in range(0, size, 1024):
        data[i:i+10] = b"test_data_"
    
    memory_store[f"memory_block_{request_count}"] = data
    
    return {
        "allocated_mb": mb,
        "total_memory_blocks": len([k for k in memory_store.keys() if k.startswith("memory_block_")]),
        "request_id": request_count
    }

@app.delete("/memory/clear")
async def clear_memory():
    """Clear allocated memory"""
    global memory_store
    memory_blocks = [k for k in memory_store.keys() if k.startswith("memory_block_")]
    for key in memory_blocks:
        del memory_store[key]
    
    return {
        "message": "Memory cleared",
        "blocks_cleared": len(memory_blocks),
        "remaining_items": len(memory_store)
    }

@app.get("/stats")
async def get_stats():
    """Get server statistics"""
    return {
        "total_requests": request_count,
        "memory_items": len(memory_store),
        "memory_blocks": len([k for k in memory_store.keys() if k.startswith("memory_block_")]),
        "task_results": len([k for k in memory_store.keys() if k.startswith("task_")]),
        "uptime": time.time()
    }

async def background_task(name: str, duration: int):
    """Background task for testing async processing"""
    logger.info(f"Starting background task: {name}")
    await asyncio.sleep(duration)
    logger.info(f"Completed background task: {name}")

@app.post("/background/start")
async def start_background_task(background_tasks: BackgroundTasks, task: Task):
    """Start a background task"""
    background_tasks.add_task(background_task, task.id, task.duration)
    return {
        "message": f"Background task {task.id} started",
        "duration": task.duration,
        "description": task.description
    }

@app.get("/concurrent/{count}")
async def test_concurrent(count: int):
    """Test concurrent processing"""
    if count > 50:
        raise HTTPException(status_code=400, detail="Cannot process more than 50 concurrent tasks")
    
    async def worker(worker_id: int):
        await asyncio.sleep(random.uniform(1, 3))
        return f"Worker {worker_id} completed"
    
    start_time = time.time()
    tasks = [worker(i) for i in range(count)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    return {
        "concurrent_tasks": count,
        "processing_time": end_time - start_time,
        "results": results[:5],  # Show first 5 results
        "total_results": len(results)
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
