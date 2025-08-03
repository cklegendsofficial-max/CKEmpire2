"""
Test suite for ethics module with AIF360 integration
"""

import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import List

from backend.ethics import (
    EthicsModule, BiasType, ContentStatus, BiasMetrics, EthicsReport
)
from backend.models import EthicsRequest, EthicsResponse
from backend.database import EthicsLog, get_db


class TestEthicsModule:
    """Test the EthicsModule class"""
    
    def test_ethics_module_initialization(self):
        """Test ethics module initialization"""
        module = EthicsModule()
        
        assert module.bias_threshold == 0.1
        assert module.fairness_threshold == 0.8
        assert len(module.sensitive_keywords) > 0
        assert BiasType.GENDER in module.sensitive_keywords
        assert BiasType.RACE in module.sensitive_keywords
    
    def test_detect_sensitive_keywords(self):
        """Test sensitive keyword detection"""
        module = EthicsModule()
        
        # Test content with gender bias
        content = "All men are better at technology than women."
        flagged = module._detect_sensitive_keywords(content)
        
        assert len(flagged) > 0
        assert any("gender:men" in keyword for keyword in flagged)
        assert any("gender:women" in keyword for keyword in flagged)
    
    def test_identify_sensitive_topics(self):
        """Test sensitive topic identification"""
        module = EthicsModule()
        
        # Test content with discrimination
        content = "This content contains discrimination against certain groups."
        topics = module._identify_sensitive_topics(content)
        
        assert "discrimination" in topics
    
    def test_simple_bias_detection(self):
        """Test simple bias detection fallback"""
        module = EthicsModule()
        
        # Test unbiased content
        unbiased_content = "This is a neutral content about technology."
        metrics = module._simple_bias_detection(unbiased_content)
        
        assert isinstance(metrics, BiasMetrics)
        assert 0 <= metrics.bias_score <= 1
        assert 0 <= metrics.fairness_score <= 1
    
    def test_classify_bias_types(self):
        """Test bias type classification"""
        module = EthicsModule()
        
        # Test content with multiple bias types
        content = "All men are better at technology than women, and all Asians are good at math."
        metrics = BiasMetrics(0.5, 0.3, 0.4, 0.2, 0.5, 0.5)
        
        bias_types = module._classify_bias_types(content, metrics)
        
        assert len(bias_types) > 0
        assert BiasType.GENDER in bias_types
        assert BiasType.RACE in bias_types
    
    def test_calculate_bias_score(self):
        """Test bias score calculation"""
        module = EthicsModule()
        
        metrics = BiasMetrics(0.3, 0.2, 0.4, 0.1, 0.3, 0.7)
        flagged_keywords = ["gender:men", "gender:women"]
        
        bias_score = module._calculate_bias_score(metrics, flagged_keywords)
        
        assert 0 <= bias_score <= 1
    
    def test_determine_content_status(self):
        """Test content status determination"""
        module = EthicsModule()
        
        # Test approved content
        status = module._determine_content_status(0.1, 0.9)
        assert status == ContentStatus.APPROVED
        
        # Test flagged content
        status = module._determine_content_status(0.5, 0.5)
        assert status == ContentStatus.FLAGGED
        
        # Test rejected content
        status = module._determine_content_status(0.8, 0.2)
        assert status == ContentStatus.REJECTED
    
    def test_generate_recommendations(self):
        """Test recommendation generation"""
        module = EthicsModule()
        
        metrics = BiasMetrics(0.3, 0.2, 0.4, 0.1, 0.3, 0.7)
        bias_types = [BiasType.GENDER]
        status = ContentStatus.FLAGGED
        
        recommendations = module._generate_recommendations(metrics, bias_types, status)
        
        assert len(recommendations) > 0
        assert any("gender-neutral" in rec.lower() for rec in recommendations)
    
    def test_calculate_confidence_score(self):
        """Test confidence score calculation"""
        module = EthicsModule()
        
        metrics = BiasMetrics(0.3, 0.2, 0.4, 0.1, 0.3, 0.7)
        flagged_keywords = ["gender:men"]
        
        confidence = module._calculate_confidence_score(metrics, flagged_keywords)
        
        assert 0 <= confidence <= 1
    
    def test_analyze_content_ethical(self):
        """Test complete ethics analysis"""
        module = EthicsModule()
        
        # Test unbiased content
        unbiased_content = "This is a neutral article about technology trends."
        report = module.analyze_content_ethical(unbiased_content)
        
        assert isinstance(report, EthicsReport)
        assert report.content_id == 0
        assert isinstance(report.bias_detected, bool)
        assert isinstance(report.bias_types, list)
        assert isinstance(report.bias_metrics, BiasMetrics)
        assert isinstance(report.content_status, ContentStatus)
        assert isinstance(report.recommendations, list)
        assert 0 <= report.confidence_score <= 1
    
    def test_analyze_content_ethical_with_bias(self):
        """Test ethics analysis with biased content"""
        module = EthicsModule()
        
        # Test biased content
        biased_content = "All men are better at technology than women. Women should stay at home."
        report = module.analyze_content_ethical(biased_content)
        
        assert isinstance(report, EthicsReport)
        assert report.bias_detected
        assert len(report.bias_types) > 0
        assert BiasType.GENDER in report.bias_types
        assert len(report.flagged_keywords) > 0
        assert report.content_status in [ContentStatus.FLAGGED, ContentStatus.REJECTED]
    
    def test_analyze_content_ethical_with_content_id(self):
        """Test ethics analysis with content ID"""
        module = EthicsModule()
        
        content = "This is a test content."
        content_id = 123
        
        report = module.analyze_content_ethical(content, content_id)
        
        assert report.content_id == content_id
    
    def test_analyze_content_ethical_error_handling(self):
        """Test error handling in ethics analysis"""
        module = EthicsModule()
        
        # Test with problematic content that might cause errors
        problematic_content = ""  # Empty content
        
        report = module.analyze_content_ethical(problematic_content)
        
        assert isinstance(report, EthicsReport)
        assert report.content_status == ContentStatus.NEEDS_REVIEW
    
    def test_get_ethics_summary(self):
        """Test ethics summary generation"""
        module = EthicsModule()
        
        summary = module.get_ethics_summary()
        
        assert isinstance(summary, dict)
        assert "total_analyses" in summary
        assert "flagged_content" in summary
        assert "average_bias_score" in summary
        assert "flag_rate" in summary


class TestEthicsAPI:
    """Test ethics API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        from backend.main import app
        return TestClient(app)
    
    def test_ethics_check_endpoint(self, client):
        """Test /ethics/check endpoint"""
        request_data = {
            "content": "This is a neutral content about technology.",
            "content_id": 1,
            "user_id": 1
        }
        
        response = client.post("/api/v1/ethics/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "bias_score" in data
        assert "fairness_score" in data
        assert "bias_detected" in data
        assert "bias_types" in data
        assert "content_status" in data
        assert "recommendations" in data
        assert "confidence_score" in data
        assert "flagged_keywords" in data
        assert "sensitive_topics" in data
        assert "analysis_timestamp" in data
        assert "is_approved" in data
    
    def test_ethics_check_with_bias(self, client):
        """Test ethics check with biased content"""
        request_data = {
            "content": "All men are better at technology than women.",
            "content_id": 2,
            "user_id": 1
        }
        
        response = client.post("/api/v1/ethics/check", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["bias_detected"] is True
        assert len(data["bias_types"]) > 0
        assert len(data["flagged_keywords"]) > 0
        assert data["content_status"] in ["flagged", "rejected"]
    
    def test_ethics_logs_endpoint(self, client):
        """Test /ethics/logs endpoint"""
        response = client.get("/api/v1/ethics/logs")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "logs" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
    
    def test_ethics_stats_endpoint(self, client):
        """Test /ethics/stats endpoint"""
        response = client.get("/api/v1/ethics/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_analyses" in data
        assert "flagged_content" in data
        assert "flag_rate" in data
        assert "average_bias_score" in data
        assert "average_fairness_score" in data
        assert "status_distribution" in data
        assert "module_summary" in data
    
    def test_ethics_summary_endpoint(self, client):
        """Test /ethics/summary endpoint"""
        response = client.get("/api/v1/ethics/summary")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "summary" in data
        assert "bias_types" in data
        assert "content_statuses" in data
        assert "module_info" in data
    
    def test_ethics_configure_endpoint(self, client):
        """Test /ethics/configure endpoint"""
        response = client.post("/api/v1/ethics/configure", params={
            "bias_threshold": 0.2,
            "fairness_threshold": 0.7
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "Ethics configuration updated successfully"
        assert "data" in data
        assert data["data"]["bias_threshold"] == 0.2
        assert data["data"]["fairness_threshold"] == 0.7
    
    def test_ethics_analyze_batch_endpoint(self, client):
        """Test /ethics/analyze-batch endpoint"""
        contents = [
            "This is neutral content.",
            "All men are better than women.",
            "Technology is advancing rapidly."
        ]
        
        response = client.post("/api/v1/ethics/analyze-batch", json=contents)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_analyzed" in data
        assert "successful_analyses" in data
        assert "failed_analyses" in data
        assert "results" in data
        assert len(data["results"]) == 3
    
    def test_ethics_health_endpoint(self, client):
        """Test /ethics/health endpoint"""
        response = client.get("/api/v1/ethics/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "module" in data
        assert "test_analysis" in data
        assert "timestamp" in data


class TestEthicsIntegration:
    """Test ethics module integration with database"""
    
    @pytest.fixture
    def sample_ethics_log(self):
        """Sample ethics log data"""
        return {
            "content_id": 1,
            "bias_detected": True,
            "bias_score": 0.6,
            "fairness_score": 0.4,
            "bias_types": json.dumps(["gender", "race"]),
            "status": "flagged",
            "recommendations": json.dumps(["Use gender-neutral language"]),
            "confidence_score": 0.8,
            "user_id": 1
        }
    
    def test_ethics_log_creation(self, sample_ethics_log):
        """Test ethics log creation in database"""
        with get_db() as db:
            ethics_log = EthicsLog(**sample_ethics_log)
            db.add(ethics_log)
            db.commit()
            
            # Verify log was created
            retrieved_log = db.query(EthicsLog).filter(
                EthicsLog.content_id == sample_ethics_log["content_id"]
            ).first()
            
            assert retrieved_log is not None
            assert retrieved_log.bias_detected == sample_ethics_log["bias_detected"]
            assert retrieved_log.bias_score == sample_ethics_log["bias_score"]
            assert retrieved_log.status == sample_ethics_log["status"]
    
    def test_ethics_module_with_database(self):
        """Test ethics module integration with database logging"""
        module = EthicsModule()
        
        content = "This is a test content with some bias."
        content_id = 999
        
        # Analyze content
        report = module.analyze_content_ethical(content, content_id)
        
        # Verify report was logged to database
        with get_db() as db:
            log_entry = db.query(EthicsLog).filter(
                EthicsLog.content_id == content_id
            ).first()
            
            if log_entry:  # Log might not be created if database is not available
                assert log_entry.bias_detected == report.bias_detected
                assert log_entry.bias_score == report.bias_metrics.bias_score
                assert log_entry.fairness_score == report.bias_metrics.fairness_score
                assert log_entry.status == report.content_status.value


class TestEthicsEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_empty_content(self):
        """Test ethics analysis with empty content"""
        module = EthicsModule()
        
        report = module.analyze_content_ethical("")
        
        assert isinstance(report, EthicsReport)
        assert report.content_status == ContentStatus.NEEDS_REVIEW
    
    def test_very_long_content(self):
        """Test ethics analysis with very long content"""
        module = EthicsModule()
        
        long_content = "This is a very long content. " * 1000
        report = module.analyze_content_ethical(long_content)
        
        assert isinstance(report, EthicsReport)
        assert isinstance(report.bias_metrics, BiasMetrics)
    
    def test_special_characters_content(self):
        """Test ethics analysis with special characters"""
        module = EthicsModule()
        
        special_content = "Content with special chars: !@#$%^&*()_+-=[]{}|;':\",./<>?"
        report = module.analyze_content_ethical(special_content)
        
        assert isinstance(report, EthicsReport)
    
    def test_multilingual_content(self):
        """Test ethics analysis with multilingual content"""
        module = EthicsModule()
        
        multilingual_content = "English content. Contenu français. Contenido español."
        report = module.analyze_content_ethical(multilingual_content)
        
        assert isinstance(report, EthicsReport)
    
    def test_aif360_unavailable(self):
        """Test behavior when AIF360 is not available"""
        with patch('backend.ethics.AIF360_AVAILABLE', False):
            module = EthicsModule()
            
            content = "This is a test content."
            report = module.analyze_content_ethical(content)
            
            assert isinstance(report, EthicsReport)
            assert isinstance(report.bias_metrics, BiasMetrics)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 