#!/usr/bin/env python3
"""
AI Video/NFT Minting Test Script
Tests AI-powered video generation, NFT metadata optimization, and minting capabilities
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Mock config to avoid import issues
class MockSettings:
    def __init__(self):
        self.encryption_key = "test_key_12345"
        self.database_url = "sqlite:///test.db"
        self.DATABASE_URL = "sqlite:///test.db"
        self.secret_key = "test_secret_key"
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.redis_url = "redis://localhost:6379"
        self.vault_url = "http://localhost:8200"
        self.vault_token = "test_token"
        self.stripe_secret_key = "sk_test_123"
        self.stripe_publishable_key = "pk_test_123"
        self.openai_api_key = "sk-test-123"
        self.sentry_dsn = "https://test@sentry.io/123"
        self.log_level = "INFO"
        self.environment = "test"
        self.DEBUG = False
        self.TESTING = True
        self.DEVELOPMENT = False
        self.PRODUCTION = False
        self.API_V1_STR = "/api/v1"
        self.PROJECT_NAME = "CK Empire"
        self.BACKEND_CORS_ORIGINS = ["http://localhost:3000"]
        self.SUPERUSER_EMAIL = "admin@ckempire.com"
        self.SUPERUSER_PASSWORD = "admin123"
        self.FIRST_SUPERUSER = "admin@ckempire.com"
        self.FIRST_SUPERUSER_PASSWORD = "admin123"
        self.USERS_OPEN_REGISTRATION = True
        self.EMAILS_FROM_EMAIL = "noreply@ckempire.com"
        self.EMAILS_FROM_NAME = "CK Empire"
        self.SMTP_TLS = True
        self.SMTP_PORT = 587
        self.SMTP_HOST = "smtp.gmail.com"
        self.SMTP_USER = "test@example.com"
        self.SMTP_PASSWORD = "test_password"
        self.EMAILS_ENABLED = False
        self.EMAIL_TEST_USER = "test@example.com"
        self.SERVER_NAME = "localhost"
        self.SERVER_HOST = "http://localhost"
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.API_V1_STR = "/api/v1"
        self.PROJECT_NAME = "CK Empire"
        self.VERSION = "1.0.0"
        self.DESCRIPTION = "CK Empire API"
        self.AUTHOR = "CK Empire Team"
        self.EMAIL = "admin@ckempire.com"
        self.LICENSE = "MIT"
        self.URL = "https://ckempire.com"

# Mock the config module
sys.modules['config'] = type('MockConfig', (), {'settings': MockSettings()})

try:
    from video import video_manager, VideoStyle, NFTMetadata, PricingPrediction, AIMintingConfig
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

class VideoNFTMintingTester:
    """Test AI video/NFT minting capabilities"""
    
    def __init__(self):
        self.test_results = {}
        self.test_themes = [
            "Epic battle between light and darkness",
            "Futuristic cityscape with flying cars",
            "Emotional journey through time",
            "Cosmic exploration of distant galaxies"
        ]
        self.test_styles = ["zack_snyder", "action", "dramatic", "sci_fi"]
        
    def test_ai_video_prompt_generation(self) -> Dict[str, Any]:
        """Test AI video prompt generation"""
        print("\n🎬 Testing AI Video Prompt Generation...")
        results = {}
        
        for theme in self.test_themes:
            for style in self.test_styles:
                try:
                    prompt = asyncio.run(video_manager.generate_ai_video_prompt(
                        theme=theme,
                        duration=120,
                        style=style
                    ))
                    
                    results[f"{style}_{theme[:20]}"] = {
                        'success': True,
                        'prompt_length': len(prompt),
                        'style': style,
                        'theme': theme,
                        'ai_enhanced': 'ai_enhanced' in prompt.lower() or 'blockchain' in prompt.lower(),
                        'minting_ready': 'nft' in prompt.lower() or 'blockchain' in prompt.lower()
                    }
                    
                    print(f"  ✅ {style}: {theme[:30]}... - {len(prompt)} chars")
                    
                except Exception as e:
                    results[f"{style}_{theme[:20]}"] = {
                        'success': False,
                        'error': str(e)
                    }
                    print(f"  ❌ {style}: {theme[:30]}... - Error: {e}")
        
        return results
    
    def test_enhanced_video_metadata(self) -> Dict[str, Any]:
        """Test enhanced video metadata creation"""
        print("\n📋 Testing Enhanced Video Metadata...")
        results = {}
        
        for style in self.test_styles:
            try:
                mock_prompt = f"AI-enhanced {style} video with blockchain-ready metadata"
                metadata = asyncio.run(video_manager.create_enhanced_video_metadata(mock_prompt, style))
                
                results[style] = {
                    'success': True,
                    'production_id': metadata.get('production_id', ''),
                    'ai_enhanced': metadata.get('ai_enhanced', False),
                    'minting_ready': metadata.get('minting_ready', False),
                    'rarity_level': metadata.get('rarity_level', 'Unknown'),
                    'base_price': metadata.get('base_price', 0.0),
                    'ai_model_version': metadata.get('ai_model_version', '')
                }
                
                print(f"  ✅ {style}: AI={metadata.get('ai_enhanced')}, Minting={metadata.get('minting_ready')}, Price={metadata.get('base_price')} ETH")
                
            except Exception as e:
                results[style] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {style}: Error - {e}")
        
        return results
    
    def test_nft_metadata_optimization(self) -> Dict[str, Any]:
        """Test AI-optimized NFT metadata generation"""
        print("\n🎨 Testing NFT Metadata Optimization...")
        results = {}
        
        for style in self.test_styles:
            try:
                # Create mock video metadata
                video_metadata = {
                    'title': f'AI-Enhanced {style.title()} Video',
                    'style': f'{style.title()} Style',
                    'resolution': '1920x1080',
                    'frame_rate': '24 fps',
                    'aspect_ratio': '2.35:1',
                    'effects': ['ai_enhanced', 'blockchain_ready'],
                    'ai_enhanced': True,
                    'minting_ready': True,
                    'rarity_level': 'Legendary' if style == 'zack_snyder' else 'Epic',
                    'base_price': 2.0 if style == 'zack_snyder' else 1.5,
                    'ai_model_version': 'gpt-4-turbo'
                }
                
                nft_metadata = asyncio.run(video_manager.generate_optimized_nft_metadata(video_metadata))
                
                results[style] = {
                    'success': True,
                    'name': nft_metadata.name,
                    'ai_generated': nft_metadata.ai_generated,
                    'rarity_score': nft_metadata.rarity_score,
                    'attributes_count': len(nft_metadata.attributes),
                    'blockchain_ready': 'Ethereum' in str(nft_metadata.attributes),
                    'ai_enhanced_attr': any('AI' in attr.get('trait_type', '') for attr in nft_metadata.attributes)
                }
                
                print(f"  ✅ {style}: Score={nft_metadata.rarity_score:.2f}, AI={nft_metadata.ai_generated}, Attrs={len(nft_metadata.attributes)}")
                
            except Exception as e:
                results[style] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {style}: Error - {e}")
        
        return results
    
    def test_enhanced_pricing_prediction(self) -> Dict[str, Any]:
        """Test enhanced pricing prediction with ML model"""
        print("\n💰 Testing Enhanced Pricing Prediction...")
        results = {}
        
        for style in self.test_styles:
            try:
                # Create mock NFT metadata
                nft_metadata = NFTMetadata(
                    name=f"AI-Enhanced {style.title()} NFT",
                    description=f"AI-generated {style} video with blockchain optimization",
                    image_url="https://ckempire.com/ai-video.jpg",
                    animation_url="https://ckempire.com/ai-video.mp4",
                    attributes=[
                        {"trait_type": "Style", "value": f"{style.title()} Style"},
                        {"trait_type": "AI Enhanced", "value": "Yes"},
                        {"trait_type": "Rarity", "value": "Legendary" if style == "zack_snyder" else "Epic"},
                        {"trait_type": "Base Price", "value": f"{2.0 if style == 'zack_snyder' else 1.5} ETH"}
                    ],
                    external_url="https://ckempire.com/nft",
                    seller_fee_basis_points=500,
                    collection={"name": "CKEmpire AI Videos", "family": "CKEmpire AI"},
                    ai_generated=True,
                    minting_timestamp=datetime.now(),
                    blockchain_metadata={
                        "contract_address": "0x1234567890abcdef",
                        "token_standard": "ERC-721",
                        "blockchain": "Ethereum"
                    },
                    rarity_score=0.85 if style == "zack_snyder" else 0.75,
                    market_analysis={
                        "similar_nfts": 150,
                        "average_price": 1.2,
                        "market_trend": "bullish"
                    }
                )
                
                pricing_prediction = asyncio.run(video_manager.predict_enhanced_nft_pricing(nft_metadata))
                
                results[style] = {
                    'success': True,
                    'predicted_price': pricing_prediction.predicted_price,
                    'confidence': pricing_prediction.confidence,
                    'ml_model_version': pricing_prediction.ml_model_version,
                    'training_data_points': pricing_prediction.training_data_points,
                    'market_volatility': pricing_prediction.market_volatility,
                    'factors_count': len(pricing_prediction.factors),
                    'competitor_analysis': bool(pricing_prediction.competitor_analysis)
                }
                
                print(f"  ✅ {style}: Price={pricing_prediction.predicted_price:.2f} ETH, Confidence={pricing_prediction.confidence:.2f}")
                
            except Exception as e:
                results[style] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {style}: Error - {e}")
        
        return results
    
    def test_enhanced_stripe_product_creation(self) -> Dict[str, Any]:
        """Test enhanced Stripe product creation"""
        print("\n💳 Testing Enhanced Stripe Product Creation...")
        results = {}
        
        for style in self.test_styles:
            try:
                # Create mock NFT metadata and pricing prediction
                nft_metadata = NFTMetadata(
                    name=f"AI-Enhanced {style.title()} NFT",
                    description=f"AI-generated {style} video",
                    image_url="https://ckempire.com/ai-video.jpg",
                    animation_url="https://ckempire.com/ai-video.mp4",
                    attributes=[{"trait_type": "Style", "value": f"{style.title()} Style"}],
                    external_url="https://ckempire.com/nft",
                    seller_fee_basis_points=500,
                    collection={"name": "CKEmpire AI Videos", "family": "CKEmpire AI"},
                    ai_generated=True,
                    minting_timestamp=datetime.now(),
                    blockchain_metadata={},
                    rarity_score=0.8,
                    market_analysis={}
                )
                
                pricing_prediction = PricingPrediction(
                    predicted_price=2.0 if style == "zack_snyder" else 1.5,
                    confidence=0.8,
                    factors=["AI enhancement", "Rarity"],
                    market_analysis={},
                    recommendation="List at predicted price",
                    ml_model_version="v2.1",
                    training_data_points=15000,
                    market_volatility=0.25,
                    competitor_analysis={}
                )
                
                stripe_product = asyncio.run(video_manager.create_enhanced_stripe_product(nft_metadata, pricing_prediction))
                
                results[style] = {
                    'success': True,
                    'product_id': stripe_product.get('product_id', ''),
                    'price_usd': stripe_product.get('price_usd', 0),
                    'price_eth': stripe_product.get('price_eth', 0),
                    'ai_enhanced': stripe_product.get('ai_enhanced', False),
                    'ml_model_version': stripe_product.get('ml_model_version', ''),
                    'confidence': stripe_product.get('confidence', 0),
                    'market_volatility': stripe_product.get('market_volatility', 0)
                }
                
                print(f"  ✅ {style}: ${stripe_product.get('price_usd', 0):.2f}, {stripe_product.get('price_eth', 0):.2f} ETH")
                
            except Exception as e:
                results[style] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {style}: Error - {e}")
        
        return results
    
    def test_complete_workflow(self) -> Dict[str, Any]:
        """Test complete AI video/NFT workflow"""
        print("\n🚀 Testing Complete AI Video/NFT Workflow...")
        results = {}
        
        test_cases = [
            {"theme": "Epic battle between light and darkness", "style": "zack_snyder", "duration": 180},
            {"theme": "Futuristic cityscape with flying cars", "style": "sci_fi", "duration": 120},
            {"theme": "Emotional journey through time", "style": "dramatic", "duration": 90},
            {"theme": "High-speed chase through neon streets", "style": "action", "duration": 60}
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                # Complete workflow test
                result = asyncio.run(video_manager.process_enhanced_video_production(
                    theme=test_case["theme"],
                    duration=test_case["duration"],
                    style=test_case["style"]
                ))
                
                results[f"workflow_{i+1}"] = {
                    'success': True,
                    'production_id': result.get('production_id', ''),
                    'video_prompt_length': len(result.get('video_prompt', '')),
                    'ai_enhanced': result.get('video_metadata', {}).get('ai_enhanced', False),
                    'minting_ready': result.get('video_metadata', {}).get('minting_ready', False),
                    'nft_rarity_score': result.get('nft_metadata', {}).get('rarity_score', 0),
                    'predicted_price': result.get('pricing_prediction', {}).get('predicted_price', 0),
                    'ml_model_version': result.get('pricing_prediction', {}).get('ml_model_version', ''),
                    'stripe_product_created': bool(result.get('stripe_product', {}).get('product_id')),
                    'minting_history_count': result.get('minting_history_count', 0)
                }
                
                print(f"  ✅ Workflow {i+1}: {test_case['style']} - Price={result.get('pricing_prediction', {}).get('predicted_price', 0):.2f} ETH, Score={result.get('nft_metadata', {}).get('rarity_score', 0):.2f}")
                
            except Exception as e:
                results[f"workflow_{i+1}"] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ Workflow {i+1}: Error - {e}")
        
        return results
    
    def test_ai_minting_configuration(self) -> Dict[str, Any]:
        """Test AI minting configuration"""
        print("\n⚙️ Testing AI Minting Configuration...")
        
        try:
            config = video_manager.ai_minting_config
            
            results = {
                'success': True,
                'model_version': config.model_version,
                'prompt_optimization': config.prompt_optimization,
                'metadata_enhancement': config.metadata_enhancement,
                'rarity_calculation': config.rarity_calculation,
                'market_analysis': config.market_analysis,
                'blockchain_integration': config.blockchain_integration,
                'minting_history_count': len(video_manager.minting_history),
                'video_styles_count': len(video_manager.video_styles),
                'ai_enhanced_styles': sum(1 for style in video_manager.video_styles.values() 
                                        if "ai_enhanced" in style.effects or "ai_generated" in style.effects)
            }
            
            print(f"  ✅ AI Minting Config: Model={config.model_version}, Styles={len(video_manager.video_styles)}, AI-Enhanced={results['ai_enhanced_styles']}")
            
            return results
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive AI video/NFT minting test"""
        print("🚀 CK Empire AI Video/NFT Minting Test Suite")
        print("=" * 60)
        
        # Run all tests
        self.test_results = {
            'ai_video_prompt_generation': self.test_ai_video_prompt_generation(),
            'enhanced_video_metadata': self.test_enhanced_video_metadata(),
            'nft_metadata_optimization': self.test_nft_metadata_optimization(),
            'enhanced_pricing_prediction': self.test_enhanced_pricing_prediction(),
            'enhanced_stripe_product_creation': self.test_enhanced_stripe_product_creation(),
            'complete_workflow': self.test_complete_workflow(),
            'ai_minting_configuration': self.test_ai_minting_configuration()
        }
        
        # Calculate overall success rate
        total_tests = 0
        successful_tests = 0
        
        print("\n🔍 Calculating test results...")
        for test_category, results in self.test_results.items():
            if isinstance(results, dict):
                for test_name, result in results.items():
                    total_tests += 1
                    if isinstance(result, dict) and result.get('success', False):
                        successful_tests += 1
                    elif isinstance(result, bool) and result:
                        successful_tests += 1
        
        overall_success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # Generate summary
        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_tests': total_tests,
            'successful_tests': successful_tests,
            'overall_success_rate': overall_success_rate,
            'test_results': self.test_results,
            'ai_minting_enabled': True,
            'ml_model_version': video_manager.ai_minting_config.model_version,
            'video_styles_count': len(video_manager.video_styles),
            'minting_history_count': len(video_manager.minting_history)
        }
        
        return summary
    
    def save_test_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"video_nft_test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n💾 Test results saved to: {filename}")
        except Exception as e:
            print(f"\n❌ Failed to save results: {e}")

def main():
    """Main test function"""
    tester = VideoNFTMintingTester()
    
    try:
        # Run comprehensive test
        results = tester.run_comprehensive_test()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"Successful Tests: {results['successful_tests']}")
        print(f"Success Rate: {results['overall_success_rate']:.1%}")
        print(f"AI Minting Enabled: {results['ai_minting_enabled']}")
        print(f"ML Model Version: {results['ml_model_version']}")
        print(f"Video Styles: {results['video_styles_count']}")
        print(f"Minting History: {results['minting_history_count']}")
        
        # Save results
        tester.save_test_results(results)
        
        # Exit with appropriate code
        if results['overall_success_rate'] >= 0.8:
            print("\n🎉 AI Video/NFT minting test suite passed successfully!")
            return 0
        else:
            print("\n⚠️  Some AI video/NFT minting tests failed. Please review the results.")
            return 1
            
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 