#!/usr/bin/env python3
"""
CKEmpire System Test Script
Tüm sistemi test eder ve durumunu raporlar
"""

import requests
import json
import time
from datetime import datetime

def test_backend_health():
    """Backend sağlık kontrolü"""
    print("🔍 Backend Health Check...")
    try:
        response = requests.get("http://127.0.0.1:8007/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend çalışıyor: {data.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Backend hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend bağlantı hatası: {e}")
        return False

def test_finance_endpoints():
    """Finance endpoint'lerini test et"""
    print("\n🔍 Finance Endpoints Test...")
    endpoints = [
        ("/api/v1/finance/health", "GET"),
        ("/api/v1/finance/roi", "POST"),
        ("/api/v1/finance/cac-ltv", "POST"),
        ("/api/v1/finance/dcf", "POST")
    ]
    
    results = []
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://127.0.0.1:8007{endpoint}", timeout=5)
            else:
                response = requests.post(f"http://127.0.0.1:8007{endpoint}", json={}, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
                results.append(True)
            else:
                print(f"❌ {endpoint} - {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {endpoint} - Hata: {e}")
            results.append(False)
    
    return sum(results), len(results)

def test_analytics_endpoints():
    """Analytics endpoint'lerini test et"""
    print("\n🔍 Analytics Endpoints Test...")
    endpoints = [
        ("/api/v1/analytics/health", "GET"),
        ("/api/v1/analytics/track", "POST"),
        ("/api/v1/analytics/ab-test", "POST")
    ]
    
    results = []
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://127.0.0.1:8007{endpoint}", timeout=5)
            else:
                response = requests.post(f"http://127.0.0.1:8007{endpoint}", json={}, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
                results.append(True)
            else:
                print(f"❌ {endpoint} - {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {endpoint} - Hata: {e}")
            results.append(False)
    
    return sum(results), len(results)

def test_ai_endpoints():
    """AI endpoint'lerini test et"""
    print("\n🔍 AI Endpoints Test...")
    endpoints = [
        ("/api/v1/ai/health", "GET"),
        ("/api/v1/ai/generate-strategy", "POST")
    ]
    
    results = []
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"http://127.0.0.1:8007{endpoint}", timeout=5)
            else:
                response = requests.post(f"http://127.0.0.1:8007{endpoint}", json={}, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
                results.append(True)
            else:
                print(f"❌ {endpoint} - {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {endpoint} - Hata: {e}")
            results.append(False)
    
    return sum(results), len(results)

def test_frontend():
    """Frontend bağlantısını test et"""
    print("\n🔍 Frontend Test...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend çalışıyor")
            return True
        else:
            print(f"❌ Frontend hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend bağlantı hatası: {e}")
        return False

def generate_system_report():
    """Sistem raporu oluştur"""
    print("🚀 CKEmpire Sistem Testi Başlatılıyor...")
    print("=" * 60)
    
    # Test results
    backend_ok = test_backend_health()
    finance_passed, finance_total = test_finance_endpoints()
    analytics_passed, analytics_total = test_analytics_endpoints()
    ai_passed, ai_total = test_ai_endpoints()
    frontend_ok = test_frontend()
    
    # Calculate overall status
    total_endpoints = finance_total + analytics_total + ai_total
    passed_endpoints = finance_passed + analytics_passed + ai_passed
    
    print("\n" + "=" * 60)
    print("📊 SİSTEM DURUM RAPORU")
    print("=" * 60)
    
    print(f"Backend Server:     {'✅ Çalışıyor' if backend_ok else '❌ Çalışmıyor'}")
    print(f"Frontend Server:    {'✅ Çalışıyor' if frontend_ok else '❌ Çalışmıyor'}")
    print(f"Finance Endpoints:  {finance_passed}/{finance_total} ✅")
    print(f"Analytics Endpoints: {analytics_passed}/{analytics_total} ✅")
    print(f"AI Endpoints:       {ai_passed}/{ai_total} ✅")
    
    overall_success = backend_ok and frontend_ok and (passed_endpoints == total_endpoints)
    
    print(f"\nGenel Durum: {'✅ SİSTEM ÇALIŞIYOR' if overall_success else '❌ SİSTEM SORUNLU'}")
    
    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"system_test_report_{timestamp}.json"
    
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "backend_status": backend_ok,
        "frontend_status": frontend_ok,
        "finance_endpoints": {"passed": finance_passed, "total": finance_total},
        "analytics_endpoints": {"passed": analytics_passed, "total": analytics_total},
        "ai_endpoints": {"passed": ai_passed, "total": ai_total},
        "overall_success": overall_success
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Rapor kaydedildi: {report_file}")
    
    if overall_success:
        print("\n🎉 CKEmpire sistemi tamamen çalışır durumda!")
        print("📍 Backend: http://127.0.0.1:8007")
        print("📍 Frontend: http://localhost:3000")
        print("📍 API Docs: http://127.0.0.1:8007/docs")
    else:
        print("\n⚠️  Sistem sorunları tespit edildi. Lütfen kontrol edin.")
    
    return overall_success

if __name__ == "__main__":
    generate_system_report() 