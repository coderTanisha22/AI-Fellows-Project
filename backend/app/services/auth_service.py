import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict
from pathlib import Path

# Simple file-based user store (demo purposes)
USERS_FILE = Path(__file__).parent.parent.parent / "users.json"

DEFAULT_USERS = [
    {
        "id": "user_caregiver_001",
        "name": "Sarah Johnson",
        "email": "sarah@example.com",
        "role": "caregiver",
        "resident_id": "resident_001",
        "password": "password123",  # In production, use hashed passwords
    },
    {
        "id": "user_supervisor_001",
        "name": "Dr. Michael Chen",
        "email": "michael@example.com",
        "role": "supervisor",
        "resident_id": "resident_001",
        "password": "password123",
    },
    {
        "id": "user_family_001",
        "name": "Emily Johnson",
        "email": "emily@example.com",
        "role": "family",
        "resident_id": "resident_001",
        "password": "password123",
    },
]


def load_users() -> list:
    """Load users from file or create default"""
    if USERS_FILE.exists():
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    else:
        save_users(DEFAULT_USERS)
        return DEFAULT_USERS


def save_users(users: list):
    """Save users to file"""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)


def find_user_by_email(email: str) -> Optional[Dict]:
    """Find user by email"""
    users = load_users()
    for user in users:
        if user.get("email") == email:
            return user
    return None


def find_user_by_id(user_id: str) -> Optional[Dict]:
    """Find user by ID"""
    users = load_users()
    for user in users:
        if user.get("id") == user_id:
            return user
    return None


def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """Authenticate user with email and password"""
    user = find_user_by_email(email)
    if not user:
        return None
    
    # Simple password check (in production, use bcrypt or similar)
    if user.get("password") == password:
        # Return user without password
        user_copy = user.copy()
        del user_copy["password"]
        return user_copy
    
    return None


def generate_session_token(user_id: str) -> str:
    """Generate a simple session token (in production, use JWT)"""
    # Simple implementation: user_id:timestamp:random
    timestamp = datetime.utcnow().isoformat()
    random_id = str(uuid.uuid4())
    return f"{user_id}:{timestamp}:{random_id}"


def validate_session_token(token: str) -> Optional[Dict]:
    """Validate session token and return user"""
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return None
        
        user_id = parts[0]
        timestamp_str = parts[1]
        
        # Check if token is not older than 24 hours
        token_time = datetime.fromisoformat(timestamp_str)
        if datetime.utcnow() - token_time > timedelta(hours=24):
            return None
        
        # Get user from database
        user = find_user_by_id(user_id)
        return user
    except Exception:
        return None


def get_demo_user(role: str = "caregiver") -> Dict:
    """Get a demo user for testing"""
    users = load_users()
    for user in users:
        if user.get("role") == role:
            user_copy = user.copy()
            del user_copy["password"]
            return user_copy
    
    # Fallback
    return {
        "id": "demo_user",
        "name": "Demo User",
        "email": "demo@example.com",
        "role": role,
        "resident_id": "resident_001",
    }
