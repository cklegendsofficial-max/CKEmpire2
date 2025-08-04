#!/usr/bin/env python3
"""
Quick System Test
"""

import requests
import time

def test_backend():
    """Test backend server"""
    print("🔍 Testing Backend...")
    try:
        response = requests.get("http://127.0.0.1:8007/", timeout=3)
        if response.status_code == 200:
            print("✅ Backend is running")
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
        response = requests.get("http://localhost:3000", timeout=3)
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
    print("🚀 Quick System Test")
    print("=" * 40)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 40)
    print("📊 RESULTS")
    print("=" * 40)
    print(f"Backend:  {'✅ OK' if backend_ok else '❌ FAIL'}")
    print(f"Frontend: {'✅ OK' if frontend_ok else '❌ FAIL'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 System is working!")
        print("📍 Backend: http://127.0.0.1:8007")
        print("📍 Frontend: http://localhost:3000")
    else:
        print("\n⚠️  System has issues")
    
    return backend_ok and frontend_ok

if __name__ == "__main__":
    main() 