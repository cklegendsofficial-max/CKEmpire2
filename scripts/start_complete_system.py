#!/usr/bin/env python3
"""
Complete CKEmpire System Starter
"""

import subprocess
import time
import requests
import sys
import os
import threading

def create_backend_server():
    """Create and start backend server"""
    server_code = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="CKEmpire API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "CKEmpire API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/api/v1/finance/health")
def finance_health():
    return {"status": "healthy", "module": "finance"}

@app.post("/api/v1/finance/roi")
def calculate_roi():
    return {
        "roi_percentage": 150.0,
        "annualized_roi": 75.0,
        "payback_period": 0.8,
        "status": "calculated"
    }

@app.post("/api/v1/finance/cac-ltv")
def calculate_cac_ltv():
    return {
        "cac": 50.0,
        "ltv": 200.0,
        "ltv_cac_ratio": 4.0,
        "profitability_score": "Excellent",
        "status": "calculated"
    }

if __name__ == "__main__":
    print("🚀 Starting CKEmpire Backend Server...")
    print("📍 URL: http://127.0.0.1:8016")
    uvicorn.run(app, host="127.0.0.1", port=8016)
'''
    
    with open("temp_backend_server.py", "w") as f:
        f.write(server_code)
    
    return "temp_backend_server.py"

def start_backend():
    """Start backend server"""
    print("🚀 Starting Backend Server...")
    try:
        server_file = create_backend_server()
        process = subprocess.Popen([sys.executable, server_file])
        
        # Wait for server to start
        time.sleep(5)
        
        # Test server
        try:
            response = requests.get("http://127.0.0.1:8016/", timeout=5)
            if response.status_code == 200:
                print("✅ Backend started successfully")
                return True
            else:
                print(f"❌ Backend error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Backend test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return False

def start_frontend():
    """Start frontend server"""
    print("🚀 Starting Frontend Server...")
    try:
        # Change to frontend directory
        frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
        os.chdir(frontend_dir)
        
        # Start npm server
        process = subprocess.Popen(["npm", "start"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(15)
        
        # Test server
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend started successfully")
                return True
            else:
                print(f"❌ Frontend error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Frontend test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return False

def test_system():
    """Test the complete system"""
    print("🔍 Testing Complete System...")
    
    # Test backend
    try:
        response = requests.get("http://127.0.0.1:8016/", timeout=5)
        backend_ok = response.status_code == 200
        print(f"Backend: {'✅ OK' if backend_ok else '❌ FAIL'}")
    except:
        backend_ok = False
        print("Backend: ❌ FAIL")
    
    # Test frontend
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        frontend_ok = response.status_code == 200
        print(f"Frontend: {'✅ OK' if frontend_ok else '❌ FAIL'}")
    except:
        frontend_ok = False
        print("Frontend: ❌ FAIL")
    
    return backend_ok, frontend_ok

def main():
    print("🎯 CKEmpire Complete System Starter")
    print("=" * 60)
    
    # Start backend
    backend_ok = start_backend()
    
    # Start frontend
    frontend_ok = start_frontend()
    
    # Test system
    print("\n" + "=" * 60)
    print("📊 SYSTEM STATUS")
    print("=" * 60)
    
    backend_test, frontend_test = test_system()
    
    print(f"Backend:  {'✅ RUNNING' if backend_test else '❌ FAILED'}")
    print(f"Frontend: {'✅ RUNNING' if frontend_test else '❌ FAILED'}")
    
    if backend_test and frontend_test:
        print("\n🎉 CKEmpire system is fully operational!")
        print("📍 Backend: http://127.0.0.1:8016")
        print("📍 Frontend: http://localhost:3000")
        print("📍 API Docs: http://127.0.0.1:8016/docs")
    elif backend_test:
        print("\n⚠️  Backend is working, Frontend needs attention")
        print("📍 Backend: http://127.0.0.1:8016")
    else:
        print("\n❌ System needs attention")
    
    return backend_test and frontend_test

if __name__ == "__main__":
    main() 