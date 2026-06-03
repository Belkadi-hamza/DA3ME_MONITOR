import logging
from flask import Flask, jsonify
from past.auth import AuthClient
from past.scraper import QuizScraper
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Global driver – reused across requests (saves time)
driver = None
auth_client = None

def init_driver():
    global driver, auth_client
    if driver is None:
        auth_client = AuthClient(
            base_url=os.getenv("DA3ME_BASE_URL"),
            login_url=os.getenv("DA3ME_LOGIN_URL"),
            username=os.getenv("DA3ME_USERNAME"),
            password=os.getenv("DA3ME_PASSWORD")
        )
        auth_client.login()
        driver = auth_client.driver
        logging.info("🚀 Driver initialized and logged in")

@app.route('/api/course', methods=['GET'])
def get_course():
    init_driver()
    course_url = os.getenv("DA3ME_COURSE_URL")
    scraper = QuizScraper(driver, course_url)
    sections = scraper.get_sections_with_activities()  # returns list of sections with quizzes/pdfs/assignments
    return jsonify({
        "status": "ok",
        "course_url": course_url,
        "sections": sections
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "alive"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)