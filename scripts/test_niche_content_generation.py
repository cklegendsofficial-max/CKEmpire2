#!/usr/bin/env python3
"""
Test script for niche content generation functionality
Tests the new generate_niche_content_ideas method in ai.py and its integration with the scheduler
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from ai import AIModule
from content_scheduler import ContentScheduler

async def test_niche_content_generation():
    """Test the niche content generation functionality"""
    print("🎯 Testing Niche Content Generation")
    print("=" * 50)
    
    # Initialize AI module
    ai_module = AIModule()
    
    # Test 1: Basic niche content generation
    print("\n1. Testing basic niche content generation...")
    try:
        niche = "AI and automation"
        content_ideas = await ai_module.generate_niche_content_ideas(niche, channels=5)
        
        if content_ideas:
            print(f"✅ Successfully generated {len(content_ideas)} content ideas for '{niche}'")
            
            # Display the generated ideas
            for i, idea in enumerate(content_ideas, 1):
                print(f"\n   Idea {i}:")
                print(f"   - Title: {idea.title}")
                print(f"   - Type: {idea.content_type.value}")
                print(f"   - Viral Potential: {idea.viral_potential:.2f}")
                print(f"   - Estimated Revenue: ${idea.estimated_revenue:.2f}")
                print(f"   - Keywords: {', '.join(idea.keywords)}")
                print(f"   - Hashtags: {', '.join(idea.hashtags)}")
        else:
            print("❌ No content ideas generated")
            
    except Exception as e:
        print(f"❌ Error in basic niche content generation: {e}")
    
    # Test 2: Different niche with different channel count
    print("\n2. Testing different niche with 3 channels...")
    try:
        niche = "Sustainable living"
        content_ideas = await ai_module.generate_niche_content_ideas(niche, channels=3)
        
        if content_ideas:
            print(f"✅ Successfully generated {len(content_ideas)} content ideas for '{niche}'")
            
            # Check variation types
            variation_types = {}
            for idea in content_ideas:
                variation_type = "educational"  # default
                if "viral" in idea.title.lower() or "shock" in idea.title.lower():
                    variation_type = "viral"
                elif "lifestyle" in idea.title.lower() or "journey" in idea.title.lower():
                    variation_type = "lifestyle"
                variation_types[variation_type] = variation_types.get(variation_type, 0) + 1
            
            print(f"   Variation types: {variation_types}")
        else:
            print("❌ No content ideas generated")
            
    except Exception as e:
        print(f"❌ Error in different niche test: {e}")
    
    # Test 3: Check CSV analytics file creation
    print("\n3. Testing CSV analytics tracking...")
    try:
        csv_file = Path("data/niche_content_analytics.csv")
        if csv_file.exists():
            print(f"✅ Niche content analytics CSV file created: {csv_file}")
            
            # Read and display the CSV content
            import csv
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            if len(rows) > 1:  # Has headers and at least one data row
                print(f"   📊 CSV has {len(rows)-1} data entries")
                print(f"   📋 Headers: {', '.join(rows[0])}")
                if len(rows) > 1:
                    print(f"   📈 Latest entry: {rows[-1]}")
            else:
                print("   📊 CSV file exists but no data entries found")
        else:
            print("❌ Niche content analytics CSV file not found")
            
    except Exception as e:
        print(f"❌ Error checking CSV analytics: {e}")

async def test_scheduler_integration():
    """Test the integration with content scheduler"""
    print("\n🎯 Testing Scheduler Integration")
    print("=" * 50)
    
    # Initialize scheduler
    scheduler = ContentScheduler()
    
    # Test 1: Manual niche content generation through scheduler
    print("\n1. Testing manual niche content generation...")
    try:
        result = await scheduler._generate_daily_niche_content()
        
        if result and result.get("status") == "success":
            niche = result.get("niche", "Unknown")
            total_ideas = result.get("total_ideas", 0)
            avg_viral_potential = result.get("average_viral_potential", 0.0)
            total_revenue = result.get("total_estimated_revenue", 0.0)
            variation_types = result.get("variation_types", {})
            
            print(f"✅ Scheduler generated niche content for '{niche}'")
            print(f"   📊 Total ideas: {total_ideas}")
            print(f"   📈 Average viral potential: {avg_viral_potential:.2f}")
            print(f"   💰 Total estimated revenue: ${total_revenue:.2f}")
            print(f"   📝 Variation types: {variation_types}")
            
            # Display some content ideas
            content_ideas = result.get("content_ideas", [])
            if content_ideas:
                print(f"\n   📋 Sample content ideas:")
                for i, idea in enumerate(content_ideas[:3], 1):
                    print(f"      {i}. {idea.get('title', 'Unknown')}")
        else:
            print("❌ Scheduler niche content generation failed")
            
    except Exception as e:
        print(f"❌ Error in scheduler integration test: {e}")

async def test_ollama_integration():
    """Test Ollama integration for niche content"""
    print("\n🎯 Testing Ollama Integration")
    print("=" * 50)
    
    # Initialize AI module
    ai_module = AIModule()
    
    # Test 1: Test Ollama method directly
    print("\n1. Testing Ollama niche content generation...")
    try:
        prompt = """
Generate a viral content idea for the niche: "AI and automation"

Requirements:
- Content type: viral
- Niche: AI and automation
- Must be engaging and shareable
- Include 2025 trends: AI-powered personalization, Short-form video dominance, Authentic storytelling, Community-driven content, Educational entertainment
- Target audience: AI and automation enthusiasts and general audience
- Viral potential: High
- Revenue potential: Medium to High

Format the response as JSON:
{
    "title": "Engaging title",
    "description": "Detailed description",
    "content_type": "video|article|social_media|podcast",
    "target_audience": "Specific audience",
    "viral_potential": 0.0-1.0,
    "estimated_revenue": 0.0,
    "keywords": ["keyword1", "keyword2"],
    "hashtags": ["#hashtag1", "#hashtag2"],
    "variation_type": "viral",
    "niche_focus": "AI and automation",
    "trends_included": ["trend1", "trend2"]
}
"""
        
        response = await ai_module._generate_with_ollama_niche(prompt, "AI and automation", "viral")
        
        if response:
            print("✅ Ollama response received")
            print(f"   📝 Response length: {len(response)} characters")
            print(f"   📋 Response preview: {response[:200]}...")
            
            # Try to parse the response
            content_idea = ai_module._parse_niche_content_idea(response, "AI and automation", "viral")
            if content_idea:
                print("✅ Successfully parsed Ollama response into ContentIdea")
                print(f"   📝 Title: {content_idea.title}")
                print(f"   📊 Viral potential: {content_idea.viral_potential:.2f}")
            else:
                print("⚠️ Could not parse Ollama response, using fallback")
        else:
            print("❌ No Ollama response received, using fallback")
            
    except Exception as e:
        print(f"❌ Error in Ollama integration test: {e}")

async def test_mock_content_generation():
    """Test mock content generation when Ollama is unavailable"""
    print("\n🎯 Testing Mock Content Generation")
    print("=" * 50)
    
    # Initialize AI module
    ai_module = AIModule()
    
    # Test different niches and variation types
    test_cases = [
        ("Fitness and nutrition", "educational", 0),
        ("Cryptocurrency and blockchain", "viral", 1),
        ("Digital nomad lifestyle", "lifestyle", 2)
    ]
    
    for niche, variation_type, index in test_cases:
        print(f"\nTesting mock content for '{niche}' ({variation_type} variation)...")
        try:
            mock_content = ai_module._create_mock_niche_content(niche, variation_type, index)
            
            print(f"✅ Generated mock content:")
            print(f"   📝 Title: {mock_content.title}")
            print(f"   📄 Description: {mock_content.description}")
            print(f"   📊 Viral potential: {mock_content.viral_potential:.2f}")
            print(f"   💰 Estimated revenue: ${mock_content.estimated_revenue:.2f}")
            print(f"   🏷️ Keywords: {', '.join(mock_content.keywords)}")
            print(f"   #️⃣ Hashtags: {', '.join(mock_content.hashtags)}")
            
        except Exception as e:
            print(f"❌ Error generating mock content: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting Niche Content Generation Tests")
    print("=" * 60)
    
    # Run all test functions
    await test_niche_content_generation()
    await test_scheduler_integration()
    await test_ollama_integration()
    await test_mock_content_generation()
    
    print("\n" + "=" * 60)
    print("✅ All niche content generation tests completed!")
    print("\n📊 Summary:")
    print("   - Niche content generation with educational/viral/lifestyle variations")
    print("   - Integration with content scheduler for daily production")
    print("   - Ollama integration with 2025 trends in prompts")
    print("   - Mock content fallback when Ollama is unavailable")
    print("   - CSV analytics tracking for niche content")
    print("   - Cost-free operation using local AI")

if __name__ == "__main__":
    asyncio.run(main()) 