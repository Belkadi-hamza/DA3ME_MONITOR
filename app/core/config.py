"""Configuration management"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment variables"""
    
    # Da3me configuration
    BASE_URL = os.getenv("DA3ME_BASE_URL", "https://da3me.ma")
    LOGIN_URL = os.getenv("DA3ME_LOGIN_URL", "https://da3me.ma/login/index.php")
    COURSE_URL = os.getenv("DA3ME_COURSE_URL")
    
    # Credentials
    USERNAME = os.getenv("DA3ME_USERNAME")
    PASSWORD = os.getenv("DA3ME_PASSWORD")
    
    # Monitoring
    CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "3600"))
    
    # State file
    STATE_FILE = os.getenv("STATE_FILE", "state.json")
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.USERNAME or not cls.PASSWORD:
            raise ValueError("Missing credentials: USERNAME and PASSWORD required in .env")
        if not cls.COURSE_URL:
            raise ValueError("Missing COURSE_URL in .env")
