import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

# Use SQLite by default, can be overridden with DATABASE_URL env var
database_url = os.getenv("DATABASE_URL", "sqlite:///./caring_ai.db")

# For SQLite, add check_same_thread=False
if database_url.startswith("sqlite"):
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
else:
    engine = create_engine(database_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class AnomalyType(str, enum.Enum):
    INACTIVITY = "inactivity"
    PATTERN_CHANGE = "pattern_change"
    ERRATIC_BEHAVIOR = "erratic_behavior"
    MISSING_ROUTINE = "missing_routine"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserRole(str, enum.Enum):
    CAREGIVER = "caregiver"
    SUPERVISOR = "supervisor"
    FAMILY = "family"


# ============ MODELS ============

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.CAREGIVER)
    resident_id = Column(String, index=True)  # Who they care for
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Resident(Base):
    __tablename__ = "residents"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer, nullable=True)
    medical_conditions = Column(String, nullable=True)
    emergency_contact = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True, index=True)
    resident_id = Column(String, index=True)
    timestamp = Column(DateTime, index=True)
    activity_level = Column(Float)  # 0-100
    location = Column(String, nullable=True)
    activity_type = Column(String, nullable=True)  # "movement", "sleep", "eating", etc.
    created_at = Column(DateTime, default=datetime.utcnow)


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(String, primary_key=True, index=True)
    resident_id = Column(String, index=True)
    anomaly_type = Column(SQLEnum(AnomalyType), index=True)
    confidence = Column(Float)  # 0-1
    timestamp = Column(DateTime, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, index=True)
    resident_id = Column(String, index=True)
    anomaly_id = Column(String, index=True)
    alert_type = Column(SQLEnum(AnomalyType))
    severity = Column(SQLEnum(AlertSeverity))
    summary = Column(String)
    explanation = Column(String)
    confidence = Column(Float)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)  # User ID


class AlertAction(Base):
    __tablename__ = "alert_actions"

    id = Column(String, primary_key=True, index=True)
    alert_id = Column(String, index=True)
    user_id = Column(String, index=True)
    action = Column(String)  # "approve", "reject", "snooze"
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Dependency for FastAPI to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully")
