"""
Configuration management for EPLDA (English Premier League Data API)
"""
import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for EPLDA library"""
    
    # Core API settings (not user-configurable)
    ROOT_URL = 'https://footballapi.pulselive.com/football/'
    HEADERS = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.premierleague.com',
        'referer': 'https://www.premierleague.com',
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_path: Path to custom configuration file
        """
        self._config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load configuration from YAML file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Configuration dictionary
        """
        if config_path is None:
            # Use default config file in the same directory
            current_dir = Path(__file__).parent
            config_path = current_dir / 'config.yaml'
        
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            # Return default configuration if file not found
            return self._get_default_config()
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration file: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration when config file is not available"""
        return {
            'request': {
                'timeout': 30,
                'max_retries': 3,
                'retry_delay': 1,
                'page_size': 100
            },
            'competition': {
                'premier_league_id': 1,
                'comp_code': 'EN_PR',
                'club_page_size': 20,
                'player_page_size': 50
            },
            'data': {
                'default_output_format': 'json',
                'include_nationality': True,
                'filter_first_team_only': True
            },
            'cache': {
                'enabled': False,
                'ttl': 3600
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'request.timeout')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'request.timeout')
            value: Value to set
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the final value
        config[keys[-1]] = value
    
    @property
    def request_timeout(self) -> int:
        """Request timeout in seconds"""
        return self.get('request.timeout', 30)
    
    @property
    def max_retries(self) -> int:
        """Maximum number of retry attempts"""
        return self.get('request.max_retries', 3)
    
    @property
    def retry_delay(self) -> int:
        """Delay between retries in seconds"""
        return self.get('request.retry_delay', 1)
    
    @property
    def default_page_size(self) -> int:
        """Default page size for paginated requests"""
        return self.get('request.page_size', 100)
    
    @property
    def default_output_format(self) -> str:
        """Default output format"""
        return self.get('data.default_output_format', 'df')
    
    @property
    def include_nationality(self) -> bool:
        """Whether to include nationality in player data"""
        return self.get('data.include_nationality', True)
    
    @property
    def filter_first_team_only(self) -> bool:
        """Whether to filter only first team players"""
        return self.get('data.filter_first_team_only', True)
    
    # Competition-specific properties
    @property
    def premier_league_id(self) -> int:
        """Premier League competition ID"""
        return self.get('competition.premier_league_id', 1)
    
    @property
    def comp_code(self) -> str:
        """Competition code for active players"""
        return self.get('competition.comp_code', 'EN_PR')
    
    @property
    def club_page_size(self) -> int:
        """Page size for club data (20 teams in EPL)"""
        return self.get('competition.club_page_size', 20)
    
    @property
    def player_page_size(self) -> int:
        """Page size for player rankings"""
        return self.get('competition.player_page_size', 50)


# Global configuration instance
config = Config()