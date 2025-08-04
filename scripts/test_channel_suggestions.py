#!/usr/bin/env python3
"""
Test script for channel suggestions functionality
Tests the new suggest_alternative_channels method in ai.py
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ai import AIModule

async def test_channel_suggestions():
    """Test the channel suggestions functionality"""
    print("📺 Testing Channel Suggestions Generation...")
    
    try:
        # Initialize AI module
        ai_module = AIModule()
        
        # Create sample content for testing
        original_content = {
            "title": "AI Automation Trends 2025",
            "description": "Comprehensive guide to the latest AI automation trends and how they're transforming industries worldwide.",
            "content_type": "video",
            "target_audience": "Tech professionals and business leaders",
            "viral_potential": 0.85,
            "estimated_revenue": 500.0,
            "keywords": ["AI", "automation", "trends", "2025"],
            "hashtags": ["#AI", "#automation", "#trends"]
        }
        
        print("📝 Testing with sample content...")
        result = await ai_module.suggest_alternative_channels(original_content)
        
        if result.get("status") == "success":
            channel_suggestions = result.get("channel_suggestions", {})
            total_revenue = result.get("total_potential_revenue", 0)
            
            print(f"✅ Channel suggestions generated successfully!")
            print(f"💰 Total potential revenue: ${total_revenue:.2f}/month")
            print(f"📱 Channels analyzed: {len(channel_suggestions)}")
            
            # Display results for each channel
            for channel_key, suggestion in channel_suggestions.items():
                channel_name = suggestion.get("channel_name", channel_key.upper())
                adaptation = suggestion.get("adaptation", {})
                revenue_forecast = suggestion.get("revenue_forecast", {})
                
                print(f"\n📺 {channel_name}:")
                print(f"   📝 Adapted Title: {adaptation.get('adapted_title', 'N/A')}")
                print(f"   💰 Monthly Revenue: ${revenue_forecast.get('monthly_revenue', 0):.2f}")
                print(f"   👀 Estimated Views: {revenue_forecast.get('estimated_views_per_month', 0):,}")
                print(f"   📊 Engagement Rate: {revenue_forecast.get('engagement_rate', 0):.1%}")
                print(f"   🏷️  Hashtags: {', '.join(adaptation.get('optimal_hashtags', [])[:3])}")
            
            # Check analytics file
            analytics_file = Path("data/channel_suggestions_analytics.json")
            if analytics_file.exists():
                with open(analytics_file, 'r', encoding='utf-8') as f:
                    analytics = json.load(f)
                print(f"\n✅ Analytics tracked: {len(analytics)} channel suggestions")
            else:
                print("\n⚠️ Analytics file not found")
                
        else:
            print(f"❌ Failed to generate channel suggestions: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error testing channel suggestions: {e}")

async def test_with_different_content_types():
    """Test with different content types"""
    print("\n🔄 Testing with different content types...")
    
    try:
        ai_module = AIModule()
        
        # Test different content types
        content_types = [
            {
                "title": "Sustainable Business Models",
                "description": "How to build profitable businesses that help the environment",
                "content_type": "article"
            },
            {
                "title": "Crypto Investment Strategies",
                "description": "Advanced cryptocurrency investment techniques for 2025",
                "content_type": "video"
            },
            {
                "title": "Remote Work Productivity Hacks",
                "description": "10 proven strategies to boost productivity while working from home",
                "content_type": "social_media"
            }
        ]
        
        for i, content in enumerate(content_types, 1):
            print(f"\n📝 Test {i}: {content['title']}")
            result = await ai_module.suggest_alternative_channels(content)
            
            if result.get("status") == "success":
                total_revenue = result.get("total_potential_revenue", 0)
                channel_count = len(result.get("channel_suggestions", {}))
                print(f"   ✅ Generated for {channel_count} channels - Revenue: ${total_revenue:.2f}/month")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"❌ Error testing different content types: {e}")

async def test_revenue_forecasting():
    """Test revenue forecasting functionality"""
    print("\n💰 Testing Revenue Forecasting...")
    
    try:
        from finance import FinanceManager
        
        finance_manager = FinanceManager()
        
        # Test different RPM scenarios
        test_channels = [
            {"name": "YouTube", "rpm_range": (2.0, 8.0), "engagement_rate": 0.08},
            {"name": "TikTok", "rpm_range": (0.5, 2.0), "engagement_rate": 0.12},
            {"name": "LinkedIn", "rpm_range": (3.0, 10.0), "engagement_rate": 0.06}
        ]
        
        for channel in test_channels:
            min_rpm, max_rpm = channel["rpm_range"]
            avg_rpm = (min_rpm + max_rpm) / 2
            monthly_views = 5000 * 30  # 5000 views per day
            monthly_revenue = (monthly_views / 1000) * avg_rpm
            
            print(f"📺 {channel['name']}:")
            print(f"   📊 Avg RPM: ${avg_rpm:.2f}")
            print(f"   👀 Monthly Views: {monthly_views:,}")
            print(f"   💰 Monthly Revenue: ${monthly_revenue:.2f}")
            print(f"   📈 Engagement Rate: {channel['engagement_rate']:.1%}")
            
    except Exception as e:
        print(f"❌ Error testing revenue forecasting: {e}")

async def main():
    """Main test function"""
    print("🧪 Channel Suggestions Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    await test_channel_suggestions()
    
    # Test with different content types
    await test_with_different_content_types()
    
    # Test revenue forecasting
    await test_revenue_forecasting()
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    asyncio.run(main()) 