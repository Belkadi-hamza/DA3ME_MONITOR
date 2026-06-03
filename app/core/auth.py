import logging
import time
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,
)

from webdriver_manager.chrome import ChromeDriverManager


logger = logging.getLogger(__name__)


@dataclass
class AuthConfig:
    base_url: str
    login_url: str
    username: str
    password: str


class AuthClient:
    def __init__(self, base_url, login_url, username, password):
        self.config = AuthConfig(
            base_url,
            login_url,
            username,
            password,
        )

        self.driver = self._init_driver()

    def _init_driver(self):
        try:
            options = webdriver.ChromeOptions()

            # Essential arguments
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # Memory optimization - reduce resource usage
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-plugins")
            
            # Disable images to reduce memory
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
            
            options.add_experimental_option(
                "excludeSwitches",
                ["enable-automation"]
            )

            options.add_experimental_option(
                "useAutomationExtension",
                False
            )

            driver = webdriver.Chrome(
                service = Service(
                    ChromeDriverManager(driver_version="149.0.7827.54").install()
                ),
                options=options
            )

            driver.execute_script(
                """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
            )

            logger.info("🌐 Chrome driver initialized successfully")

            return driver

        except WebDriverException as e:
            logger.error(f"❌ Chrome init failed: {e}")
            raise

    def login(self):
        try:
            logger.info("🔐 Starting authentication...")
            logger.info(f"📍 Login URL: {self.config.login_url}")

            self.driver.get(self.config.login_url)
            logger.info(f"📄 Current page URL: {self.driver.current_url}")
            logger.info(f"📄 Current page title: {self.driver.title}")

            wait = WebDriverWait(self.driver, 20)

            logger.info("⏳ Waiting for login form...")

            wait.until(
                EC.presence_of_element_located(
                    (By.ID, "username")
                )
            )

            # Retry block against stale elements
            for attempt in range(3):

                try:

                    logger.info(
                        f"🔑 Filling credentials (attempt {attempt + 1}/3)..."
                    )

                    username_input = wait.until(
                        EC.element_to_be_clickable(
                            (By.ID, "username")
                        )
                    )

                    password_input = wait.until(
                        EC.element_to_be_clickable(
                            (By.ID, "password")
                        )
                    )

                    username_input.clear()
                    username_input.send_keys(
                        self.config.username
                    )
                    logger.info(f"✏️ Username entered: {self.config.username}")

                    password_input.clear()
                    password_input.send_keys(
                        self.config.password
                    )
                    logger.info(f"✏️ Password entered: {'*' * len(self.config.password)}")

                    # Verify values were entered
                    username_value = username_input.get_attribute("value")
                    logger.info(f"✅ Username field contains: {username_value}")

                    break

                except StaleElementReferenceException:

                    logger.warning(
                        f"⚠️ Stale element while filling form. Retrying..."
                    )

                    time.sleep(1)

            logger.info("🚀 Clicking login button...")
            logger.info(f"📄 Page before login click - URL: {self.driver.current_url}")

            login_button = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "loginbtn")
                )
            )

            login_button.click()
            time.sleep(2)

            logger.info(f"📄 Page after login click - URL: {self.driver.current_url}")
            logger.info(f"📄 Page after login click - Title: {self.driver.title}")
            
            # Check if still on login page (login failed)
            if "login" in self.driver.current_url.lower() and "login/index.php" in self.driver.current_url:
                logger.error("❌ Still on login page - credentials may be incorrect!")
                # Try to get error message
                try:
                    error_msg = self.driver.find_element(By.CLASS_NAME, "alert-error")
                    logger.error(f"❌ Login error: {error_msg.text}")
                except:
                    pass
                
                # Get page content to debug
                page_text = self.driver.find_element(By.TAG_NAME, "body").text
                logger.error(f"❌ Page content (first 500 chars): {page_text[:500]}")
                raise Exception("Login failed - credentials rejected by server")
            
            logger.info("✅ Login successful")
            return self.driver

        except TimeoutException:
            logger.error("❌ Timeout: Unable to complete login")
            raise
        except Exception as e:
            logger.error(f"❌ Login failed")
            raise

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Browser closed")
