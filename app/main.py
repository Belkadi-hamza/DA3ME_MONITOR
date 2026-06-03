"""Main entry point for Da3me Monitor application"""
import logging
import time
import sys
from flask import Flask
from dotenv import load_dotenv

from app.core.auth import AuthClient
from app.core.scraper import QuizScraper
from app.core.config import Settings
from app.services.course_service import CourseService
from app.utils.logging import setup_logging
from app.api.routes import api
from app.api.dependencies import close_driver

load_dotenv()
setup_logging(logging.INFO)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    
    # Register API blueprint
    app.register_blueprint(api)
    
    # Cleanup on shutdown
    @app.teardown_appcontext
    def shutdown(exception=None):
        close_driver()
    
    return app


def monitor_course_cli():
    """CLI mode: continuous monitoring with logging"""
    try:
        Settings.validate()
        logger.info("🚀 Logging in once...")
        
        auth_client = AuthClient(
            base_url=Settings.BASE_URL,
            login_url=Settings.LOGIN_URL,
            username=Settings.USERNAME,
            password=Settings.PASSWORD
        )
        auth_client.login()
        driver = auth_client.driver
        
        scraper = QuizScraper(driver, Settings.COURSE_URL)
        course_service = CourseService(Settings.STATE_FILE)
        
        logger.info(f"🔁 Starting monitoring loop every {Settings.CHECK_INTERVAL_SECONDS} seconds")
        
        while True:
            logger.info("--- Checking for new activities ---")
            try:
                sections = scraper.get_sections_with_activities()
                
                sections_with_new = []
                
                for sec in sections:
                    sec_id = sec["section_id"]
                    sec_title = sec["section_title"]
                    quizzes = sec["quizzes"]
                    pdfs = sec["pdfs"]
                    assignments = sec["assignments"]
                    
                    new_q, new_p, new_a = course_service.find_new_items_in_section(
                        sec_id, quizzes, pdfs, assignments
                    )
                    
                    if new_q or new_p or new_a:
                        sections_with_new.append({
                            "section_title": sec_title,
                            "new_quizzes": new_q,
                            "new_pdfs": new_p,
                            "new_assignments": new_a
                        })
                        # Update state with current items
                        course_service.update_section_items(
                            sec_id, sec_title, quizzes, pdfs, assignments
                        )
                        logger.info(f"📌 {sec_title}: {len(new_q)} quizzes, {len(new_p)} PDFs, {len(new_a)} assignments")
                
                if not sections_with_new:
                    logger.info("✅ No new activities detected")
                else:
                    logger.info(f"✨ Found new items in {len(sections_with_new)} section(s)")
                
                logger.info(f"💤 Sleeping for {Settings.CHECK_INTERVAL_SECONDS} seconds")
                time.sleep(Settings.CHECK_INTERVAL_SECONDS)
            
            except Exception as e:
                logger.error(f"Error during monitoring cycle: {e}")
                logger.info(f"💤 Sleeping for {Settings.CHECK_INTERVAL_SECONDS} seconds before retry")
                time.sleep(Settings.CHECK_INTERVAL_SECONDS)
    
    except KeyboardInterrupt:
        logger.info("🛑 Manual stop requested")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        if 'auth_client' in locals():
            auth_client.close()
        logger.info("🔒 Browser closed")


def run_server():
    """Run Flask API server"""
    try:
        Settings.validate()
        app = create_app()
        logger.info(f"🚀 Starting server on {Settings.HOST}:{Settings.PORT}")
        app.run(
            host=Settings.HOST,
            port=Settings.PORT,
            debug=Settings.DEBUG
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Da3me Monitor - Moodle course activity monitor")
    parser.add_argument(
        "--mode",
        choices=["cli", "server"],
        default="server",
        help="Run in CLI monitoring mode or as Flask API server (default: server)"
    )
    
    args = parser.parse_args()
    
    if args.mode == "cli":
        logger.info("📟 Running in CLI mode (continuous monitoring)")
        monitor_course_cli()
    else:
        logger.info("🌐 Running in server mode (Flask API)")
        run_server()
