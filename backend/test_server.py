#!/usr/bin/env python3
"""
Simple test server for CKEmpire
"""

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "CKEmpire API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("🚀 Starting CKEmpire Test Server...")
    print("📍 URL: http://127.0.0.1:8006")
    uvicorn.run(app, host="127.0.0.1", port=8006) 