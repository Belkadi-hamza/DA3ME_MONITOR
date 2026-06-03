"""Course monitoring service - tracks activities and manages state"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)


class CourseService:
    """Service for monitoring course activities and managing state"""
    
    def __init__(self, state_file: str = "state.json"):
        self.state_file = state_file
        self.state = self.load_state()
    
    def load_state(self) -> dict:
        """Load state from file"""
        if not os.path.exists(self.state_file):
            logger.info("📄 No previous state found. Starting fresh.")
            return {"sections": {}}
        with open(self.state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_state(self):
        """Save state to file"""
        logger.info("💾 Saving state...")
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
        logger.info("✅ State saved successfully.")
    
    def _get_section_state(self, section_id: str) -> dict:
        """Ensure section exists in state and return its dict"""
        if "sections" not in self.state:
            self.state["sections"] = {}
        if section_id not in self.state["sections"]:
            self.state["sections"][section_id] = {
                "quizzes": {},
                "pdfs": {},
                "assignments": {}
            }
        return self.state["sections"][section_id]
    
    def update_section_items(self, section_id: str, section_title: str,
                            quizzes: list, pdfs: list, assignments: list):
        """Update state with current section items"""
        sec_state = self._get_section_state(section_id)
        sec_state["title"] = section_title
        now = datetime.now().isoformat()
        
        for q in quizzes:
            if q["url"] not in sec_state["quizzes"]:
                sec_state["quizzes"][q["url"]] = {
                    "name": q["name"],
                    "first_seen": now,
                    "last_seen": now
                }
            else:
                sec_state["quizzes"][q["url"]]["last_seen"] = now
        
        for p in pdfs:
            if p["url"] not in sec_state["pdfs"]:
                sec_state["pdfs"][p["url"]] = {
                    "name": p["name"],
                    "first_seen": now,
                    "last_seen": now
                }
            else:
                sec_state["pdfs"][p["url"]]["last_seen"] = now
        
        for a in assignments:
            if a["url"] not in sec_state["assignments"]:
                sec_state["assignments"][a["url"]] = {
                    "name": a["name"],
                    "first_seen": now,
                    "last_seen": now
                }
            else:
                sec_state["assignments"][a["url"]]["last_seen"] = now
        
        self.save_state()
    
    def find_new_items_in_section(self, section_id: str,
                                 quizzes: list, pdfs: list, assignments: list):
        """Find new items in a section by comparing with known URLs"""
        sec_state = self._get_section_state(section_id)
        
        known_quiz_urls = set(sec_state["quizzes"].keys())
        new_quizzes = [q for q in quizzes if q["url"] not in known_quiz_urls]
        
        known_pdf_urls = set(sec_state["pdfs"].keys())
        new_pdfs = [p for p in pdfs if p["url"] not in known_pdf_urls]
        
        known_assign_urls = set(sec_state["assignments"].keys())
        new_assignments = [a for a in assignments if a["url"] not in known_assign_urls]
        
        return new_quizzes, new_pdfs, new_assignments
