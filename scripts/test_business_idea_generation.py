#!/usr/bin/env python3
"""
Test script for business idea generation functionality
Tests the new generate_and_implement_business_idea method in ai.py
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai import AIModule

async def test_business_idea_generation():
    """Test the business idea generation functionality"""
    print("🚀 Testing Business Idea Generation...")
    
    try:
        # Initialize AI module
        ai_module = AIModule()
        
        # Test with empty current ideas
        print("📝 Testing with empty current ideas...")
        result = await ai_module.generate_and_implement_business_idea([])
        
        if result.get("status") == "success":
            business_idea = result.get("business_idea", {})
            roi_analysis = result.get("roi_analysis", {})
            pdf_path = result.get("pdf_plan_path", "")
            
            print(f"✅ Business Idea Generated: {business_idea.get('title', 'Unknown')}")
            print(f"📊 ROI: {roi_analysis.get('roi_calculation', {}).get('roi_percentage', 0):.2f}%")
            print(f"📄 PDF Path: {pdf_path}")
            
            # Check if PDF/HTML file was created
            if pdf_path and Path(pdf_path).exists():
                print(f"✅ PDF/HTML file created successfully")
            else:
                print(f"⚠️ PDF/HTML file not found at: {pdf_path}")
            
            # Check analytics file
            analytics_file = Path("data/business_ideas_analytics.json")
            if analytics_file.exists():
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    analytics = json.load(f)
                print(f"✅ Analytics tracked: {len(analytics)} business ideas")
            else:
                print("⚠️ Analytics file not found")
                
        else:
            print(f"❌ Failed to generate business idea: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing business idea generation: {e}")

async def test_with_existing_ideas():
    """Test with existing business ideas to avoid duplication"""
    print("\n🔄 Testing with existing business ideas...")
    
    try:
        # Create mock existing ideas
        existing_ideas = [
            {
                "title": "AI-Powered Personal Finance Advisor",
                "initial_investment": 75000,
                "projected_revenue_year_3": 600000,
                "roi_percentage": 15.5
            },
            {
                "title": "Sustainable Smart Home Energy Management",
                "initial_investment": 100000,
                "projected_revenue_year_3": 900000,
                "roi_percentage": 25.2
            }
        ]
        
        ai_module = AIModule()
        result = await ai_module.generate_and_implement_business_idea(existing_ideas)
        
        if result.get("status") == "success":
            business_idea = result.get("business_idea", {})
            print(f"✅ New business idea generated: {business_idea.get('title', 'Unknown')}")
            
            # Check if it's different from existing ideas
            new_title = business_idea.get('title', '')
            existing_titles = [idea.get('title', '') for idea in existing_ideas]
            
            if new_title not in existing_titles:
                print("✅ New idea is different from existing ones")
            else:
                print("⚠️ New idea might be similar to existing ones")
        else:
            print(f"❌ Failed to generate business idea: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing with existing ideas: {e}")

async def test_roi_calculation():
    """Test ROI calculation functionality"""
    print("\n📊 Testing ROI calculation...")
    
    try:
        from finance import FinanceManager
        
        finance_manager = FinanceManager()
        
        # Test DCF model
        dcf_model = finance_manager.create_dcf_model(
            initial_investment=50000,
            target_revenue=200000,
            growth_rate=0.15,
            discount_rate=0.10,
            time_period=3
        )
        
        print(f"✅ DCF Model created")
        print(f"📈 NPV: ${dcf_model.calculate_npv():,.0f}")
        print(f"📈 IRR: {dcf_model.calculate_irr():.2f}%")
        
        # Test ROI calculation
        roi_calc = finance_manager.calculate_roi_for_target(
            target_amount=200000,
            initial_investment=50000,
            time_period=3.0
        )
        
        print(f"📊 ROI: {roi_calc.calculate_roi():.2f}%")
        print(f"📊 Annualized ROI: {roi_calc.calculate_annualized_roi():.2f}%")
        print(f"📊 Payback Period: {roi_calc.calculate_payback_period():.1f} years")
        
    except Exception as e:
        print(f"❌ Error testing ROI calculation: {e}")

async def main():
    """Main test function"""
    print("🧪 Business Idea Generation Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    await test_business_idea_generation()
    
    # Test with existing ideas
    await test_with_existing_ideas()
    
    # Test ROI calculation
    await test_roi_calculation()
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main()) 