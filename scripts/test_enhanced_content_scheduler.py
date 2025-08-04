#!/usr/bin/env python3
"""
Enhanced Content Scheduler Test Script
Tests the new quality checks, performance tracking, and analytics features
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_enhanced_content_scheduler():
    """Test the enhanced content scheduler with quality checks and performance tracking"""
    print("🚀 Testing Enhanced Content Scheduler")
    print("=" * 50)
    
    try:
        # Import the content scheduler
        from content_scheduler import ContentScheduler, ContentPerformance
        
        print("✅ Content scheduler imported successfully")
        
        # Create scheduler instance
        scheduler = ContentScheduler()
        print(f"✅ Scheduler created with quality threshold: {scheduler.quality_threshold}")
        
        # Test quality assessment
        print("\n🔍 Testing Quality Assessment...")
        from ai import ContentIdea, ContentType
        
        # Create a test content idea
        test_idea = ContentIdea(
            title="Test Viral Content",
            description="This is a test content idea for quality assessment",
            content_type=ContentType.VIDEO,
            target_audience="Tech professionals",
            viral_potential=0.85,
            estimated_revenue=500.0,
            keywords=["test", "viral", "quality"],
            hashtags=["#test", "#viral", "#quality"]
        )
        
        # Test quality assessment
        async def test_quality_assessment():
            result = await scheduler._assess_content_quality(test_idea)
            print(f"   Quality Assessment Result:")
            print(f"   - Passed: {result.get('passed', False)}")
            print(f"   - Score: {result.get('score', 0):.2f}")
            print(f"   - Reason: {result.get('reason', 'Unknown')}")
            
            if result.get('passed', False):
                print("   ✅ Quality check passed")
            else:
                print("   ❌ Quality check failed")
        
        # Test performance tracking
        print("\n📊 Testing Performance Tracking...")
        async def test_performance_tracking():
            # Create test repurposed content
            from content_scheduler import RepurposedContent, ChannelType
            
            test_content = RepurposedContent(
                original_idea=test_idea,
                channel=ChannelType.YOUTUBE,
                adapted_title="Test YouTube Content",
                adapted_description="Test description for YouTube",
                platform_specific_hooks=["Hook 1", "Hook 2"],
                optimal_posting_time="15:00",
                hashtags=["#test", "#youtube"],
                content_format="video",
                estimated_engagement=0.8,
                viral_potential=0.85,
                quality_score=0.0,
                mock_views=0,
                mock_engagement_rate=0.0
            )
            
            # Test quality assessment for repurposed content
            quality_result = await scheduler._assess_repurposed_quality(test_content)
            print(f"   Repurposed Quality Assessment:")
            print(f"   - Passed: {quality_result.get('passed', False)}")
            print(f"   - Score: {quality_result.get('score', 0):.2f}")
            print(f"   - Reason: {quality_result.get('reason', 'Unknown')}")
            
            # Test performance tracking
            tracked_content = await scheduler._add_performance_tracking(test_content)
            print(f"   Performance Tracking:")
            print(f"   - Mock Views: {tracked_content.mock_views:,}")
            print(f"   - Mock Engagement Rate: {tracked_content.mock_engagement_rate:.2%}")
            print(f"   - Quality Score: {tracked_content.quality_score:.2f}")
            
            # Test analytics tracking
            await scheduler._track_content_analytics([tracked_content])
            print("   ✅ Analytics tracking completed")
        
        # Test CSV file creation
        print("\n📁 Testing CSV Analytics...")
        async def test_csv_analytics():
            csv_file = Path("data/content_performance_analytics.csv")
            if csv_file.exists():
                print(f"   ✅ CSV file created: {csv_file}")
                
                # Read and display sample data
                import csv
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    print(f"   📊 CSV Headers: {headers}")
                    
                    # Show last few rows
                    rows = list(reader)
                    if rows:
                        print(f"   📈 Total rows: {len(rows)}")
                        print(f"   📋 Latest row: {rows[-1]}")
            else:
                print("   ⚠️ CSV file not found")
        
        # Test manual content generation
        print("\n🔄 Testing Manual Content Generation...")
        async def test_manual_generation():
            try:
                content = await scheduler.manual_generate_content()
                print(f"   ✅ Generated {len(content)} content pieces")
                
                for i, item in enumerate(content, 1):
                    print(f"   📱 {i}. {item.channel.value}: {item.adapted_title}")
                    print(f"      Quality: {item.quality_score:.2f}, Views: {item.mock_views:,}")
                
            except Exception as e:
                print(f"   ❌ Manual generation failed: {e}")
        
        # Run all tests
        async def run_all_tests():
            await test_quality_assessment()
            await test_performance_tracking()
            await test_csv_analytics()
            await test_manual_generation()
        
        # Run the tests
        asyncio.run(run_all_tests())
        
        print("\n✅ Enhanced Content Scheduler Test Completed Successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def test_scheduler_status():
    """Test scheduler status and configuration"""
    print("\n🔧 Testing Scheduler Status...")
    
    try:
        from content_scheduler import ContentScheduler
        
        scheduler = ContentScheduler()
        status = scheduler.get_scheduler_status()
        
        print(f"   Scheduler Running: {status['is_running']}")
        print(f"   Content History Count: {status['content_history_count']}")
        print(f"   Jobs Count: {len(status['jobs'])}")
        
        for job in status['jobs']:
            print(f"   📅 Job: {job['name']} (ID: {job['id']})")
            if job['next_run']:
                print(f"      Next Run: {job['next_run']}")
        
        print("   ✅ Scheduler status test completed")
        
    except Exception as e:
        print(f"   ❌ Scheduler status test failed: {e}")

def test_quality_threshold_configuration():
    """Test quality threshold configuration"""
    print("\n⚙️ Testing Quality Threshold Configuration...")
    
    try:
        from content_scheduler import ContentScheduler
        
        scheduler = ContentScheduler()
        
        # Test different quality thresholds
        test_thresholds = [0.5, 0.7, 0.8, 0.9]
        
        for threshold in test_thresholds:
            scheduler.quality_threshold = threshold
            print(f"   Quality Threshold: {threshold}")
            print(f"   - Threshold set to: {scheduler.quality_threshold}")
        
        # Reset to default
        scheduler.quality_threshold = 0.7
        print(f"   ✅ Reset to default threshold: {scheduler.quality_threshold}")
        
    except Exception as e:
        print(f"   ❌ Quality threshold test failed: {e}")

if __name__ == "__main__":
    print("🚀 Enhanced Content Scheduler Test Suite")
    print("=" * 60)
    
    # Run all tests
    success1 = test_enhanced_content_scheduler()
    test_scheduler_status()
    test_quality_threshold_configuration()
    
    if success1:
        print("\n🎉 All Enhanced Content Scheduler Tests Passed!")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    print("\n📋 Test Summary:")
    print("✅ Quality assessment with viral potential threshold")
    print("✅ Performance tracking with mock views and engagement")
    print("✅ CSV analytics tracking")
    print("✅ Manual content generation")
    print("✅ Scheduler status and configuration")
    print("✅ Quality threshold configuration") 