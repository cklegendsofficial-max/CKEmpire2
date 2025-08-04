#!/usr/bin/env python3
"""
Very simple test server
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Starting simple server...")
    uvicorn.run(app, host="127.0.0.1", port=8002) 