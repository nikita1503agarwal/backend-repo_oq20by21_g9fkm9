"""
Database Schemas for Maatram KK360

Each Pydantic model maps to a MongoDB collection using the lowercase class name.
Examples:
- Tutor -> "tutor"
- Student -> "student"
- Class -> "class"

These schemas are used for validation in API endpoints and exposed at GET /schema for tooling.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class Tutor(BaseModel):
    name: str = Field(..., description="Tutor full name")
    email: EmailStr = Field(..., description="Tutor email")
    subjects: List[str] = Field(default_factory=list, description="Subjects the tutor can teach")
    availability: List[str] = Field(default_factory=list, description="Available time slots, e.g., Mon-10:00")
    institution_id: Optional[str] = Field(None, description="Institution/center ID")
    rating: Optional[float] = Field(default=None, ge=0, le=5)

class Student(BaseModel):
    name: str = Field(..., description="Student full name")
    grade: int = Field(..., ge=11, le=12, description="Grade 11 or 12")
    student_id: str = Field(..., description="Unique student identifier")
    subjects: List[str] = Field(default_factory=list, description="Enrolled subjects")
    contact_email: Optional[EmailStr] = None
    tutor_id: Optional[str] = Field(None, description="Linked tutor ID if any")

class Class(BaseModel):
    subject: str = Field(..., description="Subject name")
    grade: int = Field(..., ge=11, le=12)
    tutor_id: str = Field(..., description="Tutor in charge")
    student_ids: List[str] = Field(default_factory=list, description="Students in class")
    schedule: List[str] = Field(default_factory=list, description="Schedule entries e.g., Mon-10:00")

class Vacancy(BaseModel):
    institution_id: str = Field(..., description="Institution posting the vacancy")
    subject: str = Field(..., description="Subject")
    grade: int = Field(..., ge=11, le=12)
    description: Optional[str] = None
    status: str = Field(default="open", description="open|closed")

class Attendance(BaseModel):
    class_id: str
    student_id: str
    status: str = Field(..., description="present|absent|late")
    method: Optional[str] = Field(None, description="qr|face|manual")
    token: Optional[str] = Field(None, description="QR token used (if any)")

class Reward(BaseModel):
    student_id: str
    points: int = Field(..., ge=0)
    badge: Optional[str] = None
    reason: Optional[str] = None

class LiveSession(BaseModel):
    class_id: str
    tutor_id: str
    topic: str
    platform: str = Field(default="yt", description="yt|webrtc")

# Legacy examples (kept for reference)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
