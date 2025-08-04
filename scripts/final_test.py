#!/usr/bin/env python3
"""
Final CKEmpire System Test
"""

import requests
import time

def test_backend():
    """Test backend server"""
    print("🔍 Testing Backend...")
    try:
        response = requests.get("http://127.0.0.1:8012/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend connection error: {e}")
        return False

def test_frontend():
    """Test frontend server"""
    print("🔍 Testing Frontend...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running")
            return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend connection error: {e}")
        return False

def main():
    print("🚀 Final CKEmpire System Test")
    print("=" * 50)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)
    print(f"Backend:  {'✅ RUNNING' if backend_ok else '❌ FAILED'}")
    print(f"Frontend: {'✅ RUNNING' if frontend_ok else '❌ FAILED'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 CKEmpire system is fully operational!")
        print("📍 Backend: http://127.0.0.1:8012")
        print("📍 Frontend: http://localhost:3000")
        print("📍 API Docs: http://127.0.0.1:8012/docs")
    elif backend_ok:
        print("\n⚠️  Backend is working, Frontend needs attention")
        print("📍 Backend: http://127.0.0.1:8012")
    else:
        print("\n❌ System needs attention")
    
    return backend_ok and frontend_ok

if __name__ == "__main__":
    main() 