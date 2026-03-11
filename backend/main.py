"""
AURA - Student Wellness Intelligence System
FastAPI backend with real-time SSE feed

Main endpoints:
- /api/students - Student management
- /api/alerts - Alert management & identity reveal
- /api/feed/live - Server-Sent Events for real-time updates
- /api/predict/run - Trigger model predictions
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
import asyncio
from datetime import datetime
from typing import AsyncGenerator
import json

from backend.db import get_db, close_db_connection
from backend.routers import students, alerts


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    print("🚀 AURA API starting...")
    print(f"📅 {datetime.now().isoformat()}")
    yield
    print("🛑 AURA API shutting down...")
    await close_db_connection()


# Create FastAPI app
app = FastAPI(
    title="AURA API",
    description="Student Wellness Intelligence System - Privacy-first behavioral analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "https://*.vercel.app",  # Vercel deployments
        "https://*.onrender.com",  # Render deployments
        "https://*.railway.app",  # Railway deployments
        # Add your production domain here
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(students.router)
app.include_router(alerts.router)


@app.get("/")
async def root():
    """API health check."""
    return {
        "service": "AURA API",
        "status": "operational",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }


@app.get("/api/feed/live")
async def live_feed(db = Depends(get_db)) -> StreamingResponse:
    """
    Server-Sent Events (SSE) stream for real-time risk prediction updates.
    
    Frontend connects with:
    const eventSource = new EventSource('http://localhost:8000/api/feed/live');
    eventSource.onmessage = (event) => { ... };
    """
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for new risk predictions."""
        
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        last_check = datetime.now()
        
        while True:
            try:
                # Check for new risk predictions
                cursor = db.risk_predictions.find(
                    {'pred_date': {'$gte': last_check}}
                ).sort('pred_date', -1).limit(10)
                
                new_predictions = []
                async for pred in cursor:
                    pred['_id'] = str(pred['_id'])
                    pred['pred_date'] = pred['pred_date'].isoformat()
                    new_predictions.append(pred)
                
                if new_predictions:
                    # Send new predictions
                    event_data = {
                        'type': 'new_predictions',
                        'count': len(new_predictions),
                        'predictions': new_predictions,
                        'timestamp': datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(event_data)}\n\n"
                
                # Update last check time
                last_check = datetime.now()
                
                # Keep-alive ping every 15 seconds
                yield f": ping\n\n"
                
                await asyncio.sleep(15)
                
            except asyncio.CancelledError:
                print("SSE connection closed by client")
                break
            except Exception as e:
                print(f"SSE error: {e}")
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                await asyncio.sleep(5)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/predict/run")
async def run_predictions(db = Depends(get_db)):
    """
    Trigger model predictions on latest behavioral_logs.
    
    In production, this would:
    1. Load trained model from models/saved/
    2. Run feature engineering on recent behavioral_logs
    3. Generate predictions
    4. Upsert into risk_predictions collection
    
    For now, returns a stub response.
    """
    
    # Count recent behavioral logs
    recent_count = await db.behavioral_logs.count_documents({})
    student_count = await db.students.count_documents({})
    
    # TODO: Integrate with models/train.py pipeline
    # from models.features import extract_features
    # from models.train import load_model
    # predictions = model.predict(features)
    
    return {
        'status': 'completed',
        'message': 'Model predictions triggered',
        'behavioral_logs_processed': recent_count,
        'students_analyzed': student_count,
        'timestamp': datetime.now().isoformat(),
        'note': 'Full model integration pending - see models/train.py'
    }


@app.get("/health")
async def health_check(db = Depends(get_db)):
    """Deep health check including MongoDB connection."""
    try:
        # Test MongoDB connection
        await db.command('ping')
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "api": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
