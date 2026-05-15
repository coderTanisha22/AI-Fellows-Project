import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..db.database import SessionLocal, Activity, Alert, Anomaly, AlertStatus, AlertSeverity, AnomalyType


class ActivityService:
    """Service for persisting activity data to database"""
    
    @staticmethod
    def create_activity(
        resident_id: str,
        activity_level: float,
        location: str = "unknown",
        activity_type: str = "movement"
    ) -> Activity:
        """Create and save an activity record"""
        db = SessionLocal()
        try:
            activity = Activity(
                id=str(uuid.uuid4()),
                resident_id=resident_id,
                timestamp=datetime.utcnow(),
                activity_level=activity_level,
                location=location,
                activity_type=activity_type,
            )
            db.add(activity)
            db.commit()
            db.refresh(activity)
            return activity
        finally:
            db.close()
    
    @staticmethod
    def get_recent_activities(resident_id: str, hours: int = 24) -> List[Activity]:
        """Get recent activities for a resident"""
        db = SessionLocal()
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return db.query(Activity).filter(
                Activity.resident_id == resident_id,
                Activity.timestamp >= cutoff
            ).order_by(desc(Activity.timestamp)).all()
        finally:
            db.close()
    
    @staticmethod
    def get_activity_level_timeline(resident_id: str, hours: int = 24) -> List[float]:
        """Get timeline of activity levels (last N hours)"""
        db = SessionLocal()
        try:
            activities = ActivityService.get_recent_activities(resident_id, hours)
            return [a.activity_level for a in sorted(activities, key=lambda x: x.timestamp)]
        finally:
            db.close()


class AlertService:
    """Service for persisting alerts to database"""
    
    @staticmethod
    def create_alert(
        resident_id: str,
        anomaly_type: str,
        severity: str,
        summary: str,
        explanation: str,
        confidence: float,
        anomaly_id: Optional[str] = None
    ) -> Alert:
        """Create and save an alert"""
        db = SessionLocal()
        try:
            alert = Alert(
                id=str(uuid.uuid4()),
                resident_id=resident_id,
                anomaly_id=anomaly_id or str(uuid.uuid4()),
                alert_type=AnomalyType[anomaly_type.upper().replace(" ", "_")],
                severity=AlertSeverity[severity.upper()],
                summary=summary,
                explanation=explanation,
                confidence=confidence,
                status=AlertStatus.ACTIVE,
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            return alert
        finally:
            db.close()
    
    @staticmethod
    def get_active_alerts(resident_id: str, role: str = "caregiver") -> List[Alert]:
        """Get active alerts, filtered by role"""
        db = SessionLocal()
        try:
            alerts = db.query(Alert).filter(
                Alert.resident_id == resident_id,
                Alert.status == AlertStatus.ACTIVE
            ).order_by(desc(Alert.created_at)).all()
            
            # Role-based filtering
            if role == "family":
                # Family sees only high severity
                alerts = [a for a in alerts if a.severity == AlertSeverity.HIGH]
            
            return alerts
        finally:
            db.close()
    
    @staticmethod
    def resolve_alert(alert_id: str, action: str, user_id: Optional[str] = None) -> dict:
        """Resolve an alert (approve/reject/snooze)"""
        db = SessionLocal()
        try:
            alert = db.query(Alert).filter(Alert.id == alert_id).first()
            if not alert:
                return {"success": False, "error": "Alert not found"}
            
            if action == "approve":
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = user_id
            elif action == "reject":
                alert.status = AlertStatus.DISMISSED
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = user_id
            
            db.commit()
            return {
                "success": True,
                "alert_id": alert_id,
                "action": action,
                "status": alert.status
            }
        finally:
            db.close()


class AnomalyService:
    """Service for persisting anomalies to database"""
    
    @staticmethod
    def create_anomaly(
        resident_id: str,
        anomaly_type: str,
        confidence: float,
        description: str
    ) -> Anomaly:
        """Create and save an anomaly record"""
        db = SessionLocal()
        try:
            anomaly = Anomaly(
                id=str(uuid.uuid4()),
                resident_id=resident_id,
                anomaly_type=AnomalyType[anomaly_type.upper().replace(" ", "_")],
                confidence=confidence,
                description=description,
                timestamp=datetime.utcnow(),
            )
            db.add(anomaly)
            db.commit()
            db.refresh(anomaly)
            return anomaly
        finally:
            db.close()
    
    @staticmethod
    def get_recent_anomalies(resident_id: str, hours: int = 24) -> List[Anomaly]:
        """Get recent anomalies"""
        db = SessionLocal()
        try:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return db.query(Anomaly).filter(
                Anomaly.resident_id == resident_id,
                Anomaly.timestamp >= cutoff
            ).order_by(desc(Anomaly.timestamp)).all()
        finally:
            db.close()
