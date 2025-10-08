"""
Configuration settings for SEAgent
Enhanced with secure environment variable loading
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


def load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent.parent / '.env'
    if env_file.exists():
        print(f"Loading environment variables from {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value
    else:
        print("No .env file found, using environment variables only")

# Load .env file on import
load_env_file()


@dataclass
class AgentConfig:
    """Configuration for individual agents"""
    enabled: bool = True
    max_concurrent_tasks: int = 5
    timeout: int = 300  # seconds
    retry_attempts: int = 3
    log_level: str = "INFO"
    specific_config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class APIConfig:
    """API server configuration"""
    host: str = field(default_factory=lambda: os.getenv("API_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("API_PORT", "8000")))
    cors_origins: list = field(default_factory=lambda: ["*"])


@dataclass
class DeepSeekConfig:
    """DeepSeek-Coder V2 API configuration - secured with environment variables"""
    api_key: str = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    model: str = field(default_factory=lambda: os.getenv("DEEPSEEK_MODEL", "deepseek-coder"))
    base_url: str = field(default_factory=lambda: os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"))
    max_tokens: int = field(default_factory=lambda: int(os.getenv("DEEPSEEK_MAX_TOKENS", "4000")))
    temperature: float = field(default_factory=lambda: float(os.getenv("DEEPSEEK_TEMPERATURE", "0.7")))
    
    def is_configured(self) -> bool:
        """Check if DeepSeek is properly configured"""
        return bool(self.api_key and len(self.api_key) > 10)


@dataclass
class UIConfig:
    """UI dashboard configuration"""
    host: str = field(default_factory=lambda: os.getenv("UI_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("UI_PORT", "8001")))
    title: str = field(default_factory=lambda: os.getenv("UI_TITLE", "SEAgent Dashboard"))


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///seagent.db"))
    echo: bool = field(default_factory=lambda: os.getenv("DATABASE_ECHO", "false").lower() == "true")


@dataclass  
class RedisConfig:
    """Redis configuration"""
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    password: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_PASSWORD", None))


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
    token_expiry: int = field(default_factory=lambda: int(os.getenv("TOKEN_EXPIRY", "3600")))
    
    def __post_init__(self):
        """Validate security configuration"""
        if self.secret_key == "dev-secret-key-change-in-production":
            print("⚠️  WARNING: Using default secret key. Set SECRET_KEY environment variable for production!")


@dataclass
class AgentsConfig:
    """All agents configuration"""
    code_generation: AgentConfig = field(default_factory=AgentConfig)
    security_analysis: AgentConfig = field(default_factory=AgentConfig)
    debug: AgentConfig = field(default_factory=AgentConfig)
    performance: AgentConfig = field(default_factory=AgentConfig)
    integration: AgentConfig = field(default_factory=AgentConfig)
    testing: AgentConfig = field(default_factory=AgentConfig)


class Settings:
    """Main application settings"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config_path = config_path
        
        # Set default values
        self.api = APIConfig()
        self.deepseek = DeepSeekConfig()
        self.ui = UIConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.logging = LoggingConfig()
        self.security = SecurityConfig()
        self.agents = AgentsConfig()
        
        # Load configuration if file exists
        self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            config_file = Path(self.config_path)
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f) or {}
                
                # Load environment variables first
                if 'environment_variables' in config_data:
                    env_vars = config_data['environment_variables']
                    for key, value in env_vars.items():
                        if isinstance(value, str) and not value.startswith('your-') and value != 'sk-proj-...':
                            os.environ[key] = value
                
                # Load DeepSeek configuration
                if 'openai' in config_data:
                    openai_data = config_data['openai']
                    self.openai.api_key = openai_data.get('api_key', os.getenv('OPENAI_API_KEY', ''))
                    self.openai.model = openai_data.get('model', self.openai.model)
                    self.openai.max_tokens = openai_data.get('max_tokens', self.openai.max_tokens)
                    self.openai.temperature = openai_data.get('temperature', self.openai.temperature)
                else:
                    # Load from environment if not in config
                    self.openai.api_key = os.getenv('OPENAI_API_KEY', '')
                
                # Update configurations with loaded data
                if 'api' in config_data:
                    api_data = config_data['api']
                    self.api.host = api_data.get('host', self.api.host)
                    self.api.port = api_data.get('port', self.api.port)
                    self.api.cors_origins = api_data.get('cors_origins', self.api.cors_origins)
                
                if 'ui' in config_data:
                    ui_data = config_data['ui']
                    self.ui.host = ui_data.get('host', self.ui.host)
                    self.ui.port = ui_data.get('port', self.ui.port)
                    self.ui.title = ui_data.get('title', self.ui.title)
                
                if 'database' in config_data:
                    db_data = config_data['database']
                    self.database.url = db_data.get('url', self.database.url)
                    self.database.echo = db_data.get('echo', self.database.echo)
                
                if 'agents' in config_data:
                    agents_data = config_data['agents']
                    
                    # Update each agent config
                    for agent_name in ['code_generation', 'security_analysis', 'debug', 
                                     'performance', 'integration', 'testing']:
                        if agent_name in agents_data:
                            agent_data = agents_data[agent_name]
                            agent_config = getattr(self.agents, agent_name)
                            
                            agent_config.enabled = agent_data.get('enabled', agent_config.enabled)
                            agent_config.timeout = agent_data.get('timeout', agent_config.timeout)
                            agent_config.specific_config = agent_data.get('specific_config', {})
                
        except Exception as e:
            print(f"Warning: Failed to load config from {config_file}: {e}")
            print("Using default configuration")


def get_settings(config_path: str = "config/config.yaml") -> Settings:
    """Get application settings"""
    return Settings(config_path)
