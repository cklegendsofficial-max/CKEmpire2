#!/usr/bin/env python3
"""
Test script for Content Scheduler
Tests the content scheduler functionality with manual content generation
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from content_scheduler import ContentScheduler, start_content_scheduler, stop_content_scheduler

async def test_content_scheduler():
    """Test the content scheduler functionality"""
    print("🚀 Testing Content Scheduler...")
    
    try:
        # Initialize scheduler
        scheduler = ContentScheduler()
        print("✅ Scheduler initialized")
        
        # Test Ollama connection
        print("\n🔗 Testing Ollama connection...")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{scheduler.ollama_url}/api/generate",
                    json={
                        "model": "llama2",
                        "prompt": "Hello, this is a test.",
                        "stream": False
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    print("✅ Ollama connection successful")
                else:
                    print(f"⚠️ Ollama connection failed: {response.status_code}")
                    print("Note: Ollama may not be running. Using fallback generation.")
        except Exception as e:
            print(f"⚠️ Ollama connection failed: {e}")
            print("Note: Ollama may not be running. Using fallback generation.")
        
        # Test manual content generation
        print("\n📝 Testing manual content generation...")
        content = await scheduler.manual_generate_content()
        
        if content:
            print(f"✅ Generated {len(content)} content pieces")
            
            # Display generated content
            for i, item in enumerate(content, 1):
                print(f"\n📱 Content {i} - {item.channel.value.upper()}:")
                print(f"   Title: {item.adapted_title}")
                print(f"   Description: {item.adapted_description}")
                print(f"   Format: {item.content_format}")
                print(f"   Posting Time: {item.optimal_posting_time}")
                print(f"   Engagement: {item.estimated_engagement:.2f}")
                print(f"   Hashtags: {', '.join(item.hashtags[:3])}")
        else:
            print("❌ No content generated")
        
        # Test scheduler status
        print("\n📊 Testing scheduler status...")
        status = scheduler.get_scheduler_status()
        print(f"✅ Scheduler running: {status['is_running']}")
        print(f"✅ Jobs configured: {len(status['jobs'])}")
        print(f"✅ Content history: {status['content_history_count']} items")
        
        # Test analytics
        print("\n📈 Testing analytics...")
        total_content = len(scheduler.content_history)
        if total_content > 0:
            avg_engagement = sum(c.estimated_engagement for c in scheduler.content_history) / total_content
            print(f"✅ Total content: {total_content}")
            print(f"✅ Average engagement: {avg_engagement:.3f}")
            
            # Channel distribution
            channel_dist = {}
            for content in scheduler.content_history:
                channel = content.channel.value
                if channel not in channel_dist:
                    channel_dist[channel] = 0
                channel_dist[channel] += 1
            
            print("✅ Channel distribution:")
            for channel, count in channel_dist.items():
                print(f"   {channel}: {count} pieces")
        else:
            print("⚠️ No content in history for analytics")
        
        # Test scheduler start/stop
        print("\n⏰ Testing scheduler start/stop...")
        try:
            await start_content_scheduler()
            print("✅ Scheduler started successfully")
            
            # Wait a moment
            await asyncio.sleep(2)
            
            await stop_content_scheduler()
            print("✅ Scheduler stopped successfully")
        except Exception as e:
            print(f"❌ Scheduler start/stop test failed: {e}")
        
        print("\n🎉 Content Scheduler test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Content Scheduler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_content_generation_only():
    """Test only content generation without scheduler"""
    print("🚀 Testing Content Generation Only...")
    
    try:
        scheduler = ContentScheduler()
        
        # Generate content
        content = await scheduler.manual_generate_content()
        
        if content:
            print(f"✅ Generated {len(content)} content pieces")
            
            # Save to test file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_content_generation_{timestamp}.json"
            
            # Convert to serializable format
            content_data = []
            for item in content:
                content_dict = {
                    "channel": item.channel.value,
                    "adapted_title": item.adapted_title,
                    "adapted_description": item.adapted_description,
                    "platform_specific_hooks": item.platform_specific_hooks,
                    "optimal_posting_time": item.optimal_posting_time,
                    "hashtags": item.hashtags,
                    "content_format": item.content_format,
                    "estimated_engagement": item.estimated_engagement,
                    "created_at": item.created_at.isoformat(),
                    "original_idea": {
                        "title": item.original_idea.title,
                        "description": item.original_idea.description,
                        "content_type": item.original_idea.content_type.value,
                        "target_audience": item.original_idea.target_audience,
                        "viral_potential": item.original_idea.viral_potential,
                        "estimated_revenue": item.original_idea.estimated_revenue,
                        "keywords": item.original_idea.keywords,
                        "hashtags": item.original_idea.hashtags
                    }
                }
                content_data.append(content_dict)
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(content_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Content saved to {filename}")
            
            # Display summary
            print("\n📊 Content Generation Summary:")
            for i, item in enumerate(content, 1):
                print(f"   {i}. {item.channel.value.upper()}: {item.adapted_title}")
            
            return True
        else:
            print("❌ No content generated")
            return False
            
    except Exception as e:
        print(f"❌ Content generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Content Scheduler")
    parser.add_argument("--generation-only", action="store_true", 
                       help="Test only content generation without scheduler")
    
    args = parser.parse_args()
    
    if args.generation_only:
        success = asyncio.run(test_content_generation_only())
    else:
        success = asyncio.run(test_content_scheduler())
    
    sys.exit(0 if success else 1) 