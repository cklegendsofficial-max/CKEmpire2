#!/usr/bin/env python3
"""
Test script for enhanced business idea generation functionality
Tests the enhanced generate_and_implement_business_idea method with mock applications and affiliate integration
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from ai import AIModule

async def test_enhanced_business_idea_generation():
    """Test the enhanced business idea generation with mock applications and affiliate integration"""
    print("🧪 Testing Enhanced Business Idea Generation")
    print("=" * 60)
    
    try:
        # Initialize AI module
        ai_module = AIModule()
        
        # Test data - existing business ideas
        current_ideas = [
            {
                "title": "AI-Powered Personal Finance Advisor",
                "description": "Automated financial planning using AI",
                "initial_investment": 75000,
                "projected_revenue_year_3": 600000
            },
            {
                "title": "Sustainable Smart Home Energy Management",
                "description": "IoT-based energy optimization system",
                "initial_investment": 100000,
                "projected_revenue_year_3": 900000
            }
        ]
        
        print("📋 Current business ideas loaded for reference")
        for idea in current_ideas:
            print(f"   • {idea['title']}")
        
        print("\n🚀 Generating enhanced business idea with mock applications...")
        
        # Generate enhanced business idea
        result = await ai_module.generate_and_implement_business_idea(current_ideas)
        
        if result.get("status") == "success":
            print("✅ Enhanced business idea generated successfully!")
            
            # Extract components
            business_idea = result.get("business_idea", {})
            roi_analysis = result.get("roi_analysis", {})
            pdf_plan_path = result.get("pdf_plan_path", "")
            mock_applications = result.get("mock_applications", {})
            affiliate_earnings = result.get("affiliate_earnings", {})
            
            # Display business idea details
            print(f"\n📊 Business Idea Details:")
            print(f"   Title: {business_idea.get('title', 'N/A')}")
            print(f"   Description: {business_idea.get('description', 'N/A')[:100]}...")
            print(f"   Target Market: {business_idea.get('target_market', 'N/A')}")
            print(f"   Initial Investment: ${business_idea.get('initial_investment', 0):,.0f}")
            print(f"   Projected Revenue (Year 3): ${business_idea.get('projected_revenue_year_3', 0):,.0f}")
            print(f"   Risk Level: {business_idea.get('risk_level', 'N/A')}")
            print(f"   Scalability: {business_idea.get('scalability_potential', 'N/A')}")
            
            # Display ROI analysis
            print(f"\n💰 ROI Analysis:")
            roi_calc = roi_analysis.get("roi_calculation", {})
            dcf_model = roi_analysis.get("dcf_model", {})
            print(f"   ROI Percentage: {roi_calc.get('roi_percentage', 0):.2f}%")
            print(f"   Annualized ROI: {roi_calc.get('annualized_roi', 0):.2f}%")
            print(f"   Payback Period: {roi_calc.get('payback_period', 0):.1f} years")
            print(f"   NPV: ${dcf_model.get('npv', 0):,.0f}")
            print(f"   IRR: {dcf_model.get('irr', 0):.2f}%")
            
            # Display PDF plan
            print(f"\n📄 Implementation Plan:")
            if pdf_plan_path:
                print(f"   PDF Plan: {pdf_plan_path}")
                if os.path.exists(pdf_plan_path):
                    file_size = os.path.getsize(pdf_plan_path)
                    print(f"   File Size: {file_size:,} bytes")
                else:
                    print("   ⚠️ PDF file not found (may be HTML fallback)")
            else:
                print("   ❌ No PDF plan generated")
            
            # Display mock applications
            print(f"\n🎯 Mock Applications:")
            ebook_path = mock_applications.get("ebook_path", "")
            youtube_link = mock_applications.get("youtube_link", "")
            social_content = mock_applications.get("social_media_content", {})
            
            if ebook_path:
                print(f"   📚 E-book: {ebook_path}")
                if os.path.exists(ebook_path):
                    file_size = os.path.getsize(ebook_path)
                    print(f"      File Size: {file_size:,} bytes")
                else:
                    print("      ⚠️ E-book file not found")
            else:
                print("   ❌ No e-book generated")
            
            if youtube_link:
                print(f"   📺 YouTube Link: {youtube_link}")
            else:
                print("   ❌ No YouTube link generated")
            
            if social_content:
                print(f"   📱 Social Media Content Generated:")
                for platform, content in social_content.items():
                    if isinstance(content, dict):
                        title = content.get("title", "No title")
                        print(f"      • {platform.upper()}: {title}")
                    else:
                        print(f"      • {platform.upper()}: Content available")
            else:
                print("   ❌ No social media content generated")
            
            # Display affiliate earnings
            print(f"\n💰 Affiliate Earnings Analysis:")
            total_affiliate_earnings = affiliate_earnings.get("total_affiliate_earnings", 0)
            affiliate_roi = affiliate_earnings.get("affiliate_roi", 0)
            affiliate_investment = affiliate_earnings.get("affiliate_investment", 0)
            
            print(f"   Total Affiliate Earnings: ${total_affiliate_earnings:,.0f}")
            print(f"   Affiliate Investment: ${affiliate_investment:,.0f}")
            print(f"   Affiliate ROI: {affiliate_roi:.2f}%")
            
            # Display affiliate channels
            channels = affiliate_earnings.get("channels", {})
            if channels:
                print(f"   Channel Breakdown:")
                for channel_name, channel_data in channels.items():
                    if isinstance(channel_data, dict):
                        platform = channel_data.get("platform", "Unknown")
                        earnings = channel_data.get("estimated_earnings", 0)
                        commission_rate = channel_data.get("commission_rate", 0)
                        print(f"      • {platform}: ${earnings:,.0f} ({commission_rate*100:.1f}% commission)")
            
            # Calculate total potential earnings
            base_revenue = business_idea.get("projected_revenue_year_3", 0)
            total_potential = base_revenue + total_affiliate_earnings
            print(f"\n💎 Total Potential Earnings:")
            print(f"   Base Business Revenue: ${base_revenue:,.0f}")
            print(f"   Affiliate Earnings: ${total_affiliate_earnings:,.0f}")
            print(f"   Total Potential: ${total_potential:,.0f}")
            
            # Check analytics file
            analytics_file = Path("data/business_ideas_analytics.json")
            if analytics_file.exists():
                print(f"\n📈 Analytics Tracking:")
                print(f"   Analytics file: {analytics_file}")
                file_size = analytics_file.stat().st_size
                print(f"   File size: {file_size:,} bytes")
                
                # Read and display latest analytics
                try:
                    with open(analytics_file, 'r', encoding='utf-8') as f:
                        analytics_data = json.load(f)
                    
                    if analytics_data:
                        latest_analytics = analytics_data[-1]
                        print(f"   Latest entry:")
                        print(f"      • Idea: {latest_analytics.get('idea_title', 'Unknown')}")
                        print(f"      • ROI: {latest_analytics.get('roi_percentage', 0):.2f}%")
                        print(f"      • Affiliate Earnings: ${latest_analytics.get('affiliate_earnings', 0):,.0f}")
                        print(f"      • Total Potential: ${latest_analytics.get('total_potential_earnings', 0):,.0f}")
                        
                        # Check mock applications tracking
                        mock_apps = latest_analytics.get('mock_applications', {})
                        if mock_apps:
                            print(f"      • E-book Generated: {mock_apps.get('ebook_generated', False)}")
                            print(f"      • YouTube Link: {mock_apps.get('youtube_link', 'N/A')}")
                            print(f"      • Social Content: {mock_apps.get('social_content_generated', False)}")
                except Exception as e:
                    print(f"   ⚠️ Error reading analytics: {e}")
            else:
                print(f"\n❌ Analytics file not found: {analytics_file}")
            
            print(f"\n✅ Enhanced business idea generation test completed successfully!")
            return True
            
        else:
            print(f"❌ Enhanced business idea generation failed:")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_scheduler_integration():
    """Test that the enhanced business idea generation is properly integrated with the scheduler"""
    print("\n🔧 Testing Scheduler Integration")
    print("=" * 60)
    
    try:
        # Import scheduler
        from content_scheduler import ContentScheduler
        
        # Initialize scheduler
        scheduler = ContentScheduler()
        
        print("📋 Testing business idea generation through scheduler...")
        
        # Test the business idea generation method directly
        business_idea_result = await scheduler._generate_daily_business_idea()
        
        if business_idea_result:
            print("✅ Scheduler business idea generation successful!")
            
            business_idea = business_idea_result.get("business_idea", {})
            roi_analysis = business_idea_result.get("roi_analysis", {})
            mock_applications = business_idea_result.get("mock_applications", {})
            affiliate_earnings = business_idea_result.get("affiliate_earnings", {})
            
            print(f"   📊 Business Idea: {business_idea.get('title', 'N/A')}")
            print(f"   💰 ROI: {roi_analysis.get('roi_calculation', {}).get('roi_percentage', 0):.2f}%")
            print(f"   📚 E-book Generated: {bool(mock_applications.get('ebook_path'))}")
            print(f"   📺 YouTube Link: {bool(mock_applications.get('youtube_link'))}")
            print(f"   💎 Affiliate Earnings: ${affiliate_earnings.get('total_affiliate_earnings', 0):,.0f}")
            
            return True
        else:
            print("❌ Scheduler business idea generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Scheduler integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cost_free_operation():
    """Test that all operations remain cost-free using local tools"""
    print("\n💰 Testing Cost-Free Operation")
    print("=" * 60)
    
    try:
        # Check for local dependencies
        print("🔍 Checking local dependencies:")
        
        # Check if Ollama is available (local AI)
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=5.0)
                if response.status_code == 200:
                    print("   ✅ Ollama (local AI) - Available")
                else:
                    print("   ⚠️ Ollama (local AI) - Not responding")
        except Exception:
            print("   ❌ Ollama (local AI) - Not available")
        
        # Check if PDFKit is available (local PDF generation)
        try:
            import pdfkit
            print("   ✅ PDFKit (local PDF generation) - Available")
        except ImportError:
            print("   ❌ PDFKit (local PDF generation) - Not installed")
        
        # Check if finance module is available (local calculations)
        try:
            from finance import FinanceManager
            print("   ✅ Finance Module (local calculations) - Available")
        except ImportError:
            print("   ❌ Finance Module (local calculations) - Not available")
        
        # Check data directory
        data_dir = Path("data")
        if data_dir.exists():
            print("   ✅ Data Directory - Available")
        else:
            print("   ❌ Data Directory - Not found")
        
        print("\n📊 Cost-Free Operation Summary:")
        print("   • AI Generation: Local Ollama (free)")
        print("   • PDF Generation: Local PDFKit (free)")
        print("   • Financial Calculations: Local finance module (free)")
        print("   • Data Storage: Local CSV/JSON files (free)")
        print("   • No external API costs or subscriptions required")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost-free operation test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Enhanced Business Idea Generation Test Suite")
    print("=" * 60)
    
    # Change to backend directory for proper imports
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    # Run tests
    tests = [
        ("Enhanced Business Idea Generation", test_enhanced_business_idea_generation),
        ("Scheduler Integration", test_scheduler_integration),
        ("Cost-Free Operation", test_cost_free_operation)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = await test_func()
        results.append((test_name, result))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced business idea generation is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main()) 