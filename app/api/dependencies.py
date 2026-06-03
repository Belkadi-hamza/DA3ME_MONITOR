"""Global dependencies for API"""
from typing import Optional
from app.core.auth import AuthClient
from app.core.scraper import QuizScraper
from app.core.config import Settings

# Global instances
_driver = None
_auth_client = None
_scraper = None


def get_driver():
    """Get or initialize the browser driver"""
    global _driver, _auth_client
    
    if _driver is None:
        Settings.validate()
        _auth_client = AuthClient(
            base_url=Settings.BASE_URL,
            login_url=Settings.LOGIN_URL,
            username=Settings.USERNAME,
            password=Settings.PASSWORD
        )
        _auth_client.login()
        _driver = _auth_client.driver
    
    return _driver


def get_scraper() -> QuizScraper:
    """Get or initialize the scraper"""
    global _scraper
    
    if _scraper is None:
        driver = get_driver()
        Settings.validate()
        _scraper = QuizScraper(driver, Settings.COURSE_URL)
    
    return _scraper


def close_driver():
    """Close the browser driver"""
    global _driver, _auth_client, _scraper
    
    if _auth_client:
        _auth_client.close()
    
    _driver = None
    _auth_client = None
    _scraper = None
