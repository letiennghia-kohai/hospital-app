"""
Appointment Service
Business logic for appointment scheduling and alerts
"""
from typing import List, Optional
from datetime import date, datetime, timedelta
from sqlalchemy.orm import joinedload
from sqlalchemy import and_, or_
from database.models import Appointment, Patient, Visit
from database.db_manager import get_db_manager
import config


class AppointmentService:
    """Service class for appointment operations"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    def create_appointment(self, patient_id: int, appointment_date: date,
                          visit_id: int = None, reason: str = None,
                          notes: str = None) -> Appointment:
        """Create a new appointment"""
        with self.db_manager.session_scope() as session:
            appointment = Appointment(
                patient_id=patient_id,
                visit_id=visit_id,
                appointment_date=appointment_date,
                reason=reason,
                status="PENDING",
                notes=notes
            )
            session.add(appointment)
            session.flush()
            session.refresh(appointment)
            return appointment
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Appointment]:
        """Get appointment by ID"""
        session = self.db_manager.get_session()
        try:
            return session.query(Appointment)\
                .options(joinedload(Appointment.patient))\
                .filter(Appointment.id == appointment_id)\
                .first()
        finally:
            session.close()
    
    def get_patient_appointments(self, patient_id: int, include_completed: bool = False) -> List[Appointment]:
        """Get all appointments for a patient"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Appointment)\
                .filter(Appointment.patient_id == patient_id)
            
            if not include_completed:
                query = query.filter(Appointment.status != "COMPLETED")
            
            return query.order_by(Appointment.appointment_date.desc()).all()
        finally:
            session.close()
    
    def get_appointments_by_date(self, target_date: date) -> List[Appointment]:
        """Get all appointments for a specific date"""
        session = self.db_manager.get_session()
        try:
            return session.query(Appointment)\
                .options(joinedload(Appointment.patient))\
                .filter(Appointment.appointment_date == target_date)\
                .filter(Appointment.status != "CANCELLED")\
                .order_by(Appointment.patient_id)\
                .all()
        finally:
            session.close()
    
    def get_appointments_by_date_range(self, start_date: date, end_date: date) -> List[Appointment]:
        """Get appointments within a date range"""
        session = self.db_manager.get_session()
        try:
            return session.query(Appointment)\
                .options(joinedload(Appointment.patient))\
                .filter(and_(
                    Appointment.appointment_date >= start_date,
                    Appointment.appointment_date <= end_date
                ))\
                .filter(Appointment.status != "CANCELLED")\
                .order_by(Appointment.appointment_date)\
                .all()
        finally:
            session.close()
    
    def get_overdue_appointments(self) -> List[Appointment]:
        """
        Get all overdue appointments (past date and still PENDING)
        This is used for dashboard alerts
        """
        session = self.db_manager.get_session()
        try:
            today = date.today()
            
            # Get pending appointments that are past due
            overdue = session.query(Appointment)\
                .options(joinedload(Appointment.patient))\
                .filter(and_(
                    Appointment.appointment_date < today,
                    Appointment.status == "PENDING"
                ))\
                .order_by(Appointment.appointment_date)\
                .all()
            
            # Auto-update status to OVERDUE
            for appointment in overdue:
                appointment.status = "OVERDUE"
            
            session.commit()
            
            return overdue
        finally:
            session.close()
    
    def get_upcoming_appointments(self, days: int = 7) -> List[Appointment]:
        """Get upcoming appointments within next N days"""
        session = self.db_manager.get_session()
        try:
            today = date.today()
            end_date = today + timedelta(days=days)
            
            return session.query(Appointment)\
                .options(joinedload(Appointment.patient))\
                .filter(and_(
                    Appointment.appointment_date >= today,
                    Appointment.appointment_date <= end_date,
                    or_(
                        Appointment.status == "PENDING",
                        Appointment.status == "OVERDUE"
                    )
                ))\
                .order_by(Appointment.appointment_date)\
                .all()
        finally:
            session.close()
    
    def update_appointment(self, appointment_id: int, **kwargs) -> Optional[Appointment]:
        """Update appointment"""
        with self.db_manager.session_scope() as session:
            appointment = session.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                for key, value in kwargs.items():
                    if hasattr(appointment, key):
                        setattr(appointment, key, value)
                session.flush()
                session.refresh(appointment)
                return appointment
            return None
    
    def mark_as_completed(self, appointment_id: int, visit_id: int = None) -> Optional[Appointment]:
        """Mark appointment as completed"""
        update_data = {"status": "COMPLETED"}
        if visit_id:
            update_data["visit_id"] = visit_id
        return self.update_appointment(appointment_id, **update_data)
    
    def mark_as_cancelled(self, appointment_id: int) -> Optional[Appointment]:
        """Mark appointment as cancelled"""
        return self.update_appointment(appointment_id, status="CANCELLED")
    
    def delete_appointment(self, appointment_id: int) -> bool:
        """Delete an appointment"""
        with self.db_manager.session_scope() as session:
            appointment = session.query(Appointment).filter(Appointment.id == appointment_id).first()
            if appointment:
                session.delete(appointment)
                return True
            return False
    
    def get_overdue_count(self) -> int:
        """Get count of overdue appointments"""
        overdue = self.get_overdue_appointments()
        return len(overdue)
