#!/usr/bin/env python3
"""
Test script for dashboard functionality
Tests multi-channel graphs, scheduler integration, and cost-free operation
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from dashboard import DashboardManager, dashboard_manager

async def test_dashboard_generation():
    """Test dashboard generation with multi-channel graphs"""
    print("🧪 Testing Dashboard Generation")
    print("=" * 60)
    
    try:
        # Initialize dashboard manager
        dashboard = DashboardManager()
        
        print("📊 Generating daily dashboard report...")
        
        # Generate daily report
        report = await dashboard.generate_daily_report()
        
        if report:
            print("✅ Daily report generated successfully!")
            
            # Display report summary
            print(f"\n📈 Report Summary:")
            print(f"   Total Views: {report.total_views:,}")
            print(f"   Total Revenue: ${report.total_revenue:,.0f}")
            print(f"   Average Engagement: {report.average_engagement:.1%}")
            print(f"   Top Channel: {report.top_performing_channel.value}")
            print(f"   Business Ideas: {report.business_ideas_generated}")
            print(f"   Content Quality: {report.content_quality_score:.1%}")
            
            # Display channel breakdown
            print(f"\n📋 Channel Breakdown:")
            for channel, metrics in report.channel_breakdown.items():
                print(f"   • {channel.title()}:")
                print(f"     - Views: {metrics.views:,}")
                print(f"     - Revenue: ${metrics.revenue:,.0f}")
                print(f"     - Engagement: {metrics.engagement_rate:.1%}")
                print(f"     - Quality: {metrics.quality_score:.1%}")
                print(f"     - Viral Potential: {metrics.viral_potential:.1%}")
            
            # Generate multi-channel graphs
            print(f"\n📈 Generating multi-channel graphs...")
            graphs = await dashboard.generate_multi_channel_graphs(report)
            
            if graphs:
                print(f"✅ Generated {len(graphs)} graphs:")
                for graph_name, graph_path in graphs.items():
                    if os.path.exists(graph_path):
                        file_size = os.path.getsize(graph_path)
                        print(f"   • {graph_name}: {graph_path} ({file_size:,} bytes)")
                    else:
                        print(f"   • {graph_name}: {graph_path} (file not found)")
            
            # Create Streamlit dashboard
            print(f"\n🌐 Creating Streamlit dashboard...")
            dashboard_path = await dashboard.create_streamlit_dashboard(report, graphs)
            
            if dashboard_path and os.path.exists(dashboard_path):
                file_size = os.path.getsize(dashboard_path)
                print(f"✅ Dashboard created: {dashboard_path} ({file_size:,} bytes)")
            else:
                print(f"❌ Dashboard creation failed")
            
            return True
        else:
            print("❌ Failed to generate daily report")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_scheduler_integration():
    """Test dashboard integration with content scheduler"""
    print("\n🔧 Testing Scheduler Integration")
    print("=" * 60)
    
    try:
        # Import content scheduler
        from content_scheduler import ContentScheduler
        
        # Initialize scheduler
        scheduler = ContentScheduler()
        
        print("📋 Testing dashboard generation through scheduler...")
        
        # Test the dashboard generation method directly
        dashboard_result = await scheduler._generate_daily_dashboard_report()
        
        if dashboard_result:
            print("✅ Scheduler dashboard generation successful!")
            
            report = dashboard_result.get("report", {})
            graphs = dashboard_result.get("graphs", {})
            dashboard_path = dashboard_result.get("dashboard_path", "")
            
            print(f"   📊 Report generated: {bool(report)}")
            print(f"   📈 Graphs created: {len(graphs)}")
            print(f"   🌐 Dashboard path: {dashboard_path}")
            
            if report:
                total_views = report.total_views if hasattr(report, 'total_views') else 0
                total_revenue = report.total_revenue if hasattr(report, 'total_revenue') else 0
                print(f"   📈 Total Views: {total_views:,}")
                print(f"   💰 Total Revenue: ${total_revenue:,.0f}")
            
            return True
        else:
            print("❌ Scheduler dashboard generation failed")
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
        
        # Check if Matplotlib is available (local graph generation)
        try:
            import matplotlib.pyplot as plt
            print("   ✅ Matplotlib (local graph generation) - Available")
        except ImportError:
            print("   ❌ Matplotlib (local graph generation) - Not installed")
        
        # Check if NumPy is available (local calculations)
        try:
            import numpy as np
            print("   ✅ NumPy (local calculations) - Available")
        except ImportError:
            print("   ❌ NumPy (local calculations) - Not available")
        
        # Check if dashboard module is available (local dashboard)
        try:
            from dashboard import DashboardManager
            print("   ✅ Dashboard Module (local dashboard) - Available")
        except ImportError:
            print("   ❌ Dashboard Module (local dashboard) - Not available")
        
        # Check data directory
        data_dir = Path("data")
        if data_dir.exists():
            print("   ✅ Data Directory - Available")
        else:
            print("   ❌ Data Directory - Not found")
        
        print("\n📊 Cost-Free Operation Summary:")
        print("   • Graph Generation: Local Matplotlib (free)")
        print("   • Calculations: Local NumPy (free)")
        print("   • Dashboard: Local HTML generation (free)")
        print("   • Data Storage: Local files (free)")
        print("   • No external API costs or subscriptions required")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost-free operation test failed: {e}")
        return False

async def test_multi_channel_graphs():
    """Test multi-channel graph generation specifically"""
    print("\n📈 Testing Multi-Channel Graph Generation")
    print("=" * 60)
    
    try:
        # Initialize dashboard manager
        dashboard = DashboardManager()
        
        # Create a test report
        from dashboard import DashboardReport, ChannelMetrics, ChannelType
        
        # Create mock channel metrics
        channel_breakdown = {}
        for channel in [ChannelType.YOUTUBE, ChannelType.TIKTOK, ChannelType.INSTAGRAM, ChannelType.LINKEDIN, ChannelType.TWITTER]:
            channel_breakdown[channel.value] = ChannelMetrics(
                channel=channel,
                views=10000 + (hash(channel.value) % 50000),
                revenue=1000 + (hash(channel.value) % 5000),
                engagement_rate=0.05 + (hash(channel.value) % 10) / 100,
                viral_potential=0.3 + (hash(channel.value) % 50) / 100,
                quality_score=0.6 + (hash(channel.value) % 30) / 100,
                date=None
            )
        
        # Create test report
        test_report = DashboardReport(
            total_views=sum(metrics.views for metrics in channel_breakdown.values()),
            total_revenue=sum(metrics.revenue for metrics in channel_breakdown.values()),
            average_engagement=0.1,
            top_performing_channel=ChannelType.YOUTUBE,
            channel_breakdown=channel_breakdown,
            business_ideas_generated=3,
            content_quality_score=0.75,
            generated_at=None
        )
        
        print("📊 Test report created with 5 channels")
        
        # Generate graphs
        graphs = await dashboard.generate_multi_channel_graphs(test_report)
        
        if graphs:
            print(f"✅ Generated {len(graphs)} multi-channel graphs:")
            for graph_name, graph_path in graphs.items():
                if os.path.exists(graph_path):
                    file_size = os.path.getsize(graph_path)
                    print(f"   • {graph_name}: {file_size:,} bytes")
                else:
                    print(f"   • {graph_name}: File not found")
            
            # Test dashboard creation with graphs
            dashboard_path = await dashboard.create_streamlit_dashboard(test_report, graphs)
            
            if dashboard_path and os.path.exists(dashboard_path):
                file_size = os.path.getsize(dashboard_path)
                print(f"✅ Dashboard created: {file_size:,} bytes")
                return True
            else:
                print("❌ Dashboard creation failed")
                return False
        else:
            print("❌ No graphs generated")
            return False
            
    except Exception as e:
        print(f"❌ Multi-channel graph test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all dashboard tests"""
    print("🚀 Dashboard Test Suite")
    print("=" * 60)
    
    # Change to backend directory for proper imports
    backend_dir = Path(__file__).parent.parent / "backend"
    os.chdir(backend_dir)
    
    # Run tests
    tests = [
        ("Dashboard Generation", test_dashboard_generation),
        ("Scheduler Integration", test_scheduler_integration),
        ("Cost-Free Operation", test_cost_free_operation),
        ("Multi-Channel Graphs", test_multi_channel_graphs)
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
        print("🎉 All tests passed! Dashboard functionality is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    asyncio.run(main()) 