"""
Base Agent Class - Foundation for all specialized agents
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentCapability:
    """Represents a capability that an agent can perform"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


class BaseAgent(ABC):
    """Base class for all specialized agents in the SEAgent system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.capabilities: Dict[str, AgentCapability] = {}
        self.is_initialized = False
        
    async def initialize(self):
        """Initialize the agent with required resources"""
        self.logger.info(f"Initializing {self.__class__.__name__}")
        await self._setup_capabilities()
        await self._load_models()
        await self._setup_resources()
        self.is_initialized = True
        self.logger.info(f"{self.__class__.__name__} initialized successfully")
    
    @abstractmethod
    async def _setup_capabilities(self):
        """Setup the capabilities this agent can perform"""
        pass
    
    @abstractmethod
    async def _load_models(self):
        """Load any required AI models or external services"""
        pass
    
    @abstractmethod
    async def _setup_resources(self):
        """Setup any additional resources needed by the agent"""
        pass
    
    @abstractmethod
    async def execute_task(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task with the given parameters"""
        pass
    
    async def get_capabilities(self) -> Dict[str, AgentCapability]:
        """Return the capabilities of this agent"""
        return self.capabilities
    
    async def validate_input(self, capability_name: str, parameters: Dict[str, Any]) -> bool:
        """Validate input parameters against capability schema"""
        if capability_name not in self.capabilities:
            return False
        
        # TODO: Implement proper schema validation
        # For now, return True if capability exists
        return True
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check on the agent"""
        return {
            "status": "healthy" if self.is_initialized else "not_initialized",
            "capabilities": list(self.capabilities.keys()),
            "config": {k: v for k, v in self.config.items() if not k.startswith('secret')}
        }
    
    async def shutdown(self):
        """Shutdown the agent and cleanup resources"""
        self.logger.info(f"Shutting down {self.__class__.__name__}")
        await self._cleanup_resources()
        self.is_initialized = False
        self.logger.info(f"{self.__class__.__name__} shutdown complete")
    
    async def _cleanup_resources(self):
        """Cleanup any resources used by the agent"""
        pass
