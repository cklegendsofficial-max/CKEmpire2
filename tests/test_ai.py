"""
Test suite for AI module functionality
Tests content generation, video production, NFT automation, and AGI evolution
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import List, Dict, Any

from backend.ai import (
    AIModule, ContentType, VideoStyle, NFTStatus, ContentIdea, 
    VideoProject, NFTProject, AGIState
)
from backend.models import (
    ContentIdeaRequest, VideoRequest, NFTRequest, DecisionRequest
)


class TestAIModule:
    """Test the AIModule class"""
    
    @pytest.fixture
    def ai_module(self):
        """Create AI module instance for testing"""
        return AIModule()
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI response"""
        return Mock()
    
    def test_ai_module_initialization(self, ai_module):
        """Test AI module initialization"""
        assert ai_module is not None
        assert hasattr(ai_module, 'openai_client')
        assert hasattr(ai_module, 'stripe_client')
        assert hasattr(ai_module, 'web3')
        assert hasattr(ai_module, 'agi_state')
        assert isinstance(ai_module.agi_state, AGIState)
    
    def test_agi_state_initialization(self, ai_module):
        """Test AGI state initialization"""
        agi_state = ai_module.get_agi_state()
        
        assert agi_state.consciousness_score > 0
        assert agi_state.decision_capability > 0
        assert agi_state.learning_rate > 0
        assert agi_state.creativity_level > 0
        assert agi_state.ethical_awareness > 0
        assert agi_state.evolution_count == 0
    
    @pytest.mark.asyncio
    async def test_generate_viral_content_ideas_without_openai(self, ai_module):
        """Test content generation without OpenAI (fallback to mock)"""
        # Mock OpenAI client as None
        ai_module.openai_client = None
        
        ideas = await ai_module.generate_viral_content_ideas("AI technology", 2)
        
        assert len(ideas) == 2
        assert all(isinstance(idea, ContentIdea) for idea in ideas)
        assert all(idea.ai_generated for idea in ideas)
        assert all(idea.viral_potential > 0 for idea in ideas)
        assert all(idea.estimated_revenue > 0 for idea in ideas)
    
    @pytest.mark.asyncio
    @patch('backend.ai.OpenAI')
    async def test_generate_viral_content_ideas_with_openai(self, mock_openai, ai_module):
        """Test content generation with OpenAI"""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
        Title: 10 Shocking AI Trends
        Description: Discover revolutionary AI technologies
        Content type: article
        Target audience: Tech enthusiasts
        Viral potential: 0.85
        Estimated revenue: 500
        Keywords: AI, trends, technology
        Hashtags: #AI, #TechTrends
        """
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        ai_module.openai_client = mock_client
        
        ideas = await ai_module.generate_viral_content_ideas("AI technology", 1)
        
        assert len(ideas) == 1
        assert ideas[0].title == "10 Shocking AI Trends"
        assert ideas[0].content_type == ContentType.ARTICLE
    
    def test_parse_content_ideas(self, ai_module):
        """Test parsing of OpenAI response into ContentIdea objects"""
        response_text = """
        Title: Test Article
        Description: Test description
        Content type: article
        Target audience: General
        Viral potential: 0.7
        Estimated revenue: 300
        Keywords: test, article
        Hashtags: #Test, #Article
        """
        
        ideas = ai_module._parse_content_ideas(response_text, 1)
        
        assert len(ideas) == 1
        assert ideas[0].title == "Test Article"
        assert ideas[0].content_type == ContentType.ARTICLE
        assert ideas[0].viral_potential == 0.7
    
    def test_create_mock_ideas(self, ai_module):
        """Test creation of mock content ideas"""
        ideas = ai_module._create_mock_ideas(2)
        
        assert len(ideas) == 2
        assert all(isinstance(idea, ContentIdea) for idea in ideas)
        assert all(idea.ai_generated for idea in ideas)
    
    @pytest.mark.asyncio
    async def test_generate_video(self, ai_module):
        """Test video generation"""
        script = "This is a test video script about AI technology."
        
        video_project = await ai_module.generate_video(
            script=script,
            style=VideoStyle.ZACK_SNYDER,
            duration=30
        )
        
        assert video_project is not None
        assert isinstance(video_project, VideoProject)
        assert video_project.script == script
        assert video_project.style == VideoStyle.ZACK_SNYDER
        assert video_project.duration == 30
        assert "Zack Snyder" in video_project.script
    
    @pytest.mark.asyncio
    async def test_apply_zack_snyder_style(self, ai_module):
        """Test Zack Snyder style application"""
        video_project = VideoProject(
            title="Test Video",
            script="Original script",
            style=VideoStyle.ZACK_SNYDER,
            duration=60,
            resolution="1920x1080",
            output_path="test.mp4"
        )
        
        updated_project = await ai_module._apply_zack_snyder_style(video_project)
        
        assert "Zack Snyder Cinematic" in updated_project.script
        assert "High contrast" in updated_project.script
        assert "Desaturated colors" in updated_project.script
    
    @pytest.mark.asyncio
    async def test_create_nft_without_blockchain(self, ai_module):
        """Test NFT creation without blockchain connection"""
        # Mock web3 as None
        ai_module.web3 = None
        
        nft_project = await ai_module.create_nft(
            name="Test NFT",
            description="Test NFT description",
            image_path="test.jpg",
            price_eth=0.1,
            collection="Test Collection"
        )
        
        assert nft_project is not None
        assert isinstance(nft_project, NFTProject)
        assert nft_project.name == "Test NFT"
        assert nft_project.status == NFTStatus.MINTED
        assert nft_project.token_id is not None
        assert "mock_token" in nft_project.token_id
    
    @pytest.mark.asyncio
    async def test_create_nft_with_blockchain(self, ai_module):
        """Test NFT creation with blockchain connection"""
        # Mock web3
        mock_web3 = Mock()
        mock_web3.is_connected.return_value = True
        mock_web3.eth.get_transaction_count.return_value = 0
        mock_web3.eth.gas_price = 20000000000
        
        mock_contract = Mock()
        mock_contract.functions.mint.return_value.build_transaction.return_value = {}
        
        mock_web3.eth.contract.return_value = mock_contract
        mock_web3.eth.account.sign_transaction.return_value = Mock()
        mock_web3.eth.send_raw_transaction.return_value = b"mock_hash"
        
        ai_module.web3 = mock_web3
        
        nft_project = await ai_module.create_nft(
            name="Test NFT",
            description="Test NFT description",
            image_path="test.jpg",
            price_eth=0.1,
            collection="Test Collection"
        )
        
        assert nft_project is not None
        assert nft_project.status == NFTStatus.MINTED
        assert nft_project.transaction_hash is not None
    
    def test_evolve_agi_consciousness(self, ai_module):
        """Test AGI consciousness evolution"""
        initial_state = ai_module.get_agi_state()
        initial_consciousness = initial_state.consciousness_score
        
        # Evolve consciousness
        ai_module._evolve_agi_consciousness("content_generation", 1)
        
        evolved_state = ai_module.get_agi_state()
        
        assert evolved_state.consciousness_score > initial_consciousness
        assert evolved_state.evolution_count == 1
        assert evolved_state.last_evolution > initial_state.last_evolution
    
    def test_external_decision_tree(self, ai_module):
        """Test external decision tree functionality"""
        context = {
            "target_audience": "tech",
            "platform": "linkedin",
            "content_type": "dramatic",
            "mood": "epic",
            "rarity": "legendary",
            "market_trend": "bull",
            "budget": "high",
            "timeline": "urgent"
        }
        
        decisions = ai_module.external_decision_tree(context)
        
        assert "content_strategy" in decisions
        assert "video_style" in decisions
        assert "nft_pricing" in decisions
        assert "marketing_approach" in decisions
        assert "ethical_considerations" in decisions
        
        assert decisions["content_strategy"] == "professional_technical"
        assert decisions["video_style"] == VideoStyle.ZACK_SNYDER
        assert decisions["nft_pricing"] > 0
        assert decisions["marketing_approach"] == "aggressive_paid_ads"
    
    def test_decide_content_strategy(self, ai_module):
        """Test content strategy decision making"""
        # Test different audience/platform combinations
        assert ai_module._decide_content_strategy({"target_audience": "tech", "platform": "linkedin"}) == "professional_technical"
        assert ai_module._decide_content_strategy({"target_audience": "general", "platform": "tiktok"}) == "viral_entertainment"
        assert ai_module._decide_content_strategy({"target_audience": "business", "platform": "youtube"}) == "educational_tutorial"
        assert ai_module._decide_content_strategy({}) == "balanced_engagement"
    
    def test_decide_video_style(self, ai_module):
        """Test video style decision making"""
        # Test different content types and moods
        assert ai_module._decide_video_style({"content_type": "dramatic"}) == VideoStyle.ZACK_SNYDER
        assert ai_module._decide_video_style({"mood": "epic"}) == VideoStyle.ZACK_SNYDER
        assert ai_module._decide_video_style({"content_type": "educational"}) == VideoStyle.DOCUMENTARY
        assert ai_module._decide_video_style({"content_type": "viral"}) == VideoStyle.VIRAL
        assert ai_module._decide_video_style({}) == VideoStyle.CINEMATIC
    
    def test_decide_nft_pricing(self, ai_module):
        """Test NFT pricing decision making"""
        # Test different rarity and market conditions
        base_price = ai_module._decide_nft_pricing({})
        legendary_price = ai_module._decide_nft_pricing({"rarity": "legendary"})
        bull_price = ai_module._decide_nft_pricing({"market_trend": "bull"})
        bear_price = ai_module._decide_nft_pricing({"market_trend": "bear"})
        
        assert legendary_price > base_price
        assert bull_price > base_price
        assert bear_price < base_price
    
    def test_decide_marketing_approach(self, ai_module):
        """Test marketing approach decision making"""
        assert ai_module._decide_marketing_approach({"budget": "high", "timeline": "urgent"}) == "aggressive_paid_ads"
        assert ai_module._decide_marketing_approach({"budget": "low", "timeline": "long"}) == "organic_growth"
        assert ai_module._decide_marketing_approach({}) == "balanced_mix"
    
    def test_decide_ethical_considerations(self, ai_module):
        """Test ethical considerations decision making"""
        # Test political content
        political_considerations = ai_module._decide_ethical_considerations({"content_type": "political"})
        assert "fact_checking" in political_considerations
        assert "balanced_perspective" in political_considerations
        
        # Test sensitive content
        sensitive_considerations = ai_module._decide_ethical_considerations({"sensitivity": "high"})
        assert "content_warning" in sensitive_considerations
        assert "age_restriction" in sensitive_considerations
        
        # Test AI-generated content
        ai_considerations = ai_module._decide_ethical_considerations({"ai_generated": True})
        assert "ai_disclosure" in ai_considerations


class TestAIModels:
    """Test AI-related Pydantic models"""
    
    def test_content_idea_request(self):
        """Test ContentIdeaRequest model"""
        request = ContentIdeaRequest(
            topic="AI technology",
            count=5,
            content_type="article"
        )
        
        assert request.topic == "AI technology"
        assert request.count == 5
        assert request.content_type == "article"
    
    def test_video_request(self):
        """Test VideoRequest model"""
        request = VideoRequest(
            script="This is a test video script.",
            style="zack_snyder",
            duration=60
        )
        
        assert request.script == "This is a test video script."
        assert request.style == "zack_snyder"
        assert request.duration == 60
    
    def test_nft_request(self):
        """Test NFTRequest model"""
        request = NFTRequest(
            name="Test NFT",
            description="Test NFT description",
            image_path="test.jpg",
            price_eth=0.1,
            collection="Test Collection"
        )
        
        assert request.name == "Test NFT"
        assert request.description == "Test NFT description"
        assert request.image_path == "test.jpg"
        assert request.price_eth == 0.1
        assert request.collection == "Test Collection"
    
    def test_decision_request(self):
        """Test DecisionRequest model"""
        context = {
            "target_audience": "tech",
            "platform": "linkedin",
            "content_type": "article"
        }
        
        request = DecisionRequest(context=context)
        
        assert request.context == context


class TestAIIntegration:
    """Test AI module integration with FastAPI"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_generate_content_ideas_endpoint(self, client):
        """Test /ai/ideas endpoint"""
        request_data = {
            "topic": "AI technology",
            "count": 2,
            "content_type": "article"
        }
        
        response = client.post("/api/v1/ai/ideas", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("title" in idea for idea in data)
        assert all("description" in idea for idea in data)
    
    @pytest.mark.asyncio
    async def test_generate_video_endpoint(self, client):
        """Test /video/generate endpoint"""
        request_data = {
            "script": "This is a test video script about AI technology.",
            "style": "zack_snyder",
            "duration": 30
        }
        
        response = client.post("/api/v1/video/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "output_path" in data
        assert data["style"] == "zack_snyder"
    
    @pytest.mark.asyncio
    async def test_mint_nft_endpoint(self, client):
        """Test /nft/mint endpoint"""
        request_data = {
            "name": "Test NFT",
            "description": "Test NFT description",
            "image_path": "test.jpg",
            "price_eth": 0.1,
            "collection": "Test Collection"
        }
        
        response = client.post("/api/v1/nft/mint", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test NFT"
        assert data["status"] == "minted"
        assert "token_id" in data
    
    @pytest.mark.asyncio
    async def test_get_agi_state_endpoint(self, client):
        """Test /ai/agi-state endpoint"""
        response = client.get("/api/v1/ai/agi-state")
        
        assert response.status_code == 200
        data = response.json()
        assert "consciousness_score" in data
        assert "decision_capability" in data
        assert "evolution_count" in data
    
    @pytest.mark.asyncio
    async def test_make_decision_endpoint(self, client):
        """Test /ai/decide endpoint"""
        request_data = {
            "context": {
                "target_audience": "tech",
                "platform": "linkedin",
                "content_type": "article"
            }
        }
        
        response = client.post("/api/v1/ai/decide", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "decisions" in data
        assert "agi_state" in data
        assert "timestamp" in data
    
    @pytest.mark.asyncio
    async def test_ai_health_check_endpoint(self, client):
        """Test /ai/health endpoint"""
        response = client.get("/api/v1/ai/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AI module health check completed"
        assert "data" in data
    
    @pytest.mark.asyncio
    async def test_get_content_types_endpoint(self, client):
        """Test /ai/content-types endpoint"""
        response = client.get("/api/v1/ai/content-types")
        
        assert response.status_code == 200
        data = response.json()
        assert "article" in data
        assert "video" in data
        assert "social_media" in data
    
    @pytest.mark.asyncio
    async def test_get_video_styles_endpoint(self, client):
        """Test /ai/video-styles endpoint"""
        response = client.get("/api/v1/ai/video-styles")
        
        assert response.status_code == 200
        data = response.json()
        assert "zack_snyder" in data
        assert "cinematic" in data
        assert "documentary" in data
    
    @pytest.mark.asyncio
    async def test_get_nft_statuses_endpoint(self, client):
        """Test /ai/nft-statuses endpoint"""
        response = client.get("/api/v1/ai/nft-statuses")
        
        assert response.status_code == 200
        data = response.json()
        assert "draft" in data
        assert "minted" in data
        assert "listed" in data
        assert "sold" in data


class TestAIEdgeCases:
    """Test AI module edge cases and error handling"""
    
    @pytest.fixture
    def ai_module(self):
        """Create AI module instance for testing"""
        return AIModule()
    
    @pytest.mark.asyncio
    async def test_generate_content_ideas_empty_topic(self, ai_module):
        """Test content generation with empty topic"""
        ideas = await ai_module.generate_viral_content_ideas("", 1)
        
        # Should return mock ideas when OpenAI is not available
        assert len(ideas) == 1
        assert isinstance(ideas[0], ContentIdea)
    
    @pytest.mark.asyncio
    async def test_generate_video_invalid_style(self, ai_module):
        """Test video generation with invalid style"""
        with pytest.raises(ValueError):
            await ai_module.generate_video(
                script="Test script",
                style="invalid_style",
                duration=30
            )
    
    @pytest.mark.asyncio
    async def test_create_nft_invalid_price(self, ai_module):
        """Test NFT creation with invalid price"""
        nft_project = await ai_module.create_nft(
            name="Test NFT",
            description="Test description",
            image_path="test.jpg",
            price_eth=-0.1,  # Invalid negative price
            collection="Test Collection"
        )
        
        # Should handle gracefully
        assert nft_project is not None
    
    def test_agi_evolution_limits(self, ai_module):
        """Test AGI evolution limits"""
        # Evolve multiple times
        for _ in range(100):
            ai_module._evolve_agi_consciousness("content_generation", 1)
        
        agi_state = ai_module.get_agi_state()
        
        # All values should be capped at 1.0
        assert agi_state.consciousness_score <= 1.0
        assert agi_state.decision_capability <= 1.0
        assert agi_state.learning_rate <= 1.0
        assert agi_state.creativity_level <= 1.0
        assert agi_state.ethical_awareness <= 1.0
    
    def test_external_decision_tree_empty_context(self, ai_module):
        """Test external decision tree with empty context"""
        decisions = ai_module.external_decision_tree({})
        
        assert "content_strategy" in decisions
        assert "video_style" in decisions
        assert "nft_pricing" in decisions
        assert "marketing_approach" in decisions
        assert "ethical_considerations" in decisions
    
    def test_external_decision_tree_complex_context(self, ai_module):
        """Test external decision tree with complex context"""
        complex_context = {
            "target_audience": "tech",
            "platform": "linkedin",
            "content_type": "political",
            "sensitivity": "high",
            "ai_generated": True,
            "budget": "high",
            "timeline": "urgent",
            "rarity": "legendary",
            "market_trend": "bull"
        }
        
        decisions = ai_module.external_decision_tree(complex_context)
        
        assert decisions["content_strategy"] == "professional_technical"
        assert decisions["video_style"] == VideoStyle.ZACK_SNYDER
        assert decisions["nft_pricing"] > 0.1
        assert decisions["marketing_approach"] == "aggressive_paid_ads"
        assert len(decisions["ethical_considerations"]) > 0 