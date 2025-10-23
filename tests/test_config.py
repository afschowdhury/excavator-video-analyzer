"""
Tests for ADK Configuration
"""

import pytest
from config.adk_config import ADKConfig, ModelConfig, AgentConfig


class TestADKConfig:
    """Test suite for ADK configuration"""

    def test_default_config(self):
        """Test default configuration creation"""
        config = ADKConfig()
        
        assert config.default_model == "gemini-2.0-flash-exp"
        assert config.fallback_model == "gemini-1.5-flash"
        assert config.parallel_execution is False
        assert config.timeout == 600

    def test_cycle_detector_config(self):
        """Test cycle detector configuration"""
        config = ADKConfig()
        
        assert config.cycle_detector.enabled is True
        assert config.cycle_detector.model.temperature == 0.1
        assert config.cycle_detector.model.top_p == 0.9
        assert config.cycle_detector.model.max_tokens == 8000

    def test_technique_evaluator_config(self):
        """Test technique evaluator configuration"""
        config = ADKConfig()
        
        assert config.technique_evaluator.enabled is True
        assert config.technique_evaluator.model.temperature == 0.3
        assert config.technique_evaluator.model.top_p == 0.95
        assert config.technique_evaluator.model.max_tokens == 4000

    def test_get_agent_model(self):
        """Test getting agent model names"""
        config = ADKConfig()
        
        cycle_model = config.get_agent_model('cycle_detector')
        assert cycle_model == "gemini-2.0-flash-exp"
        
        technique_model = config.get_agent_model('technique_evaluator')
        assert technique_model == "gemini-2.0-flash-exp"
        
        unknown_model = config.get_agent_model('unknown_agent')
        assert unknown_model == config.default_model

    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = ADKConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'default_model' in config_dict
        assert 'timeout' in config_dict
        assert config_dict['default_model'] == "gemini-2.0-flash-exp"

    def test_custom_config(self):
        """Test creating custom configuration"""
        config = ADKConfig(
            default_model="gemini-1.5-pro",
            timeout=1200,
            parallel_execution=True
        )
        
        assert config.default_model == "gemini-1.5-pro"
        assert config.timeout == 1200
        assert config.parallel_execution is True

    def test_model_config(self):
        """Test ModelConfig dataclass"""
        model = ModelConfig(
            name="gemini-2.0-pro",
            temperature=0.5,
            top_p=0.8,
            max_tokens=5000,
            timeout=200
        )
        
        assert model.name == "gemini-2.0-pro"
        assert model.temperature == 0.5
        assert model.top_p == 0.8
        assert model.max_tokens == 5000
        assert model.timeout == 200

    def test_agent_config(self):
        """Test AgentConfig dataclass"""
        agent = AgentConfig(
            enabled=True,
            retry_attempts=5,
            retry_delay=10
        )
        
        assert agent.enabled is True
        assert agent.retry_attempts == 5
        assert agent.retry_delay == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

