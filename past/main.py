# main.py
import logging
import os
import time
from dotenv import load_dotenv
from past.auth import AuthClient
from past.scraper import QuizScraper
from past.state import load_state, save_state, update_section_items, find_new_items_in_section

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# === CONFIGURATION FROM .env ===
BASE_URL = os.getenv("DA3ME_BASE_URL", "https://da3me.ma")
LOGIN_URL = os.getenv("DA3ME_LOGIN_URL", "https://da3me.ma/login/index.php")
COURSE_URL = os.getenv("DA3ME_COURSE_URL")   # must be set in .env

USERNAME = os.getenv("DA3ME_USERNAME")
PASSWORD = os.getenv("DA3ME_PASSWORD")
CHECK_INTERVAL_SECONDS = 3600   # 1 hour (you can change this)

if not USERNAME or not PASSWORD:
    raise ValueError("Missing credentials in .env")
if not COURSE_URL:
    raise ValueError("Missing DA3ME_COURSE_URL in .env")

def monitor_course(driver, course_url, state):
    scraper = QuizScraper(driver, course_url)
    sections = scraper.get_sections_with_activities()

    # Prepare data for notification
    sections_with_new = []

    for sec in sections:
        sec_id = sec["section_id"]
        sec_title = sec["section_title"]
        quizzes = sec["quizzes"]
        pdfs = sec["pdfs"]
        assignments = sec["assignments"]

        new_q, new_p, new_a = find_new_items_in_section(
            state, sec_id, quizzes, pdfs, assignments
        )

        if new_q or new_p or new_a:
            sections_with_new.append({
                "section_title": sec_title,
                "new_quizzes": new_q,
                "new_pdfs": new_p,
                "new_assignments": new_a
            })
            # Update state with current items (including old)
            update_section_items(state, sec_id, sec_title, quizzes, pdfs, assignments)
            # Log new items found
            logger.info(f"📌 {sec_title}: {len(new_q)} quizzes, {len(new_p)} PDFs, {len(new_a)} assignments")  

    if not sections_with_new:
        logger.info("✅ No new activities detected")
    else:
        logger.info(f"✨ Found new items in {len(sections_with_new)} section(s)")

    return state

def main():
    auth = AuthClient(BASE_URL, LOGIN_URL, USERNAME, PASSWORD)
    state = load_state()

    try:
        logger.info("🚀 Logging in once...")
        auth.login()
        driver = auth.driver

        logger.info(f"🔁 Starting monitoring loop every {CHECK_INTERVAL_SECONDS} seconds")
        while True:
            logger.info("--- Checking for new quizzes ---")
            try:
                state = monitor_course(driver, COURSE_URL, state)
                save_state(state)
            except Exception as e:
                logger.error(f"Error during monitoring cycle: {e}")
            logger.info(f"💤 Sleeping for {CHECK_INTERVAL_SECONDS} seconds")
            time.sleep(CHECK_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("🛑 Manual stop requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        auth.close()
        logger.info("🔒 Browser closed")

if __name__ == "__main__":
    main()