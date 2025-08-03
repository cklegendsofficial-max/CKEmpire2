#!/usr/bin/env python3
"""
Simple test server for analytics endpoints
"""

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from analytics import analytics_manager
from routers.analytics import router as analytics_router

app = FastAPI(title="Analytics Test Server")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include analytics router
app.include_router(analytics_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Analytics Test Server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "analytics": "available"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Analytics Test Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 