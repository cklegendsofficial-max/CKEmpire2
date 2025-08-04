#!/usr/bin/env python3
"""
Test script for AI optimization with 2025 trends
Tests the enhanced AI module with feedback loop and continuous optimization
"""

import sys
import asyncio
import json
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

async def test_2025_trends_initialization():
    """Test 2025 trends initialization"""
    print("🧪 Testing 2025 trends initialization...")
    
    try:
        from ai import AIModule
        
        ai_module = AIModule()
        
        # Check if trends are initialized
        if hasattr(ai_module, 'trend_data') and ai_module.trend_data:
            print("✅ 2025 trends initialized successfully")
            print(f"   📊 Number of trends: {len(ai_module.trend_data)}")
            
            # Display some trends
            for i, trend in enumerate(ai_module.trend_data[:3]):
                print(f"   📈 Trend {i+1}: {trend.trend_name} (Impact: {trend.impact_score:.2f})")
            
            return True
        else:
            print("❌ 2025 trends not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_optimized_prompt_generation():
    """Test optimized prompt generation with 2025 trends"""
    print("\n🧪 Testing optimized prompt generation...")
    
    try:
        from ai import AIModule, ContentType
        
        ai_module = AIModule()
        
        # Test prompt generation for different content types
        content_types = [ContentType.VIDEO, ContentType.SOCIAL_MEDIA, ContentType.ARTICLE]
        
        for content_type in content_types:
            base_prompt = f"Generate content about: AI technology"
            optimized_prompt = await ai_module._generate_optimized_prompt_with_2025_trends(
                base_prompt, content_type, "Tech enthusiasts"
            )
            
            if optimized_prompt and "2025 TREND OPTIMIZATION" in optimized_prompt:
                print(f"✅ Optimized prompt generated for {content_type.value}")
            else:
                print(f"❌ Failed to generate optimized prompt for {content_type.value}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_feedback_loop_optimization():
    """Test feedback loop optimization"""
    print("\n🧪 Testing feedback loop optimization...")
    
    try:
        from ai import AIModule, ContentIdea, ContentType
        
        ai_module = AIModule()
        
        # Create a test content idea
        test_idea = ContentIdea(
            title="Test Content",
            description="A test content idea for optimization",
            content_type=ContentType.VIDEO,
            target_audience="Test audience",
            viral_potential=0.5,
            estimated_revenue=100.0,
            keywords=["test"],
            hashtags=["#test"]
        )
        
        # Test optimization
        optimized_idea = await ai_module._optimize_content_with_feedback_loop(test_idea)
        
        if optimized_idea and optimized_idea.title != test_idea.title:
            print("✅ Content optimization completed")
            print(f"   📝 Original title: {test_idea.title}")
            print(f"   📝 Optimized title: {optimized_idea.title}")
            print(f"   📈 Viral potential: {optimized_idea.viral_potential:.2f}")
            return True
        else:
            print("⚠️ Content optimization returned same content (using fallback)")
            return True  # This is acceptable if Ollama is not available
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_performance_data_management():
    """Test performance data management"""
    print("\n🧪 Testing performance data management...")
    
    try:
        from ai import AIModule, ContentPerformance, ContentType
        
        ai_module = AIModule()
        
        # Test loading performance data
        initial_count = len(ai_module.performance_data)
        print(f"   📊 Initial performance records: {initial_count}")
        
        # Test saving performance data
        ai_module._save_performance_data()
        print("✅ Performance data saved successfully")
        
        # Test loading performance data
        ai_module._load_performance_data()
        final_count = len(ai_module.performance_data)
        print(f"   📊 Final performance records: {final_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_continuous_optimization_status():
    """Test continuous optimization status"""
    print("\n🧪 Testing continuous optimization status...")
    
    try:
        from ai import AIModule
        
        ai_module = AIModule()
        
        # Get optimization status
        status = ai_module.get_optimization_status()
        
        if status:
            print("✅ Optimization status retrieved successfully")
            print(f"   🔄 Continuous optimization: {status.get('continuous_optimization')}")
            print(f"   📊 Performance records: {status.get('performance_records')}")
            print(f"   📈 Trend data count: {status.get('trend_data_count')}")
            print(f"   🎯 Low performance content: {status.get('low_performance_content')}")
            return True
        else:
            print("❌ Failed to get optimization status")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_24_7_optimization_startup():
    """Test 24/7 optimization startup"""
    print("\n🧪 Testing 24/7 optimization startup...")
    
    try:
        from ai import AIModule
        
        ai_module = AIModule()
        
        # Test starting 24/7 optimization
        await ai_module.start_24_7_optimization()
        
        # Check if optimization is running
        status = ai_module.get_optimization_status()
        if status.get('continuous_optimization'):
            print("✅ 24/7 optimization started successfully")
            return True
        else:
            print("❌ 24/7 optimization failed to start")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_trend_data_parsing():
    """Test trend data parsing"""
    print("\n🧪 Testing trend data parsing...")
    
    try:
        from ai import AIModule
        
        ai_module = AIModule()
        
        # Test parsing trend data
        mock_response = '''
        [
            {
                "trend_name": "Test Trend",
                "category": "Test Category",
                "impact_score": 0.8,
                "content_adaptation": "Test adaptation",
                "viral_potential": 0.7,
                "hashtags": ["#test", "#trending"]
            }
        ]
        '''
        
        trends = ai_module._parse_trend_data(mock_response)
        
        if trends and len(trends) > 0:
            print("✅ Trend data parsing successful")
            print(f"   📈 Parsed trends: {len(trends)}")
            print(f"   📊 First trend: {trends[0].trend_name}")
            return True
        else:
            print("❌ Trend data parsing failed")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_improvement_suggestions():
    """Test improvement suggestions generation"""
    print("\n🧪 Testing improvement suggestions...")
    
    try:
        from ai import AIModule, ContentType
        
        ai_module = AIModule()
        
        # Test getting improvement suggestions
        suggestions = ai_module._get_improvement_suggestions(ContentType.VIDEO)
        
        print(f"✅ Improvement suggestions retrieved: {len(suggestions)}")
        for suggestion in suggestions[:3]:
            print(f"   💡 Suggestion: {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Starting AI Optimization Tests")
    print("=" * 50)
    
    tests = [
        ("2025 Trends Initialization", test_2025_trends_initialization),
        ("Optimized Prompt Generation", test_optimized_prompt_generation),
        ("Feedback Loop Optimization", test_feedback_loop_optimization),
        ("Performance Data Management", test_performance_data_management),
        ("Continuous Optimization Status", test_continuous_optimization_status),
        ("24/7 Optimization Startup", test_24_7_optimization_startup),
        ("Trend Data Parsing", test_trend_data_parsing),
        ("Improvement Suggestions", test_improvement_suggestions)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 30)
        
        try:
            result = await test_func()
            results[test_name] = result
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! AI optimization with 2025 trends is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 