"""
Test AI Empire Strategy Generation
Tests for fine-tuning, empire strategy generation, and financial calculations
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import Dict, Any

from ai import AIModule, EmpireStrategy, StrategyType, FinancialMetrics
from models import EmpireStrategyRequest, EmpireStrategyResponse, FinancialMetricsResponse

class TestAIEmpireStrategy:
    """Test class for AI empire strategy generation"""
    
    @pytest.fixture
    def ai_module(self):
        """Create AI module instance for testing"""
        return AIModule()
    
    @pytest.fixture
    def sample_strategy_request(self):
        """Sample empire strategy request"""
        return EmpireStrategyRequest(
            user_input="Revenue hedefi $20K, AI öneri ver",
            include_financial_metrics=True
        )
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI response"""
        return """
        Strateji Türü: Scale-Up
        Başlık: $20K Revenue Hedefi Stratejisi
        Açıklama: Hızlı büyüme odaklı strateji ile $20K gelir hedefine ulaşma
        Ana Aksiyonlar:
        - 1. Pazarlama bütçesini artır
        - 2. Satış ekibi kur
        - 3. Yeni pazarlara açıl
        - 4. Ürün gamını genişlet
        Süre: 12
        Tahmini Yatırım: 50000
        Projeksiyon ROI: 25%
        Risk Seviyesi: Orta
        Başarı Metrikleri:
        - 1. Aylık gelir artışı
        - 2. Müşteri sayısı
        - 3. Pazar payı
        """

    def test_strategy_type_determination(self, ai_module):
        """Test strategy type determination based on input"""
        # Test lean startup
        strategy_type = ai_module._determine_strategy_type("Düşük bütçe ile başla", "Düşük bütçe")
        assert strategy_type == StrategyType.LEAN_STARTUP
        
        # Test scale up
        strategy_type = ai_module._determine_strategy_type("Hızlı büyüme istiyorum", "Hızlı büyüme")
        assert strategy_type == StrategyType.SCALE_UP
        
        # Test innovation
        strategy_type = ai_module._determine_strategy_type("Teknoloji odaklı", "Teknoloji")
        assert strategy_type == StrategyType.INNOVATION
        
        # Test default
        strategy_type = ai_module._determine_strategy_type("Random input", "Random")
        assert strategy_type == StrategyType.COST_OPTIMIZATION

    def test_field_extraction(self, ai_module):
        """Test field extraction from response text"""
        response_text = """
        Başlık: Test Strategy
        Açıklama: Test description
        Ana Aksiyonlar:
        - 1. Action 1
        - 2. Action 2
        Süre: 6
        Tahmini Yatırım: 100000
        Projeksiyon ROI: 15%
        """
        
        # Test title extraction
        title = ai_module._extract_field(response_text, "Başlık", "Default")
        assert title == "Test Strategy"
        
        # Test description extraction
        description = ai_module._extract_field(response_text, "Açıklama", "Default")
        assert description == "Test description"
        
        # Test number extraction
        timeline = ai_module._extract_number_field(response_text, "Süre", 12)
        assert timeline == 6
        
        # Test investment extraction
        investment = ai_module._extract_number_field(response_text, "Tahmini Yatırım", 50000)
        assert investment == 100000
        
        # Test percentage extraction
        roi = ai_module._extract_percentage_field(response_text, "Projeksiyon ROI", 0.10)
        assert roi == 0.15

    def test_list_field_extraction(self, ai_module):
        """Test list field extraction"""
        response_text = """
        Ana Aksiyonlar:
        - 1. Action 1
        - 2. Action 2
        - 3. Action 3
        Başarı Metrikleri:
        - 1. Metric 1
        - 2. Metric 2
        """
        
        actions = ai_module._extract_list_field(response_text, "Ana Aksiyonlar")
        assert len(actions) == 3
        assert "Action 1" in actions[0]
        assert "Action 2" in actions[1]
        assert "Action 3" in actions[2]
        
        metrics = ai_module._extract_list_field(response_text, "Başarı Metrikleri")
        assert len(metrics) == 2
        assert "Metric 1" in metrics[0]
        assert "Metric 2" in metrics[1]

    def test_financial_metrics_calculation(self, ai_module):
        """Test financial metrics calculation using DCF"""
        strategy = EmpireStrategy(
            strategy_type=StrategyType.SCALE_UP,
            title="Test Strategy",
            description="Test description",
            key_actions=["Action 1", "Action 2"],
            timeline_months=12,
            estimated_investment=50000,
            projected_roi=0.25,
            risk_level="Medium",
            success_metrics=["Metric 1", "Metric 2"]
        )
        
        metrics = ai_module._calculate_financial_metrics(strategy)
        
        # Test that metrics are calculated
        assert isinstance(metrics, FinancialMetrics)
        assert metrics.npv is not None
        assert metrics.irr is not None
        assert metrics.payback_period is not None
        assert metrics.roi_percentage is not None
        assert metrics.total_investment == 50000
        assert metrics.break_even_month > 0

    @pytest.mark.asyncio
    async def test_empire_strategy_generation(self, ai_module, sample_strategy_request, mock_openai_response):
        """Test empire strategy generation"""
        with patch.object(ai_module, '_call_base_model', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = mock_openai_response
            
            strategy = await ai_module.generate_empire_strategy(sample_strategy_request.user_input)
            
            # Test strategy generation
            assert isinstance(strategy, EmpireStrategy)
            assert strategy.title == "$20K Revenue Hedefi Stratejisi"
            assert strategy.strategy_type == StrategyType.SCALE_UP
            assert strategy.timeline_months == 12
            assert strategy.estimated_investment == 50000
            assert strategy.projected_roi == 0.25
            assert len(strategy.key_actions) > 0
            assert len(strategy.success_metrics) > 0

    @pytest.mark.asyncio
    async def test_fine_tuning_dataset_creation(self, ai_module):
        """Test fine-tuning dataset creation"""
        dataset = await ai_module.create_fine_tuning_dataset()
        
        # Test dataset creation
        assert dataset.training_examples > 0
        assert dataset.validation_examples > 0
        assert dataset.model_name == "gpt-4"
        assert dataset.training_status in ["ready", "failed"]
        
        # Test that dataset file exists
        import os
        assert os.path.exists(ai_module.dataset_path)

    def test_fallback_strategy_creation(self, ai_module):
        """Test fallback strategy creation when AI fails"""
        user_input = "Test input"
        strategy = ai_module._create_fallback_strategy(user_input)
        
        assert isinstance(strategy, EmpireStrategy)
        assert strategy.strategy_type == StrategyType.LEAN_STARTUP
        assert "Test input" in strategy.description
        assert strategy.estimated_investment == 50000
        assert strategy.projected_roi == 0.15

    def test_mock_response_creation(self, ai_module):
        """Test mock response creation for testing"""
        user_input = "Test input"
        response = ai_module._create_mock_response(user_input)
        
        assert "Test input" in response
        assert "Strateji Türü" in response
        assert "Başlık" in response
        assert "Açıklama" in response

    @pytest.mark.asyncio
    async def test_fine_tuning_start(self, ai_module):
        """Test fine-tuning start process"""
        with patch.object(ai_module, 'client') as mock_client:
            # Mock file creation
            mock_file = Mock()
            mock_file.id = "file_123"
            mock_client.files.create.return_value = mock_file
            
            # Mock job creation
            mock_job = Mock()
            mock_job.id = "job_456"
            mock_client.fine_tuning.jobs.create.return_value = mock_job
            
            dataset = await ai_module.create_fine_tuning_dataset()
            job_id = await ai_module.start_fine_tuning(dataset)
            
            assert job_id == "job_456"
            mock_client.files.create.assert_called_once()
            mock_client.fine_tuning.jobs.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_fine_tuning_status_check(self, ai_module):
        """Test fine-tuning status check"""
        with patch.object(ai_module, 'client') as mock_client:
            # Mock job retrieval
            mock_job = Mock()
            mock_job.status = "succeeded"
            mock_job.fine_tuned_model = "ft:gpt-4:test:123"
            mock_job.created_at = datetime.utcnow()
            mock_job.finished_at = datetime.utcnow()
            mock_job.trained_tokens = 1000
            mock_client.fine_tuning.jobs.retrieve.return_value = mock_job
            
            status_info = await ai_module.check_fine_tuning_status("job_123")
            
            assert status_info["status"] == "succeeded"
            assert status_info["model"] == "ft:gpt-4:test:123"
            assert status_info["trained_tokens"] == 1000

    def test_strategy_templates_loading(self, ai_module):
        """Test strategy templates loading"""
        templates = ai_module.strategy_templates
        
        assert "lean_startup" in templates
        assert "scale_up" in templates
        assert "diversification" in templates
        
        # Test lean startup template
        lean_template = templates["lean_startup"]
        assert lean_template["title"] == "Lean Startup Strategy"
        assert lean_template["timeline_months"] == 6
        assert lean_template["estimated_investment"] == 50000
        assert lean_template["projected_roi"] == 0.15

    def test_sample_dataset_creation(self, ai_module):
        """Test sample dataset creation"""
        # Remove existing dataset
        import os
        if os.path.exists(ai_module.dataset_path):
            os.remove(ai_module.dataset_path)
        
        # Create new dataset
        ai_module._create_sample_dataset()
        
        # Check that dataset was created
        assert os.path.exists(ai_module.dataset_path)
        
        # Check dataset content
        with open(ai_module.dataset_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            assert len(lines) >= 100  # At least 100 examples
        
        # Check JSON format
        import json
        for line in lines[:5]:  # Check first 5 lines
            data = json.loads(line.strip())
            assert "input" in data
            assert "output" in data

    def test_random_input_generation(self, ai_module):
        """Test random input generation for dataset"""
        inputs = []
        for _ in range(10):
            input_text = ai_module._generate_random_input()
            inputs.append(input_text)
        
        # Check that inputs are generated
        assert len(inputs) == 10
        assert all(len(input_text) > 0 for input_text in inputs)
        
        # Check that inputs are from predefined list
        expected_inputs = [
            "Düşük bütçe ile başla",
            "Revenue hedefi $50K",
            "Yüksek risk toleransı",
            "Hızlı büyüme istiyorum",
            "Maliyet optimizasyonu",
            "Yeni pazarlara açıl",
            "Teknoloji odaklı",
            "Konsolide et",
            "Sürdürülebilir büyüme",
            "Kriz yönetimi"
        ]
        
        for input_text in inputs:
            assert input_text in expected_inputs

    @pytest.mark.asyncio
    async def test_empire_strategy_with_financial_metrics(self, ai_module, sample_strategy_request):
        """Test empire strategy generation with financial metrics"""
        with patch.object(ai_module, '_call_base_model', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = """
            Strateji Türü: Scale-Up
            Başlık: Test Strategy
            Açıklama: Test description
            Ana Aksiyonlar:
            - 1. Action 1
            - 2. Action 2
            Süre: 12
            Tahmini Yatırım: 100000
            Projeksiyon ROI: 20%
            Risk Seviyesi: Orta
            Başarı Metrikleri:
            - 1. Metric 1
            - 2. Metric 2
            """
            
            strategy = await ai_module.generate_empire_strategy(sample_strategy_request.user_input)
            
            # Test strategy
            assert strategy.title == "Test Strategy"
            assert strategy.estimated_investment == 100000
            assert strategy.projected_roi == 0.20
            
            # Test financial metrics calculation
            financial_metrics = ai_module._calculate_financial_metrics(strategy)
            assert financial_metrics.total_investment == 100000
            assert financial_metrics.roi_percentage > 0
            assert financial_metrics.npv is not None
            assert financial_metrics.irr is not None

    def test_error_handling_in_strategy_generation(self, ai_module):
        """Test error handling in strategy generation"""
        # Test with invalid input
        strategy = ai_module._create_fallback_strategy("")
        assert strategy.strategy_type == StrategyType.LEAN_STARTUP
        
        # Test with None input
        strategy = ai_module._create_fallback_strategy(None)
        assert strategy.strategy_type == StrategyType.LEAN_STARTUP

    def test_dataset_directory_creation(self, ai_module):
        """Test dataset directory creation"""
        import os
        import shutil
        
        # Remove data directory if exists
        if os.path.exists("data"):
            shutil.rmtree("data")
        
        # Create directory
        ai_module._ensure_dataset_directory()
        
        # Check directory exists
        assert os.path.exists("data")
        assert os.path.isdir("data")

    @pytest.mark.asyncio
    async def test_fine_tuned_model_integration(self, ai_module):
        """Test fine-tuned model integration"""
        # Set fine-tuned model
        ai_module.fine_tuned_model = "ft:gpt-4:test:123"
        
        with patch.object(ai_module, '_call_fine_tuned_model', new_callable=AsyncMock) as mock_call:
            mock_call.return_value = "Fine-tuned response"
            
            strategy = await ai_module.generate_empire_strategy("Test input")
            
            # Verify fine-tuned model was called
            mock_call.assert_called_once_with("Test input")

    def test_strategy_parsing_edge_cases(self, ai_module):
        """Test strategy parsing with edge cases"""
        # Test with minimal response
        minimal_response = "Başlık: Test\nAçıklama: Test"
        strategy = ai_module._parse_strategy_response(minimal_response, "Test input")
        
        assert strategy.title == "Test"
        assert strategy.description == "Test"
        assert strategy.strategy_type == StrategyType.COST_OPTIMIZATION  # Default
        
        # Test with empty response
        empty_response = ""
        strategy = ai_module._parse_strategy_response(empty_response, "Test input")
        
        assert strategy.title == "Empire Strategy"  # Default
        assert strategy.description == "Personalized strategy"  # Default

if __name__ == "__main__":
    pytest.main([__file__]) 