import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents

app = FastAPI(title="Maatram KK360 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Maatram KK360 Backend running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from Maatram KK360 API"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    # Final env checks
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# ----- Basic feature endpoints (minimal working versions) -----

class ConnectTutorRequest(BaseModel):
    student_id: str
    tutor_id: str

@app.post("/api/connect-tutor")
def connect_tutor(payload: ConnectTutorRequest):
    # Link student and tutor via simple document insert (history/audit)
    doc_id = create_document("connection", payload.model_dump())
    return {"status": "ok", "connection_id": doc_id}

class VacancyCreate(BaseModel):
    institution_id: str
    subject: str
    grade: int
    description: str | None = None

@app.post("/api/vacancies")
def create_vacancy(v: VacancyCreate):
    doc_id = create_document("vacancy", v.model_dump())
    return {"status": "ok", "id": doc_id}

@app.get("/api/vacancies")
def list_vacancies():
    docs = get_documents("vacancy", {})
    # Convert ObjectId to string if present
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])
    return {"items": docs}

class AttendanceMark(BaseModel):
    class_id: str
    student_id: str
    method: str | None = None
    status: str = "present"
    token: str | None = None

@app.post("/api/attendance")
def mark_attendance(a: AttendanceMark):
    doc_id = create_document("attendance", a.model_dump())
    return {"status": "ok", "attendance_id": doc_id}

class LiveSessionCreate(BaseModel):
    class_id: str
    tutor_id: str
    topic: str
    platform: str = "yt"  # yt|webrtc

@app.post("/api/live-session")
def create_live_session(s: LiveSessionCreate):
    # For yt platform we create a placeholder streaming link (simulated)
    if s.platform == "yt":
        live_url = f"https://youtube.com/live/{s.class_id}-{s.tutor_id}"
    else:
        # Placeholder WebRTC room link
        live_url = f"https://webrtc.example/room/{s.class_id}-{s.tutor_id}"
    data = s.model_dump() | {"live_url": live_url}
    doc_id = create_document("live_session", data)
    return {"status": "ok", "id": doc_id, "live_url": live_url}

# Simple AI Scheduler stub endpoint
class ScheduleRequest(BaseModel):
    tutor_availability: list[str]
    student_preferences: list[str]
    subjects: list[str]

@app.post("/api/ai-schedule")
def ai_schedule(req: ScheduleRequest):
    # Simple heuristic: intersect availability and preferences; pair with subjects sequentially
    slots = []
    for slot in req.tutor_availability:
        if slot in req.student_preferences:
            slots.append(slot)
    schedule = [{"slot": s, "subject": req.subjects[i % len(req.subjects)]} for i, s in enumerate(slots)]
    return {"schedule": schedule}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
