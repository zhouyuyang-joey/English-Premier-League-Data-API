"""
Configuration module for eplda library.

This module contains all configuration settings for the API client.
Settings can be overridden through environment variables or external config files.
"""

import os
import yaml
from typing import Dict, Any, Optional


class APIConfig:
    """
    Central configuration class for EPLAPI.
    
    Manages API endpoints, headers, timeouts, and other configurable parameters.
    Can be customized through environment variables or external YAML files.
    """
    
    # Default API configuration
    DEFAULT_CONFIG = {
        'api': {
            'root_url': 'https://footballapi.pulselive.com/football/',
            'timeout': 30,
            'max_retries': 3,
            'retry_delay': 1,
        },
        'headers': {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://www.premierleague.com',
            'referer': 'https://www.premierleague.com',
            'User-Agent': 'EPLAPI-Client/1.0'
        },
        'pagination': {
            'default_page_size': 20,
            'max_page_size': 100,
            'max_players_page_size': 100
        },
        'competition': {
            'premier_league_id': 1,
            'comp_code': 'EN_PR'
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to external YAML configuration file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        # Load external config file if provided
        if config_file and os.path.exists(config_file):
            self._load_config_file(config_file)
        
        # Override with environment variables
        self._load_environment_variables()
    
    def _load_config_file(self, config_file: str) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as file:
                external_config = yaml.safe_load(file)
                if external_config:
                    self._merge_config(self.config, external_config)
        except (yaml.YAMLError, IOError) as e:
            # Log warning but continue with default config
            print(f"Warning: Could not load config file {config_file}: {e}")
    
    def _load_environment_variables(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'EPLAPI_ROOT_URL': ('api', 'root_url'),
            'EPLAPI_TIMEOUT': ('api', 'timeout'),
            'EPLAPI_MAX_RETRIES': ('api', 'max_retries'),
            'EPLAPI_RETRY_DELAY': ('api', 'retry_delay'),
            'EPLAPI_DEFAULT_PAGE_SIZE': ('pagination', 'default_page_size'),
            'EPLAPI_MAX_PAGE_SIZE': ('pagination', 'max_page_size'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                # Convert string values to appropriate types
                if key in ['timeout', 'max_retries', 'retry_delay', 'default_page_size', 'max_page_size']:
                    try:
                        value = int(value)
                    except ValueError:
                        continue
                
                if section not in self.config:
                    self.config[section] = {}
                self.config[section][key] = value
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if not found
            
        Returns:
            Configuration value or default
        """
        return self.config.get(section, {}).get(key, default)
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return self.config.get('headers', {}).copy()
    
    def get_root_url(self) -> str:
        """Get API root URL."""
        return self.get('api', 'root_url')
    
    def get_timeout(self) -> int:
        """Get request timeout in seconds."""
        return self.get('api', 'timeout')
    
    def get_max_retries(self) -> int:
        """Get maximum number of retries for failed requests."""
        return self.get('api', 'max_retries')
    
    def get_retry_delay(self) -> int:
        """Get delay between retries in seconds."""
        return self.get('api', 'retry_delay')
    
    def get_default_page_size(self) -> int:
        """Get default pagination page size."""
        return self.get('pagination', 'default_page_size')
    
    def get_max_page_size(self) -> int:
        """Get maximum allowed page size."""
        return self.get('pagination', 'max_page_size')
    
    def get_premier_league_id(self) -> int:
        """Get Premier League competition ID."""
        return self.get('competition', 'premier_league_id')
    
    def get_comp_code(self) -> str:
        """Get competition code for active players."""
        return self.get('competition', 'comp_code')


# Global configuration instance
config = APIConfig()


def set_config_file(config_file: str) -> None:
    """
    Set external configuration file.
    
    Args:
        config_file: Path to YAML configuration file
    """
    global config
    config = APIConfig(config_file)


def get_config() -> APIConfig:
    """Get the global configuration instance."""
    return config