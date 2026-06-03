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

            options.add_argument("--start-maximized")
            options.add_argument(
                "--disable-blink-features=AutomationControlled"
            )

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

            self.driver.get(self.config.login_url)

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
                        f"🔑 Filling credentials (attempt {attempt + 1})..."
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

                    password_input.clear()
                    password_input.send_keys(
                        self.config.password
                    )

                    break

                except StaleElementReferenceException:

                    logger.warning(
                        "⚠️ Stale element while filling form. Retrying..."
                    )

                    time.sleep(1)

            logger.info("🚀 Clicking login...")

            login_button = wait.until(
                EC.element_to_be_clickable(
                    (By.ID, "loginbtn")
                )
            )

            login_button.click()

            logger.info(
                "⏳ Waiting for login result..."
            )

            time.sleep(5)

            if self._is_login_failed():

                self._save_debug()

                raise Exception(
                    "Login failed (invalid credentials)"
                )

            current_url = self.driver.current_url

            if "login" not in current_url.lower():

                logger.info("✅ Login successful")
                return True

            logger.warning(
                "⚠️ Still on login page, checking content..."
            )

            if self._is_login_failed():

                self._save_debug()

                raise Exception(
                    "Login failed (server rejected credentials)"
                )

            logger.info(
                "✅ Login probably successful"
            )

            return True

        except TimeoutException:

            self._save_debug()

            logger.error(
                "❌ Timeout during login"
            )

            raise

        except Exception as e:

            self._save_debug()

            logger.error(
                f"❌ Login failed: {e}"
            )

            raise

    def _is_login_failed(self):
        try:

            page = self.driver.page_source.lower()

            return (
                "invalid login" in page
                or "please try again" in page
            )

        except Exception:
            return False

    def _save_debug(self):
        try:

            self.driver.save_screenshot(
                "login_error.png"
            )

            with open(
                "login_debug.html",
                "w",
                encoding="utf-8"
            ) as f:
                f.write(
                    self.driver.page_source
                )

            logger.error(
                "📸 Debug saved: login_error.png + login_debug.html"
            )

        except Exception as e:

            logger.error(
                f"Failed saving debug: {e}"
            )

    def close(self):
        if self.driver:
            self.driver.quit()