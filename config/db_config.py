from dataclasses import dataclass
import os


@dataclass
class DBConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    minconn: int = 1
    maxconn: int = 10
    # SSL configuration
    ssl_mode: str = 'require'
    ssl_cert: str = None
    ssl_key: str = None
    ssl_ca: str = None
    
    def __post_init__(self):
        """Set SSL configuration based on environment"""
        # Check if running in development mode
        is_development = os.getenv('FLASK_ENV') == 'development' or os.getenv('FLASK_DEBUG') == '1'
        is_ci_mode = os.getenv('CI') == 'true' or os.getenv('GITHUB_ACTIONS') == 'true'
        
        # Get custom SSL mode from environment
        custom_ssl_mode = os.getenv('DATABASE_SSL_MODE')
        
        # In development or CI, allow less strict SSL
        if is_development or is_ci_mode:
            self.ssl_mode = custom_ssl_mode if custom_ssl_mode else 'prefer'
        else:
            # Production: require SSL
            self.ssl_mode = custom_ssl_mode if custom_ssl_mode else 'require'
        
        # SSL certificate configuration (optional)
        self.ssl_cert = os.getenv('DATABASE_SSL_CERT')
        self.ssl_key = os.getenv('DATABASE_SSL_KEY') 
        self.ssl_ca = os.getenv('DATABASE_SSL_CA')
