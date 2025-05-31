import os
from typing import Dict, Optional

class APIConfig:
    # Base API configuration
    BASE_URL = "https://footballapi.pulselive.com/football/"

    # Default request headers
    DEFAULT_HEADERS = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://www.premierleague.com',
        'referer': 'https://www.premierleague.com',
        'User-Agent': 'Mozilla/5.0 (compatible; EPL-Data-API/1.0)'
    }

    # Default request parameters
    DEFAULT_TIMEOUT = 30  # seconds
    DEFAULT_RETRIES = 3
    DEFAULT_PAGE_SIZE = 50
    
    # Competition ID for Premier League
    PREMIER_LEAGUE_ID = 1
    
    # Default output formats
    SUPPORTED_OUTPUT_FORMATS = ['json', 'df']
    DEFAULT_OUTPUT_FORMAT = 'json'
    
    # API rate limiting
    MAX_REQUESTS_PER_MINUTE = 60
    REQUEST_DELAY = 1.0  # seconds between requests

    