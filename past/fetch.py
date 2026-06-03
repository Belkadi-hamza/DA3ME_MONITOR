import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class Fetcher:
    def __init__(self, auth):
        self.auth = auth
        self.driver = None
        self.driver = self._init_driver()

    def _init_driver(self):
        try:
            logging.info("🚀 Starting Chrome driver...")

            options = Options()
            options.add_argument("--start-maximized")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-gpu")

            # IMPORTANT FIX: uncomment if Chrome not detected
            # options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )

            logging.info("✅ Chrome driver started successfully")
            return driver

        except Exception as e:
            logging.error(f"❌ Failed to start Chrome driver: {e}")
            raise

    def get_page(self, url: str) -> str:
        try:
            logging.info(f"🌐 Opening URL: {url}")
            self.driver.get(url)

            html = self.driver.page_source
            logging.info("📄 Page fetched successfully")

            return html

        except Exception as e:
            logging.error(f"❌ Error fetching page: {e}")
            return ""