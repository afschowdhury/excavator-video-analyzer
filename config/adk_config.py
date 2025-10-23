"""
ADK Configuration for agent orchestration
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str = "gemini-2.0-flash-exp"
    temperature: float = 0.2
    top_p: float = 0.95
    max_tokens: int = 8000
    timeout: int = 300  # seconds


@dataclass
class AgentConfig:
    """Configuration for an individual agent"""
    enabled: bool = True
    model: ModelConfig = field(default_factory=ModelConfig)
    retry_attempts: int = 3
    retry_delay: int = 5  # seconds
    custom_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ADKConfig:
    """Main configuration for ADK multi-agent system"""
    
    # Default model settings
    default_model: str = "gemini-2.0-flash-exp"
    fallback_model: str = "gemini-1.5-flash"
    
    # Agent-specific configurations
    cycle_detector: AgentConfig = field(default_factory=lambda: AgentConfig(
        model=ModelConfig(
            name="gemini-2.0-flash-exp",
            temperature=0.1,
            top_p=0.9,
            max_tokens=8000
        )
    ))
    
    technique_evaluator: AgentConfig = field(default_factory=lambda: AgentConfig(
        model=ModelConfig(
            name="gemini-2.0-flash-exp",
            temperature=0.3,
            top_p=0.95,
            max_tokens=4000
        )
    ))
    
    orchestrator: AgentConfig = field(default_factory=lambda: AgentConfig(
        model=ModelConfig(
            name="gemini-2.0-flash-exp",
            temperature=0.2,
            top_p=0.95,
            max_tokens=1000
        )
    ))
    
    # Orchestration settings
    parallel_execution: bool = False  # Run agents sequentially by default
    timeout: int = 600  # Overall timeout in seconds
    
    # Performance settings
    cache_results: bool = True
    cache_ttl: int = 3600  # Cache time-to-live in seconds
    
    # Output settings
    save_intermediate_results: bool = True
    output_format: str = "markdown"  # markdown, json, or both
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ADKConfig':
        """
        Create ADKConfig from dictionary

        Args:
            config_dict (Dict[str, Any]): Configuration dictionary

        Returns:
            ADKConfig: Configuration instance
        """
        # Basic implementation - can be enhanced with validation
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary

        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            'default_model': self.default_model,
            'fallback_model': self.fallback_model,
            'parallel_execution': self.parallel_execution,
            'timeout': self.timeout,
            'cache_results': self.cache_results,
            'cache_ttl': self.cache_ttl,
            'save_intermediate_results': self.save_intermediate_results,
            'output_format': self.output_format,
        }
    
    def get_agent_model(self, agent_name: str) -> str:
        """
        Get model name for specific agent

        Args:
            agent_name (str): Name of the agent

        Returns:
            str: Model name
        """
        agent_configs = {
            'cycle_detector': self.cycle_detector,
            'technique_evaluator': self.technique_evaluator,
            'orchestrator': self.orchestrator,
        }
        
        agent_config = agent_configs.get(agent_name)
        if agent_config:
            return agent_config.model.name
        
        return self.default_model


# Default configuration instance
DEFAULT_CONFIG = ADKConfig()

