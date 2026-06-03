import logging
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from past.parser import parse_course

logger = logging.getLogger(__name__)

class QuizScraper:
    def __init__(self, driver, course_url: str):
        self.driver = driver
        self.course_url = course_url

    def get_sections_with_activities(self):
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
        logger.info(f"🌐 Navigating to course: {self.course_url}")
        self.driver.get(self.course_url)
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#course-index"))
        )
        html = self.driver.page_source
        course_data = parse_course(html)   # from previous parser

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

        for section in course_data:
            section_title = section['section_title']
            for q in section['items'].get('quiz', []):
                result['quizzes'].append({**q, 'section': section_title})
            for p in section['items'].get('pdf', []):
                result['pdfs'].append({**p, 'section': section_title})
            for a in section['items'].get('assignment', []):
                result['assignments'].append({**a, 'section': section_title})

        logger.info(f"📊 Found: {len(result['quizzes'])} quizzes, "
                    f"{len(result['pdfs'])} PDFs, "
                    f"{len(result['assignments'])} assignments")
        return result