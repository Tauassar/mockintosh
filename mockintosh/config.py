#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Pydantic-based configuration module for Mockintosh.
Replaces the legacy class-based configuration system with modern Pydantic models.
"""

from typing import (
    List, Union, Dict, Optional, Any
)
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from mockintosh.constants import PYBARS, JINJA


class ConfigService(BaseModel):
    """Compatibility class for old system."""
    services: List['ConfigService'] = []
    
    def get_name(self) -> str:
        """Get service name."""
        return getattr(self, 'name', '') or ''
    
    def get_hint(self) -> str:
        """Get service hint."""
        return getattr(self, 'name', '') or ''


class ConfigExternalFilePath(BaseModel):
    """Configuration for external file paths."""
    path: str
    _index: Optional[int] = None
    
    # Compatibility with old system
    files: List['ConfigExternalFilePath'] = []

    def destroy(self) -> None:
        """Clean up external file path."""
        pass
    
    def add_external_file_path(self, external_file_path: 'ConfigExternalFilePath') -> None:
        """Add external file path to service (compatibility method)."""
        pass


class ConfigSchema(BaseModel):
    """Configuration for data schemas."""
    payload: Union[Dict[str, Any], ConfigExternalFilePath]


class ConfigDataset(BaseModel):
    """Configuration for datasets."""
    payload: Union[List[Dict[str, Any]], str, ConfigExternalFilePath]

    @field_validator('payload')
    @classmethod
    def validate_payload(cls, v):
        """Validate payload doesn't contain commas in tags."""
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict) and 'tag' in item:
                    if ',' in str(item['tag']):
                        raise ValueError("Comma in tag is forbidden")
        return v


class ConfigHeaders(BaseModel):
    """Configuration for HTTP headers."""
    payload: Dict[str, Union[str, List[str], ConfigExternalFilePath]]


class ConfigAmqpProperties(BaseModel):
    """Configuration for AMQP message properties."""
    content_type: Optional[str] = None
    content_encoding: Optional[str] = None
    delivery_mode: Optional[int] = None
    priority: Optional[int] = None
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    expiration: Optional[str] = None
    message_id: Optional[str] = None
    timestamp: Optional[float] = None
    type: Optional[str] = Field(None, alias='_type')
    user_id: Optional[str] = None
    app_id: Optional[str] = None
    cluster_id: Optional[str] = None


class ConfigConsume(BaseModel):
    """Configuration for message consumption."""
    queue: str
    group: Optional[str] = None
    key: Optional[str] = None
    schema_config: Optional[ConfigSchema] = Field(None, alias='schema')  # Renamed to avoid conflict
    value: Optional[str] = None
    headers: Optional[ConfigHeaders] = None
    amqp_properties: Optional[ConfigAmqpProperties] = None
    capture: int = 1


class ConfigProduce(BaseModel):
    """Configuration for message production."""
    queue: str
    value: Optional[str] = None
    create: bool = False
    tag: Optional[str] = None
    key: Optional[str] = None
    headers: Optional[ConfigHeaders] = None
    amqp_properties: Optional[ConfigAmqpProperties] = None


class ConfigMultiProduce(BaseModel):
    """Configuration for multiple message production."""
    produce_list: List[ConfigProduce] = Field(default_factory=list, alias='produce')


class ConfigActor(BaseModel):
    """Configuration for asynchronous service actors."""
    name: str
    dataset: Optional[Union[List[Dict[str, Any]], str, ConfigExternalFilePath]] = None
    produce: Optional[Union[ConfigProduce, ConfigMultiProduce]] = None
    consume: Optional[ConfigConsume] = None
    delay: float = 1.0
    limit: Optional[int] = None
    multi_payloads_looped: bool = True
    dataset_looped: bool = True


class ConfigAsyncService(BaseModel):
    """Configuration for asynchronous services (Kafka, AMQP, Redis, etc.)."""
    type: str
    address: str
    name: Optional[str] = None
    ssl: bool = False
    internal_service_id: Optional[int] = None
    
    # Compatibility with old system
    services: List['ConfigAsyncService'] = []
    
    # Service-specific configurations
    actors: List[ConfigActor] = []
    
    def address_template_renderer(self) -> str:
        """Get address template renderer (compatibility method)."""
        return self.address
    
    def get_name(self) -> str:
        """Get service name (compatibility method)."""
        return self.name or ''
    
    def get_hint(self) -> str:
        """Get service hint (compatibility method)."""
        return self.address


class ConfigBody(BaseModel):
    """Configuration for request/response bodies."""
    payload: Optional[Union[str, Dict[str, Any], ConfigExternalFilePath]] = None
    schema_config: Optional[ConfigSchema] = Field(None, alias='schema')  # Renamed to avoid conflict
    graphql_query: Optional[str] = Field(None, alias='graphql-query')
    graphql_variables: Optional[Dict[str, Any]] = Field(None, alias='graphql-variables')


class ConfigResponse(BaseModel):
    """Configuration for HTTP responses."""
    headers: Optional[ConfigHeaders] = None
    status: int = 200
    body: Union[str, ConfigBody, ConfigExternalFilePath]
    use_templating: bool = False
    templating_engine: Optional[str] = None
    tag: Optional[str] = None
    trigger_async_producer: Optional[str] = None


class ConfigMultiResponse(BaseModel):
    """Configuration for multiple responses."""
    responses: List[ConfigResponse] = Field(default_factory=list, alias='response')


class ConfigEndpoint(BaseModel):
    """Configuration for HTTP endpoints."""
    path: str
    id: Optional[str] = None
    comment: Optional[str] = None
    method: str = "GET"
    query_string: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, Any] = Field(default_factory=dict)
    body: Optional[ConfigBody] = None
    dataset: Optional[Union[List[Dict[str, Any]], str, ConfigExternalFilePath]] = None
    response: Union[str, ConfigResponse, ConfigMultiResponse]
    multi_responses_looped: bool = True
    dataset_looped: bool = True
    performance_profile: Optional[str] = None


class ConfigHttpService(BaseModel):
    """Configuration for HTTP services."""
    port: int
    name: Optional[str] = None
    hostname: Optional[str] = "localhost"
    ssl: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None
    management_root: Optional[str] = "/management"
    oas: Optional[Union[str, List[str], ConfigExternalFilePath]] = None
    endpoints: List[ConfigEndpoint] = []
    performance_profile: Optional[str] = None
    fallback_to: Optional[str] = None
    internal_service_id: Optional[int] = None
    templating_engine: str = PYBARS
    
    # Compatibility with old system
    services: List['ConfigHttpService'] = []
    
    def get_name(self) -> str:
        """Get service name (compatibility method)."""
        return self.name or ''
    
    def get_hint(self) -> str:
        """Get service hint (compatibility method)."""
        return f"{self.hostname or 'localhost'}:{self.port}"


class ConfigPerformanceProfile(BaseModel):
    """Configuration for performance profiles."""
    ratio: float
    delay: float
    faults: Optional[Dict[str, float]] = None
    actuator: Optional[Any] = None
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization hook for Pydantic v2."""
        if self.ratio < 0.0 or self.ratio > 1.0:
            raise ValueError("Ratio must be between 0.0 and 1.0")


class ConfigGlobals(BaseModel):
    """Configuration for global settings."""
    headers: Optional[ConfigHeaders] = None
    performance_profile: Optional[str] = None


class ConfigManagement(BaseModel):
    """Configuration for management interface."""
    port: Union[str, int]
    ssl: bool = False
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None


class ConfigRoot(BaseModel):
    """Root configuration for Mockintosh."""
    services: List[Union[ConfigHttpService, ConfigAsyncService]] = []
    management: Optional[ConfigManagement] = None
    templating_engine: str = PYBARS
    globals: Optional[ConfigGlobals] = None
    performance_profiles: Dict[str, ConfigPerformanceProfile] = Field(default_factory=dict)
    
    @field_validator('templating_engine')
    @classmethod
    def validate_templating_engine(cls, v):
        """Validate templating engine."""
        if v not in [PYBARS, JINJA]:
            raise ValueError(f"Templating engine must be one of: {PYBARS}, {JINJA}")
        return v


class MockintoshSettings(BaseSettings):
    """Settings for Mockintosh application."""
    model_config = SettingsConfigDict(
        env_prefix='MOCKINTOSH_',
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields from .env file
    )
    
    config_file: Optional[str] = None
    log_level: str = Field(default="INFO", description="Logging level")
    debug: bool = Field(default=False, description="Enable debug mode")
    host: str = Field(default="localhost", description="Default host")
    default_port: int = Field(default=8000, description="Default port")
    default_templating_engine: str = Field(default=PYBARS, description="Default templating engine")
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v.upper()
    
    @field_validator('default_templating_engine')
    @classmethod
    def validate_default_templating_engine(cls, v):
        """Validate default templating engine."""
        if v not in [PYBARS, JINJA]:
            raise ValueError(f"Default templating engine must be one of: {PYBARS}, {JINJA}")
        return v
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary."""
        return {
            'config_file': self.config_file,
            'log_level': self.log_level,
            'debug': self.debug,
            'host': self.host,
            'default_port': self.default_port,
            'default_templating_engine': self.default_templating_engine
        }
    
    def load_config(self, config_path: Optional[str] = None) -> ConfigRoot:
        """Load configuration from file."""
        import yaml
        import json
        
        config_file = config_path or self.config_file
        if not config_file:
            raise ValueError("No configuration file specified")
        
        file_path = Path(config_file)
        if not file_path.exists():
            raise ValueError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                config_data = yaml.safe_load(f)
            elif file_path.suffix.lower() == '.json':
                config_data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_path.suffix}")
        
        return ConfigRoot(**config_data)


# Export all classes for backward compatibility
__all__ = [
    'ConfigRoot',
    'ConfigHttpService',
    'ConfigAsyncService',
    'ConfigEndpoint',
    'ConfigResponse',
    'ConfigMultiResponse',
    'ConfigBody',
    'ConfigHeaders',
    'ConfigSchema',
    'ConfigActor',
    'ConfigDataset',
    'ConfigConsume',
    'ConfigProduce',
    'ConfigMultiProduce',
    'ConfigAmqpProperties',
    'ConfigExternalFilePath',
    'ConfigManagement',
    'ConfigPerformanceProfile',
    'ConfigGlobals',
    'ConfigService',
    'MockintoshSettings'
] 
