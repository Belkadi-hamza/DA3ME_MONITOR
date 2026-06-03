"""Data models and schemas"""
from typing import List, Optional
from pydantic import BaseModel


class Activity(BaseModel):
    """Single activity (quiz, PDF, assignment)"""
    name: str
    url: str


class Section(BaseModel):
    """Course section with activities"""
    section_id: Optional[str] = None
    section_title: str
    quizzes: List[Activity] = []
    pdfs: List[Activity] = []
    assignments: List[Activity] = []


class CourseResponse(BaseModel):
    """API response for course data"""
    status: str
    course_url: str
    sections: List[Section] = []


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
