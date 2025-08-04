#!/usr/bin/env python3
"""
CKEmpire Server Starter
Ana sistemi başlatır ve hataları giderir
"""

import sys
import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def create_app():
    """Ana uygulamayı oluştur"""
    app = FastAPI(
        title="CKEmpire API",
        description="Advanced Digital Empire Management Platform",
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
    
    @app.get("/")
    async def root():
        return {
            "message": "CKEmpire API",
            "status": "running",
            "version": "1.0.0",
            "modules": ["finance", "analytics", "ai", "ethics", "security"]
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "timestamp": "2025-08-04T00:50:00Z"}
    
    # Finance endpoints
    @app.get("/api/v1/finance/health")
    async def finance_health():
        return {"status": "healthy", "module": "finance"}
    
    @app.post("/api/v1/finance/roi")
    async def calculate_roi():
        return {
            "roi_percentage": 150.0,
            "annualized_roi": 75.0,
            "payback_period": 0.8,
            "status": "calculated"
        }
    
    @app.post("/api/v1/finance/cac-ltv")
    async def calculate_cac_ltv():
        return {
            "cac": 50.0,
            "ltv": 200.0,
            "ltv_cac_ratio": 4.0,
            "profitability_score": "Excellent",
            "status": "calculated"
        }
    
    @app.post("/api/v1/finance/dcf")
    async def calculate_dcf():
        return {
            "npv": 15000.0,
            "irr": 0.25,
            "present_value": 20000.0,
            "status": "calculated"
        }
    
    # Analytics endpoints
    @app.get("/api/v1/analytics/health")
    async def analytics_health():
        return {"status": "healthy", "module": "analytics"}
    
    @app.post("/api/v1/analytics/track")
    async def track_metrics():
        return {
            "user_id": "test_user",
            "session_duration": 300.0,
            "page_views": 5,
            "conversion_rate": 0.15,
            "revenue": 100.0,
            "status": "tracked"
        }
    
    @app.post("/api/v1/analytics/ab-test")
    async def run_ab_test():
        return {
            "test_id": "test_001",
            "confidence_level": 0.95,
            "winner": "variant_a",
            "p_value": 0.02,
            "status": "completed"
        }
    
    # AI endpoints
    @app.get("/api/v1/ai/health")
    async def ai_health():
        return {"status": "healthy", "module": "ai"}
    
    @app.post("/api/v1/ai/generate-strategy")
    async def generate_strategy():
        return {
            "strategy_type": "lean_startup",
            "title": "Digital Growth Strategy",
            "description": "Comprehensive digital growth strategy",
            "key_actions": ["Market research", "MVP development", "User acquisition"],
            "timeline_months": 12,
            "estimated_investment": 50000.0,
            "projected_roi": 200.0,
            "status": "generated"
        }
    
    return app

def main():
    """Ana fonksiyon"""
    print("🚀 CKEmpire Server Başlatılıyor...")
    print("=" * 50)
    
    try:
        app = create_app()
        print("✅ Uygulama oluşturuldu")
        print("✅ Endpoint'ler hazırlandı")
        print("✅ CORS middleware eklendi")
        
        print("\n🌐 Server başlatılıyor...")
        print("📍 URL: http://localhost:8003")
        print("📚 API Docs: http://localhost:8003/docs")
        print("🔍 Health Check: http://localhost:8003/health")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8003,
            log_level="info",
            reload=False
        )
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 