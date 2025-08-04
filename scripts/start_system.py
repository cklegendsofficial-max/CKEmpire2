#!/usr/bin/env python3
"""
CKEmpire System Starter
"""

import subprocess
import time
import requests
import sys
import os

def start_backend():
    """Start backend server"""
    print("🚀 Starting Backend Server...")
    try:
        # Create a simple FastAPI server
        server_code = '''
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def root():
    return {"message": "CKEmpire API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting CKEmpire Backend...")
    uvicorn.run(app, host="127.0.0.1", port=8012)
'''
        
        # Write server code to temporary file
        with open("temp_server.py", "w") as f:
            f.write(server_code)
        
        # Start server in background
        process = subprocess.Popen([sys.executable, "temp_server.py"])
        
        # Wait for server to start
        time.sleep(3)
        
        # Test server
        try:
            response = requests.get("http://127.0.0.1:8012/", timeout=5)
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
        os.chdir("../frontend")
        
        # Start npm server
        process = subprocess.Popen(["npm", "start"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(10)
        
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

def main():
    print("🎯 CKEmpire System Starter")
    print("=" * 50)
    
    # Start backend
    backend_ok = start_backend()
    
    # Start frontend
    frontend_ok = start_frontend()
    
    print("\n" + "=" * 50)
    print("📊 SYSTEM STATUS")
    print("=" * 50)
    print(f"Backend:  {'✅ Running' if backend_ok else '❌ Failed'}")
    print(f"Frontend: {'✅ Running' if frontend_ok else '❌ Failed'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 CKEmpire system is running!")
        print("📍 Backend: http://127.0.0.1:8012")
        print("📍 Frontend: http://localhost:3000")
    else:
        print("\n⚠️  System has issues")
    
    return backend_ok and frontend_ok

if __name__ == "__main__":
    main() 