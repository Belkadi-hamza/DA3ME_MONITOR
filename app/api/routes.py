"""API routes for course monitoring"""
from flask import Blueprint, jsonify, current_app
import logging
from app.core.scraper import QuizScraper
from app.core.config import Settings
from app.api.dependencies import get_driver, get_scraper

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')


@api.route('/course', methods=['GET'])
def get_course():
    """Get all sections with activities from the course"""
    try:
        scraper = get_scraper()
        sections = scraper.get_sections_with_activities()
        
        return jsonify({
            "status": "ok",
            "course_url": Settings.COURSE_URL,
            "sections": sections
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Error fetching course: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@api.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "alive"}), 200
