#!/usr/bin/env python3
"""
Performance testing script for CK Empire Builder
"""

import time
import requests
import json
from datetime import datetime

def test_performance_features():
    """Test performance features"""
    base_url = "http://localhost:8000"
    
    print("🏛️ CK Empire Builder - Performance Testing")
    print("=" * 50)
    
    # Test 1: Basic API endpoints
    print("\n1. Testing basic API endpoints...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"✅ Root endpoint: {response.status_code}")
        
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
        
        response = requests.get(f"{base_url}/api/v1/status")
        print(f"✅ API status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start the server first.")
        return
    
    # Test 2: Performance metrics
    print("\n2. Testing performance metrics...")
    try:
        response = requests.get(f"{base_url}/api/v1/metrics")
        if response.status_code == 200:
            print("✅ Prometheus metrics endpoint working")
            metrics_data = response.text
            if "http_requests_total" in metrics_data:
                print("✅ HTTP request metrics found")
        else:
            print(f"❌ Metrics endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
    
    # Test 3: Performance summary
    print("\n3. Testing performance summary...")
    try:
        response = requests.get(f"{base_url}/api/v1/performance/summary")
        if response.status_code == 200:
            summary = response.json()
            print("✅ Performance summary:")
            print(f"   - Uptime: {summary['data']['uptime']:.2f} seconds")
            print(f"   - Total queries: {summary['data']['total_queries']}")
            print(f"   - Average query time: {summary['data']['average_query_time']:.3f}s")
            print(f"   - Cache hit rate: {summary['data']['cache_hit_rate']:.1f}%")
        else:
            print(f"❌ Performance summary failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Performance summary test failed: {e}")
    
    # Test 4: Cache statistics
    print("\n4. Testing cache statistics...")
    try:
        response = requests.get(f"{base_url}/api/v1/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Cache statistics:")
            print(f"   - Hit rate: {stats['data']['hit_rate']:.1f}%")
            print(f"   - Hits: {stats['data']['hits']}")
            print(f"   - Misses: {stats['data']['misses']}")
            print(f"   - Total requests: {stats['data']['total_requests']}")
        else:
            print(f"❌ Cache stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cache stats test failed: {e}")
    
    # Test 5: Performance analysis
    print("\n5. Testing performance analysis...")
    try:
        response = requests.get(f"{base_url}/api/v1/performance/analysis")
        if response.status_code == 200:
            analysis = response.json()
            print("✅ Performance analysis:")
            print(f"   - Total queries: {analysis['data']['summary']['total_queries']}")
            print(f"   - Slow queries: {analysis['data']['summary']['slow_queries_count']}")
            print(f"   - Recommendations: {len(analysis['data']['recommendations'])}")
            
            if analysis['data']['recommendations']:
                print("   - Top recommendations:")
                for rec in analysis['data']['recommendations'][:3]:
                    print(f"     * {rec['message']}")
        else:
            print(f"❌ Performance analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Performance analysis test failed: {e}")
    
    # Test 6: Cached endpoints
    print("\n6. Testing cached endpoints...")
    try:
        # First call (cache miss)
        start_time = time.time()
        response1 = requests.get(f"{base_url}/api/v1/performance/cached-summary")
        first_duration = time.time() - start_time
        
        # Second call (cache hit)
        start_time = time.time()
        response2 = requests.get(f"{base_url}/api/v1/performance/cached-summary")
        second_duration = time.time() - start_time
        
        if response1.status_code == 200 and response2.status_code == 200:
            print("✅ Cached endpoint test:")
            print(f"   - First call (cache miss): {first_duration:.3f}s")
            print(f"   - Second call (cache hit): {second_duration:.3f}s")
            print(f"   - Speed improvement: {((first_duration - second_duration) / first_duration * 100):.1f}%")
        else:
            print(f"❌ Cached endpoint failed: {response1.status_code}, {response2.status_code}")
    except Exception as e:
        print(f"❌ Cached endpoint test failed: {e}")
    
    # Test 7: Database recommendations
    print("\n7. Testing database recommendations...")
    try:
        response = requests.get(f"{base_url}/api/v1/performance/recommendations")
        if response.status_code == 200:
            recommendations = response.json()
            print("✅ Database recommendations:")
            print(f"   - Total recommendations: {recommendations['data']['total_count']}")
            
            if recommendations['data']['recommendations']:
                print("   - Recommendations:")
                for rec in recommendations['data']['recommendations']:
                    print(f"     * {rec['recommendation']} ({rec['priority']})")
        else:
            print(f"❌ Database recommendations failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Database recommendations test failed: {e}")
    
    # Test 8: Slow queries
    print("\n8. Testing slow queries endpoint...")
    try:
        response = requests.get(f"{base_url}/api/v1/performance/slow-queries?threshold=0.5")
        if response.status_code == 200:
            slow_queries = response.json()
            print("✅ Slow queries:")
            print(f"   - Threshold: {slow_queries['data']['threshold']}s")
            print(f"   - Count: {slow_queries['data']['count']}")
            
            if slow_queries['data']['slow_queries']:
                print("   - Slow queries found:")
                for query in slow_queries['data']['slow_queries'][:3]:
                    print(f"     * {query['query']} ({query['duration']:.3f}s)")
        else:
            print(f"❌ Slow queries failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Slow queries test failed: {e}")
    
    # Test 9: Performance health check
    print("\n9. Testing performance health check...")
    try:
        response = requests.get(f"{base_url}/api/v1/performance/health")
        if response.status_code == 200:
            health = response.json()
            print("✅ Performance health check:")
            print(f"   - Status: {health['status']}")
            print(f"   - Redis: {health['data']['redis']}")
            print(f"   - Metrics collection: {health['data']['metrics_collection']}")
            print(f"   - Cache hit rate: {health['data']['cache_hit_rate']:.1f}%")
        else:
            print(f"❌ Performance health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Performance health check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Performance testing completed!")
    print("\nTo view real-time metrics:")
    print("1. Visit http://localhost:8000/api/v1/metrics for Prometheus metrics")
    print("2. Visit http://localhost:8000/docs for API documentation")
    print("3. Check logs/ directory for detailed logs")

def simulate_load():
    """Simulate load to generate performance data"""
    base_url = "http://localhost:8000"
    
    print("\n🔄 Simulating load...")
    
    # Make multiple requests to generate metrics
    for i in range(10):
        try:
            # Test different endpoints
            endpoints = [
                "/",
                "/health",
                "/api/v1/status",
                "/api/v1/performance/summary",
                "/api/v1/cache/stats"
            ]
            
            for endpoint in endpoints:
                response = requests.get(f"{base_url}{endpoint}")
                if response.status_code == 200:
                    print(f"✅ Request {i+1}: {endpoint}")
                else:
                    print(f"❌ Request {i+1}: {endpoint} - {response.status_code}")
                
                time.sleep(0.1)  # Small delay between requests
                
        except Exception as e:
            print(f"❌ Load simulation error: {e}")
            break
    
    print("✅ Load simulation completed!")

if __name__ == "__main__":
    test_performance_features()
    
    # Ask if user wants to simulate load
    try:
        choice = input("\nDo you want to simulate load to generate more metrics? (y/n): ")
        if choice.lower() in ['y', 'yes']:
            simulate_load()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!") 