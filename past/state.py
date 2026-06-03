# state.py
import json
import os
from datetime import datetime

STATE_FILE = "state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        print("No previous state found. Starting fresh.")
        return {"sections": {}}   # new structure
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: dict):
    print("Saving state...")
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
    print("State saved successfully.")

def _get_section_state(state, section_id):
    """Ensure section exists in state and return its dict."""
    if "sections" not in state:
        state["sections"] = {}
    if section_id not in state["sections"]:
        state["sections"][section_id] = {
            "quizzes": {},
            "pdfs": {},
            "assignments": {}
        }
    return state["sections"][section_id]

def update_section_items(state, section_id: str, section_title: str,
                         quizzes: list, pdfs: list, assignments: list):
    """
    quizzes, pdfs, assignments: list of dicts [{'name':..., 'url':...}]
    Stores in state["sections"][section_id][type][url] = {...}
    """
    sec_state = _get_section_state(state, section_id)
    sec_state["title"] = section_title   # store title for display
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

    save_state(state)

def find_new_items_in_section(state, section_id: str,
                              quizzes: list, pdfs: list, assignments: list):
    """Return three lists: new_quizzes, new_pdfs, new_assignments for this section."""
    sec_state = _get_section_state(state, section_id)

    known_quiz_urls = set(sec_state["quizzes"].keys())
    new_quizzes = [q for q in quizzes if q["url"] not in known_quiz_urls]

    known_pdf_urls = set(sec_state["pdfs"].keys())
    new_pdfs = [p for p in pdfs if p["url"] not in known_pdf_urls]

    known_assign_urls = set(sec_state["assignments"].keys())
    new_assignments = [a for a in assignments if a["url"] not in known_assign_urls]

    return new_quizzes, new_pdfs, new_assignments