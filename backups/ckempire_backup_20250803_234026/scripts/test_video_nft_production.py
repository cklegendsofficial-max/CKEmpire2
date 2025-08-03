#!/usr/bin/env python3
"""
Test script for Video/NFT Production Module
Tests AI-powered video production, NFT generation, and pricing prediction
"""

import asyncio
import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoNFTTester:
    """Test class for Video/NFT production module"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
    
    async def test_video_health_check(self) -> Dict[str, Any]:
        """Test video module health check"""
        try:
            logger.info("Testing video health check...")
            response = self.session.get(f"{self.base_url}/api/v1/video/health")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Video health check passed: {data}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Video health check failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Video health check error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_video_styles(self) -> Dict[str, Any]:
        """Test getting available video styles"""
        try:
            logger.info("Testing get video styles...")
            response = self.session.get(f"{self.base_url}/api/v1/video/styles")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get video styles passed: {data}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get video styles failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get video styles error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_generate_video(self) -> Dict[str, Any]:
        """Test video generation with Zack Snyder style"""
        try:
            logger.info("Testing video generation...")
            
            payload = {
                "theme": "Epic battle between light and darkness",
                "duration": 120,
                "style": "zack_snyder"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/video/generate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Video generation passed: {data['production_id']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Video generation failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Video generation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_generate_nft(self) -> Dict[str, Any]:
        """Test NFT generation for video"""
        try:
            logger.info("Testing NFT generation...")
            
            # Mock video metadata
            video_metadata = {
                "title": "Cinematic Zack Snyder Style Video",
                "description": "Epic battle between light and darkness with dramatic lighting",
                "style": "Zack Snyder Style",
                "duration": "120 seconds",
                "resolution": "1920x1080",
                "frame_rate": "24 fps",
                "aspect_ratio": "2.35:1",
                "color_grading": {
                    "contrast": 1.3,
                    "saturation": 0.8,
                    "brightness": 0.9,
                    "gamma": 1.1
                },
                "effects": ["slow_motion", "dark_contrast", "cinematic_lighting"]
            }
            
            payload = {
                "video_metadata": video_metadata,
                "collection_name": "CKEmpire Videos"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/video/nft/generate",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ NFT generation passed: {data['status']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ NFT generation failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ NFT generation error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_predict_nft_pricing(self) -> Dict[str, Any]:
        """Test NFT pricing prediction"""
        try:
            logger.info("Testing NFT pricing prediction...")
            
            # Mock NFT metadata
            nft_metadata = {
                "name": "Epic Battle Cinematic Video",
                "description": "AI-generated cinematic video with Zack Snyder style",
                "image_url": "https://ckempire.com/video-preview.jpg",
                "animation_url": "https://ckempire.com/video.mp4",
                "attributes": [
                    {"trait_type": "Style", "value": "Zack Snyder Style"},
                    {"trait_type": "Resolution", "value": "1920x1080"},
                    {"trait_type": "Frame Rate", "value": "24 fps"},
                    {"trait_type": "Aspect Ratio", "value": "2.35:1"},
                    {"trait_type": "Effects", "value": 3},
                    {"trait_type": "Rarity", "value": "Legendary"}
                ],
                "external_url": "https://ckempire.com/nft",
                "seller_fee_basis_points": 500,
                "collection": {
                    "name": "CKEmpire Videos",
                    "family": "CKEmpire"
                }
            }
            
            payload = {
                "nft_metadata": nft_metadata,
                "market_data": {
                    "eth_price": 2000,
                    "market_trend": "bullish",
                    "similar_nfts_avg_price": 0.8
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/video/nft/pricing",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ NFT pricing prediction passed: {data['predicted_price']} ETH")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ NFT pricing prediction failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ NFT pricing prediction error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_get_nft_metadata(self) -> Dict[str, Any]:
        """Test getting NFT metadata"""
        try:
            logger.info("Testing get NFT metadata...")
            
            production_id = "test_prod_123"
            response = self.session.get(
                f"{self.base_url}/api/v1/video/nft/metadata/{production_id}"
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Get NFT metadata passed: {data['production_id']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Get NFT metadata failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Get NFT metadata error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_create_stripe_product(self) -> Dict[str, Any]:
        """Test creating Stripe product for NFT"""
        try:
            logger.info("Testing create Stripe product...")
            
            nft_metadata = {
                "name": "Epic Battle Cinematic Video",
                "description": "AI-generated cinematic video with Zack Snyder style",
                "image_url": "https://ckempire.com/video-preview.jpg",
                "animation_url": "https://ckempire.com/video.mp4",
                "attributes": [
                    {"trait_type": "Style", "value": "Zack Snyder Style"},
                    {"trait_type": "Rarity", "value": "Legendary"}
                ],
                "external_url": "https://ckempire.com/nft",
                "seller_fee_basis_points": 500,
                "collection": {
                    "name": "CKEmpire Videos",
                    "family": "CKEmpire"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/video/nft/create-stripe-product",
                json=nft_metadata
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Create Stripe product passed: {data['status']}")
                return {"status": "passed", "data": data}
            else:
                logger.error(f"❌ Create Stripe product failed: {response.status_code}")
                return {"status": "failed", "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Create Stripe product error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def test_video_manager_direct(self) -> Dict[str, Any]:
        """Test video manager directly"""
        try:
            logger.info("Testing video manager directly...")
            
            # Import video manager
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
            
            from video import video_manager
            
            # Test video prompt generation
            video_prompt = await video_manager.generate_video_prompt(
                theme="Epic battle between light and darkness",
                duration=120,
                style="zack_snyder"
            )
            
            # Test video metadata creation
            video_metadata = await video_manager.create_video_metadata(
                video_prompt=video_prompt,
                style="zack_snyder"
            )
            
            # Test NFT metadata generation
            nft_metadata = await video_manager.generate_nft_metadata(video_metadata)
            
            # Test pricing prediction
            pricing_prediction = await video_manager.predict_nft_pricing(nft_metadata)
            
            # Test Stripe product creation
            stripe_product = await video_manager.create_stripe_product(nft_metadata, pricing_prediction)
            
            logger.info("✅ Video manager direct tests passed")
            return {
                "status": "passed",
                "data": {
                    "video_prompt_length": len(video_prompt),
                    "video_metadata": video_metadata,
                    "nft_metadata": nft_metadata,
                    "pricing_prediction": pricing_prediction,
                    "stripe_product": stripe_product
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Video manager direct test error: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all video/NFT tests"""
        logger.info("🚀 Starting Video/NFT Production Module Tests")
        
        tests = [
            ("Video Health Check", self.test_video_health_check),
            ("Get Video Styles", self.test_get_video_styles),
            ("Generate Video", self.test_generate_video),
            ("Generate NFT", self.test_generate_nft),
            ("Predict NFT Pricing", self.test_predict_nft_pricing),
            ("Get NFT Metadata", self.test_get_nft_metadata),
            ("Create Stripe Product", self.test_create_stripe_product),
            ("Video Manager Direct", self.test_video_manager_direct)
        ]
        
        results = {}
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"Running: {test_name}")
            logger.info(f"{'='*50}")
            
            result = await test_func()
            results[test_name] = result
            
            if result["status"] == "passed":
                passed += 1
            elif result["status"] == "failed":
                failed += 1
            else:
                errors += 1
        
        # Generate summary
        summary = {
            "total_tests": len(tests),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "success_rate": (passed / len(tests)) * 100 if len(tests) > 0 else 0,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"\n{'='*60}")
        logger.info("📊 VIDEO/NFT PRODUCTION MODULE TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Tests: {summary['total_tests']}")
        logger.info(f"✅ Passed: {summary['passed']}")
        logger.info(f"❌ Failed: {summary['failed']}")
        logger.info(f"⚠️  Errors: {summary['errors']}")
        logger.info(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        logger.info(f"{'='*60}")
        
        return summary

async def main():
    """Main test function"""
    tester = VideoNFTTester()
    
    try:
        summary = await tester.run_all_tests()
        
        # Save results to file
        with open("video_nft_test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info("💾 Test results saved to video_nft_test_results.json")
        
        # Exit with appropriate code
        if summary["failed"] == 0 and summary["errors"] == 0:
            logger.info("🎉 All tests passed!")
            exit(0)
        else:
            logger.error("❌ Some tests failed!")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        logger.error(f"💥 Test execution failed: {e}")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 