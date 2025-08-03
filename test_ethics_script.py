#!/usr/bin/env python3
"""
Manual test script for ethics module
Demonstrates bias detection with sample content
"""

import sys
import os
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from backend.ethics import EthicsModule, BiasType, ContentStatus

def test_ethics_module():
    """Test the ethics module with various content samples"""
    
    print("🧪 Testing CK Empire Builder Ethics Module")
    print("=" * 50)
    
    # Initialize ethics module
    ethics_module = EthicsModule()
    
    # Sample content for testing
    test_cases = [
        {
            "name": "Neutral Content",
            "content": "Technology is advancing rapidly. Artificial intelligence is transforming various industries. Companies are adopting new digital solutions to improve efficiency.",
            "expected_bias": False
        },
        {
            "name": "Gender Bias Content",
            "content": "All men are better at technology than women. Women should stay at home and take care of children. Men are naturally more logical and analytical.",
            "expected_bias": True
        },
        {
            "name": "Racial Bias Content", 
            "content": "All Asians are good at math and science. Black people are naturally athletic. White people are more intelligent and successful.",
            "expected_bias": True
        },
        {
            "name": "Religious Bias Content",
            "content": "All Muslims are terrorists. Christians are the only good people. Jews control the world's money.",
            "expected_bias": True
        },
        {
            "name": "Economic Bias Content",
            "content": "Rich people are better than poor people. The wealthy deserve everything they have. Poor people are lazy and don't work hard enough.",
            "expected_bias": True
        },
        {
            "name": "Political Bias Content",
            "content": "All Democrats are socialists who want to destroy America. Republicans are the only true patriots. Liberals are destroying our country.",
            "expected_bias": True
        },
        {
            "name": "Mixed Bias Content",
            "content": "Men are better at technology than women, and Asians are naturally good at math. Rich people deserve their wealth while poor people are lazy.",
            "expected_bias": True
        }
    ]
    
    print(f"📊 Testing {len(test_cases)} content samples...")
    print()
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 Test {i}: {test_case['name']}")
        print(f"Content: {test_case['content'][:100]}...")
        
        try:
            # Analyze content
            report = ethics_module.analyze_content_ethical(
                content_data=test_case['content'],
                content_id=i
            )
            
            # Display results
            print(f"✅ Analysis completed:")
            print(f"   - Bias Detected: {report.bias_detected}")
            print(f"   - Bias Score: {report.bias_metrics.bias_score:.3f}")
            print(f"   - Fairness Score: {report.bias_metrics.fairness_score:.3f}")
            print(f"   - Content Status: {report.content_status.value}")
            print(f"   - Bias Types: {[bt.value for bt in report.bias_types]}")
            print(f"   - Flagged Keywords: {report.flagged_keywords}")
            print(f"   - Sensitive Topics: {report.sensitive_topics}")
            print(f"   - Confidence: {report.confidence_score:.3f}")
            print(f"   - Recommendations: {report.recommendations[:2]}...")
            
            # Check if analysis matches expectation
            if report.bias_detected == test_case['expected_bias']:
                print(f"   ✅ Expected bias detection: {test_case['expected_bias']}")
            else:
                print(f"   ⚠️  Unexpected bias detection: expected {test_case['expected_bias']}, got {report.bias_detected}")
            
            results.append({
                "test_case": test_case['name'],
                "bias_detected": report.bias_detected,
                "bias_score": report.bias_metrics.bias_score,
                "fairness_score": report.bias_metrics.fairness_score,
                "status": report.content_status.value,
                "bias_types": [bt.value for bt in report.bias_types],
                "flagged_keywords": report.flagged_keywords,
                "sensitive_topics": report.sensitive_topics,
                "confidence": report.confidence_score,
                "expected_bias": test_case['expected_bias'],
                "correct_prediction": report.bias_detected == test_case['expected_bias']
            })
            
        except Exception as e:
            print(f"❌ Error analyzing content: {e}")
            results.append({
                "test_case": test_case['name'],
                "error": str(e),
                "expected_bias": test_case['expected_bias'],
                "correct_prediction": False
            })
        
        print("-" * 50)
    
    # Summary
    print("📈 ANALYSIS SUMMARY")
    print("=" * 50)
    
    successful_tests = [r for r in results if "error" not in r]
    failed_tests = [r for r in results if "error" in r]
    
    print(f"Total Tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if successful_tests:
        correct_predictions = [r for r in successful_tests if r['correct_prediction']]
        accuracy = len(correct_predictions) / len(successful_tests) * 100
        
        print(f"Accuracy: {accuracy:.1f}% ({len(correct_predictions)}/{len(successful_tests)})")
        
        avg_bias_score = sum(r['bias_score'] for r in successful_tests) / len(successful_tests)
        avg_fairness_score = sum(r['fairness_score'] for r in successful_tests) / len(successful_tests)
        avg_confidence = sum(r['confidence'] for r in successful_tests) / len(successful_tests)
        
        print(f"Average Bias Score: {avg_bias_score:.3f}")
        print(f"Average Fairness Score: {avg_fairness_score:.3f}")
        print(f"Average Confidence: {avg_confidence:.3f}")
        
        # Bias type distribution
        all_bias_types = []
        for r in successful_tests:
            all_bias_types.extend(r['bias_types'])
        
        bias_type_counts = {}
        for bias_type in all_bias_types:
            bias_type_counts[bias_type] = bias_type_counts.get(bias_type, 0) + 1
        
        if bias_type_counts:
            print("\nBias Type Distribution:")
            for bias_type, count in bias_type_counts.items():
                print(f"  - {bias_type}: {count}")
    
    # Test batch analysis
    print("\n🔄 Testing Batch Analysis")
    print("=" * 30)
    
    batch_contents = [
        "This is neutral content about technology.",
        "All men are better than women at coding.",
        "Technology is advancing rapidly.",
        "Rich people are better than poor people."
    ]
    
    try:
        batch_results = []
        for i, content in enumerate(batch_contents):
            report = ethics_module.analyze_content_ethical(content, i + 100)
            batch_results.append({
                "content_id": i + 100,
                "bias_detected": report.bias_detected,
                "bias_score": report.bias_metrics.bias_score,
                "status": report.content_status.value
            })
        
        print("Batch Analysis Results:")
        for result in batch_results:
            print(f"  - Content {result['content_id']}: Bias={result['bias_detected']}, Score={result['bias_score']:.3f}, Status={result['status']}")
    
    except Exception as e:
        print(f"❌ Batch analysis failed: {e}")
    
    # Test module summary
    print("\n📊 Module Summary")
    print("=" * 30)
    
    try:
        summary = ethics_module.get_ethics_summary()
        print(f"Total Analyses: {summary['total_analyses']}")
        print(f"Flagged Content: {summary['flagged_content']}")
        print(f"Average Bias Score: {summary['average_bias_score']:.3f}")
        print(f"Flag Rate: {summary['flag_rate']:.1%}")
    
    except Exception as e:
        print(f"❌ Module summary failed: {e}")
    
    # Test configuration
    print("\n⚙️  Testing Configuration")
    print("=" * 30)
    
    try:
        original_bias_threshold = ethics_module.bias_threshold
        original_fairness_threshold = ethics_module.fairness_threshold
        
        # Change thresholds
        ethics_module.bias_threshold = 0.05
        ethics_module.fairness_threshold = 0.9
        
        print(f"Updated Bias Threshold: {ethics_module.bias_threshold}")
        print(f"Updated Fairness Threshold: {ethics_module.fairness_threshold}")
        
        # Test with new thresholds
        test_content = "This is a neutral content."
        report = ethics_module.analyze_content_ethical(test_content)
        print(f"Analysis with new thresholds: Bias={report.bias_detected}, Status={report.content_status.value}")
        
        # Restore original thresholds
        ethics_module.bias_threshold = original_bias_threshold
        ethics_module.fairness_threshold = original_fairness_threshold
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
    
    print("\n✅ Ethics module testing completed!")
    print("=" * 50)

def test_api_endpoints():
    """Test ethics API endpoints"""
    
    print("\n🌐 Testing Ethics API Endpoints")
    print("=" * 40)
    
    try:
        from fastapi.testclient import TestClient
        from backend.main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        print("Testing /api/v1/ethics/health...")
        response = client.get("/api/v1/ethics/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Test ethics check endpoint
        print("Testing /api/v1/ethics/check...")
        request_data = {
            "content": "All men are better at technology than women.",
            "content_id": 1,
            "user_id": 1
        }
        response = client.post("/api/v1/ethics/check", json=request_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ethics check passed: Bias detected={data['bias_detected']}")
        else:
            print(f"❌ Ethics check failed: {response.status_code}")
        
        # Test stats endpoint
        print("Testing /api/v1/ethics/stats...")
        response = client.get("/api/v1/ethics/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint passed: {data['total_analyses']} analyses")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
        
        # Test summary endpoint
        print("Testing /api/v1/ethics/summary...")
        response = client.get("/api/v1/ethics/summary")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Summary endpoint passed: {len(data['bias_types'])} bias types")
        else:
            print(f"❌ Summary endpoint failed: {response.status_code}")
    
    except Exception as e:
        print(f"❌ API testing failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting CK Empire Builder Ethics Module Tests")
    print("=" * 60)
    
    # Test the ethics module
    test_ethics_module()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("\n🎉 All tests completed!")
    print("=" * 60) 