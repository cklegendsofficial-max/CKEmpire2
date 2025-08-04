#!/usr/bin/env python3
"""
Test Monetization Forecast Script for CK Empire
Tests the new monetization forecast functionality with multi-channel analysis
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from ai import AIModule
from finance import FinanceManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonetizationForecastTester:
    """Test monetization forecast functionality"""
    
    def __init__(self):
        self.ai_module = AIModule()
        self.finance_manager = FinanceManager()
    
    async def test_finance_calculate_max_digital_income(self) -> Dict[str, Any]:
        """Test the calculate_max_digital_income function"""
        print("\n💰 Testing Finance Module - calculate_max_digital_income...")
        
        try:
            # Test with default channels
            channels = ["YouTube", "TikTok", "Instagram", "LinkedIn", "Twitter"]
            
            result = self.finance_manager.calculate_max_digital_income(channels=channels)
            
            print(f"✅ Finance calculation successful")
            print(f"📊 Total Revenue: ${result['total_revenue']:.2f}")
            print(f"📈 Ads Revenue: ${result['ads_revenue']:.2f}")
            print(f"🔗 Affiliate Revenue: ${result['affiliate_revenue']:.2f}")
            print(f"🛍️ Product Revenue: ${result['product_revenue']:.2f}")
            print(f"📊 ROI: {result['roi_analysis']['roi_percentage']:.2f}%")
            
            # Check channel breakdown
            for channel, data in result['channel_breakdown'].items():
                print(f"   📱 {channel}: ${data['total_revenue']:.2f}/month")
            
            return {
                "success": True,
                "total_revenue": result['total_revenue'],
                "roi_percentage": result['roi_analysis']['roi_percentage'],
                "channel_count": len(result['channel_breakdown']),
                "monthly_forecast_count": len(result['monthly_forecast']),
                "recommendations_count": len(result['recommendations'])
            }
            
        except Exception as e:
            print(f"❌ Finance calculation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_ai_generate_monetization_for_channels(self) -> Dict[str, Any]:
        """Test the generate_monetization_for_channels method"""
        print("\n🎯 Testing AI Module - generate_monetization_for_channels...")
        
        try:
            channels = ["YouTube", "TikTok", "Instagram", "LinkedIn", "Twitter"]
            
            result = await self.ai_module.generate_monetization_for_channels(channels)
            
            if result.get("status") == "success":
                print(f"✅ AI monetization generation successful")
                print(f"📊 Total Potential Revenue: ${result['total_potential_revenue']:.2f}")
                print(f"📈 Monthly Revenue: ${result['financial_analysis']['total_revenue']:.2f}")
                print(f"📊 ROI: {result['roi_analysis']['roi_percentage']:.2f}%")
                
                # Check monetization suggestions
                suggestions = result.get("monetization_suggestions", {})
                if "monetization_strategies" in suggestions:
                    for channel, strategies in suggestions["monetization_strategies"].items():
                        print(f"   📱 {channel}: {', '.join(strategies[:3])}...")
                
                return {
                    "success": True,
                    "total_potential_revenue": result['total_potential_revenue'],
                    "roi_percentage": result['roi_analysis']['roi_percentage'],
                    "channel_count": len(result['channels']),
                    "monthly_forecast_count": len(result['monthly_forecast']),
                    "yearly_revenue": result['yearly_forecast']['total_revenue']
                }
            else:
                print(f"❌ AI monetization generation failed: {result.get('error', 'Unknown error')}")
                return {"success": False, "error": result.get('error', 'Unknown error')}
                
        except Exception as e:
            print(f"❌ AI monetization generation error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_csv_tracking(self) -> Dict[str, Any]:
        """Test CSV tracking functionality"""
        print("\n📊 Testing CSV Tracking...")
        
        try:
            # Check if CSV file was created
            data_dir = Path("data")
            csv_file = data_dir / "monetization_analytics.csv"
            
            if csv_file.exists():
                print(f"✅ CSV file created: {csv_file}")
                
                # Read and check CSV content
                import csv
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    
                    if len(rows) > 1:  # Headers + at least one data row
                        print(f"✅ CSV contains {len(rows)-1} data rows")
                        latest_row = rows[-1]
                        print(f"📊 Latest entry: Revenue=${latest_row[2]}, ROI={latest_row[5]}%")
                        
                        return {
                            "success": True,
                            "file_exists": True,
                            "row_count": len(rows) - 1,
                            "latest_revenue": float(latest_row[2]) if latest_row[2] else 0
                        }
                    else:
                        print("⚠️ CSV file exists but no data rows found")
                        return {"success": False, "error": "No data rows in CSV"}
            else:
                print("❌ CSV file not found")
                return {"success": False, "error": "CSV file not created"}
                
        except Exception as e:
            print(f"❌ CSV tracking error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_custom_parameters(self) -> Dict[str, Any]:
        """Test with custom parameters"""
        print("\n🔧 Testing Custom Parameters...")
        
        try:
            channels = ["YouTube", "TikTok"]
            
            # Custom parameters
            monthly_views = {
                "YouTube": 100000,  # Higher views
                "TikTok": 200000
            }
            
            rpm_rates = {
                "YouTube": 5.00,  # Higher RPM
                "TikTok": 3.00
            }
            
            result = self.finance_manager.calculate_max_digital_income(
                channels=channels,
                monthly_views_per_channel=monthly_views,
                rpm_rates=rpm_rates
            )
            
            print(f"✅ Custom parameters test successful")
            print(f"📊 Total Revenue: ${result['total_revenue']:.2f}")
            print(f"📈 ROI: {result['roi_analysis']['roi_percentage']:.2f}%")
            
            return {
                "success": True,
                "total_revenue": result['total_revenue'],
                "roi_percentage": result['roi_analysis']['roi_percentage'],
                "channel_count": len(result['channel_breakdown'])
            }
            
        except Exception as e:
            print(f"❌ Custom parameters test error: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all monetization forecast tests"""
        print("🚀 CK Empire Monetization Forecast Test Suite")
        print("=" * 50)
        
        all_results = {}
        
        # Test finance module
        all_results['finance_calculation'] = await self.test_finance_calculate_max_digital_income()
        
        # Test AI module
        all_results['ai_generation'] = await self.test_ai_generate_monetization_for_channels()
        
        # Test CSV tracking
        all_results['csv_tracking'] = await self.test_csv_tracking()
        
        # Test custom parameters
        all_results['custom_parameters'] = await self.test_custom_parameters()
        
        # Calculate overall success rate
        successful_tests = sum(1 for result in all_results.values() if result.get("success", False))
        total_tests = len(all_results)
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n📊 Test Results Summary:")
        print(f"✅ Successful tests: {successful_tests}/{total_tests}")
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monetization_forecast_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {filename}")
        
        return all_results

async def main():
    """Main test function"""
    try:
        tester = MonetizationForecastTester()
        results = await tester.run_all_tests()
        
        # Print final assessment
        successful_tests = sum(1 for result in results.values() if result.get("success", False))
        total_tests = len(results)
        
        if successful_tests == total_tests:
            print("\n🎉 All monetization forecast features are working excellently!")
        elif successful_tests >= total_tests * 0.7:
            print("\n⚠️ Most monetization forecast features are working, but some improvements needed.")
        else:
            print("\n❌ Several monetization forecast features need attention.")
            
    except Exception as e:
        print(f"❌ Test suite error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 