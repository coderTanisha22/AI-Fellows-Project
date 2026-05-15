from fastapi import APIRouter, HTTPException, Query
from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

from ..services.alert_service import (
    get_alerts_data,
    get_dashboard_data,
    get_simulation_status,
    resolve_alert,
    seed_demo_alert,
)
from ..services.gemini_client import get_gemini_runtime_status
from ..services.simulator import simulator
from ..services.auth_service import (
    authenticate_user,
    generate_session_token,
    validate_session_token,
    get_demo_user,
)

router = APIRouter()

# ============ VALIDATION MODELS ============

class AlertActionRequest(BaseModel):
    alert_id: str = Field(..., description="ID of the alert to act on")
    action: str = Field(..., pattern="^(approve|reject|snooze)$", description="Action to take on alert")


class ActivityIngestionRequest(BaseModel):
    resident_id: str = Field(..., description="ID of the resident")
    activity_level: float = Field(..., ge=0, le=100, description="Activity level 0-100")
    location: Optional[str] = Field(None, description="Location of activity")
    activity_type: Optional[str] = Field(None, description="Type of activity")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class InsightRequest(BaseModel):
    resident_id: Optional[str] = None
    days_back: int = Field(default=1, ge=1, le=30)


# ============ AUTH MODELS ============

class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    token: str
    user: dict


# ============ ROUTES ============

def validate_role(role: str) -> str:
    """Validate and normalize role parameter"""
    valid_roles = {"caregiver", "supervisor", "family"}
    role = role.lower()
    if role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    return role


# ============ AUTH ENDPOINTS ============

@router.post("/auth/login")
def login(request: LoginRequest):
    """Authenticate user and return session token"""
    try:
        user = authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        token = generate_session_token(user["id"])
        return {
            "token": token,
            "user": user
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/auth/current-user")
def get_current_user(authorization: str = Header(None)):
    """Get current authenticated user"""
    try:
        if not authorization:
            # Return demo user for unauthenticated access
            return get_demo_user("caregiver")
        
        # Extract token from "Bearer <token>"
        parts = authorization.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            return get_demo_user("caregiver")
        
        token = parts[1]
        user = validate_session_token(token)
        if not user:
            return get_demo_user("caregiver")
        
        return user
    except Exception:
        return get_demo_user("caregiver")


@router.post("/auth/logout")
def logout():
    """Logout current user"""
    return {"success": True, "message": "Logged out successfully"}


@router.get("/activity")
def get_activity(role: str = Query("caregiver", description="User role")):
    """Get activity timeline and status for a user role"""
    try:
        role = validate_role(role)
        data = get_dashboard_data(role=role)
        return {
            "timeline": data["activity"],
            "status": data["status"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
def get_alerts(role: str = Query("caregiver", description="User role")):
    """Get alerts filtered by user role"""
    try:
        role = validate_role(role)
        alerts = get_alerts_data(role=role)
        return [
            {
                "id": alert["id"],
                "title": alert["title"],
                "time": alert["time"],
                "severity": alert["severity"],
                "confidence": alert["confidence"],
                "type": alert["type"],
                "summary": alert["summary"],
                "explanation": alert["explanation"],
                "status": alert["status"],
            }
            for alert in alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insight")
def get_insight(role: str = Query("caregiver", description="User role")):
    """Get AI-generated insight about recent activity"""
    try:
        role = validate_role(role)
        data = get_dashboard_data(role=role)
        explanation = data.get("explanation")

        if isinstance(explanation, dict):
            return {
                "summary": explanation.get("summary", explanation.get("explanation", "No issues detected")),
                "confidence": explanation.get("confidence", 0.85),
            }

        return {
            "summary": "Recent activity appears to be within the expected routine, with no notable behavioral changes detected in the latest monitoring window.",
            "confidence": 0.85
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
def get_dashboard(role: str = Query("caregiver", description="User role")):
    """Get complete dashboard data for a user role"""
    try:
        role = validate_role(role)
        return get_dashboard_data(role=role)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/action")
def handle_alert_action(payload: AlertActionRequest):
    """Handle alert action (approve/reject/snooze)"""
    try:
        return resolve_alert(payload.alert_id, payload.action)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alerts/demo/seed")
def create_demo_alert(role: str = Query("supervisor", description="User role")):
    """Create a demo alert (supervisor only)"""
    try:
        role = validate_role(role)
        if role != "supervisor":
            raise HTTPException(
                status_code=403,
                detail="Only supervisors can create demo alerts"
            )
        
        alert = seed_demo_alert(role=role)
        return {
            "id": alert["id"],
            "title": alert["title"],
            "time": alert["time"],
            "severity": alert["severity"],
            "confidence": alert["confidence"],
            "type": alert["type"],
            "summary": alert["summary"],
            "explanation": alert["explanation"],
            "status": alert["status"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/activity")
def ingest_activity(data: ActivityIngestionRequest):
    """Ingest real activity data from IoT sensors or external sources"""
    try:
        # Validate input
        if not data.resident_id:
            raise HTTPException(status_code=400, detail="resident_id is required")
        
        if not 0 <= data.activity_level <= 100:
            raise HTTPException(status_code=400, detail="activity_level must be between 0 and 100")
        
        # In production, this would save to database
        # For now, we'll simulate ingestion
        simulator.add_activity_event({
            "resident_id": data.resident_id,
            "activity_level": data.activity_level,
            "location": data.location or "unknown",
            "activity_type": data.activity_type or "movement",
            "timestamp": data.timestamp.isoformat() if data.timestamp else datetime.utcnow().isoformat()
        })
        
        return {
            "success": True,
            "message": "Activity data ingested successfully",
            "resident_id": data.resident_id,
            "timestamp": data.timestamp or datetime.utcnow()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ingest/batch")
def get_ingest_batch_template():
    """Get template for batch ingestion"""
    return {
        "description": "Template for batch activity ingestion",
        "template": {
            "resident_id": "resident_123",
            "activities": [
                {
                    "activity_level": 45.5,
                    "location": "bedroom",
                    "activity_type": "sleep",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ]
        },
        "endpoint": "/ingest/batch",
        "method": "POST"
    }


@router.post("/simulate/start")
async def start_simulation():
    """Start the activity simulator"""
    try:
        return await simulator.start()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate/stop")
async def stop_simulation():
    """Stop the activity simulator"""
    try:
        return await simulator.stop()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
def health_check():
    """Health check endpoint"""
    sim_status = simulator.status()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "simulator_running": sim_status.get("running", False)
    }


@router.get("/simulate/status")
def simulation_status():
    return get_simulation_status()


@router.get("/gemini/status")
def gemini_status():
    return get_gemini_runtime_status()
