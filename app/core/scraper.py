import logging
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from .parser import parse_course

logger = logging.getLogger(__name__)

class QuizScraper:
    def __init__(self, driver, course_url: str):
        self.driver = driver
        self.course_url = course_url

    def get_sections_with_activities(self, retries=3):
        """
        Returns a list of sections, each with:
        {
            "section_id": str,
            "section_title": str,
            "quizzes": [{"name":..., "url":...}],
            "pdfs": [...],
            "assignments": [...]
        }
        """
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"🌐 Navigating to course (attempt {attempt}/{retries})")
                self.driver.get(self.course_url)
                
                # Wait for course index to appear
                logger.info("⏳ Waiting for course index...")
                WebDriverWait(self.driver, 8).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#course-index"))
                )
                
                # Small delay for content to render
                time.sleep(1)
                
                html = self.driver.page_source
                course_data = parse_course(html)

                sections = []
                for sec in course_data:
                    sections.append({
                        "section_id": sec.get("section_id"),
                        "section_title": sec["section_title"],
                        "quizzes": sec["items"].get("quiz", []),
                        "pdfs": sec["items"].get("pdf", []),
                        "assignments": sec["items"].get("assignment", [])
                    })
                logger.info(f"📚 Extracted {len(sections)} sections with activities")
                return sections
            
            except TimeoutException:
                logger.warning(f"⏱️ Timeout waiting for course index (attempt {attempt}/{retries})")
                if attempt < retries:
                    time.sleep(2)
                else:
                    logger.error("❌ Course index not found after retries")
                    raise
            
            except WebDriverException as e:
                logger.warning(f"⚠️ WebDriver error (attempt {attempt}/{retries})")
                if attempt < retries:
                    time.sleep(3)
                else:
                    logger.error(f"❌ Failed to navigate course: {e}")
                    raise
            
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                raise
