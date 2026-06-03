import logging
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def classify_activity_by_url(url: str) -> str:
    """Classify activity based on URL path."""
    if not url:
        return "other"
    if "/mod/quiz/view.php" in url:
        return "quiz"
    if "/mod/resource/view.php" in url:
        return "pdf"
    if "/mod/assign/view.php" in url:
        return "assignment"
    if "/mod/folder/view.php" in url:
        return "folder"
    if "/mod/forum/view.php" in url:
        return "forum"
    return "other"

def parse_course(html: str) -> list:
    """
    Parse the Moodle course page using the course index (#course-index)
    which is always present even in Tiles format.
    Returns a list of sections, each with section_title and items dict.
    """
    soup = BeautifulSoup(html, "html.parser")
    course_index = soup.select_one("#course-index")
    if not course_index:
        logger.warning("⚠️ #course-index not found – falling back to generic parsing")
        return _parse_generic(soup)

    sections_data = []
    sections = course_index.select(".courseindex-section")

    for section in sections:
        # Extract section title
        title_elem = section.select_one(".courseindex-link")
        section_title = title_elem.text.strip() if title_elem else "Section sans titre"

        items = {
            "quiz": [],
            "pdf": [],
            "assignment": [],
            "folder": [],
            "forum": [],
            "other": []
        }

        # Find all activities (courseindex-item) inside this section
        activities = section.select(".courseindex-item[data-for='cm']")
        for act in activities:
            link = act.select_one("a.courseindex-link")
            if not link:
                continue
            name = link.text.strip()
            url = link.get("href", "")
            if not url:
                continue

            category = classify_activity_by_url(url)
            items[category].append({"name": name, "url": url})

        sections_data.append({
            "section_id": section.get("data-id"),
            "section_title": section_title,
            "items": items
        })

    logger.info(f"📚 Parsed {len(sections_data)} sections from course index")
    total_quizzes = sum(len(s["items"]["quiz"]) for s in sections_data)
    logger.info(f"📝 Found {total_quizzes} quizzes in total")
    return sections_data

def _parse_generic(soup):
    """Fallback: try to parse hidden sections (original approach)"""
    sections_data = []
    hidden_sections = soup.select("li.section.course-section.main.moveablesection")
    for sec in hidden_sections:
        title_elem = sec.select_one(".sectionname, .sectiontitle h2")
        section_title = title_elem.text.strip() if title_elem else "Section"
        items = {"quiz": [], "pdf": [], "assignment": [], "other": []}
        activities = sec.select("li.courseindex-item")
        for act in activities:
            link = act.select_one("a")
            if not link:
                continue
            name = link.text.strip()
            url = link.get("href", "")
            category = classify_activity_by_url(url)
            items.setdefault(category, []).append({"name": name, "url": url})
        sections_data.append({
            "section_id": sec.get("data-section"),
            "section_title": section_title,
            "items": items
        })
    return sections_data
