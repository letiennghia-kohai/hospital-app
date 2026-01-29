"""
Visit Service
Business logic for visit/examination management
"""
from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import joinedload
from database.models import Visit, Patient
from database.db_manager import get_db_manager


class VisitService:
    """Service class for visit operations"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    def create_visit(self, patient_id: int, visit_date: date,
                     symptoms: str = None, diagnosis: str = None,
                     conclusion: str = None, notes: str = None) -> Visit:
        """Create a new visit"""
        session = self.db_manager.get_session()
        try:
            new_visit = Visit(
                patient_id=patient_id,
                visit_date=visit_date,
                symptoms=symptoms,
                diagnosis=diagnosis,
                conclusion=conclusion,
                notes=notes
            )
            session.add(new_visit)
            session.commit()
            
            # Get the visit ID before closing session
            visit_id = new_visit.id
            session.close()
            
            # Return fresh visit with eager loaded patient
            return self.get_visit_by_id(visit_id)
        except Exception as e:
            session.rollback()
            raise e
        finally:
            if session.is_active:
                session.close()
    
    def get_visit_by_id(self, visit_id: int) -> Optional[Visit]:
        """Get visit by ID with related data"""
        session = self.db_manager.get_session()
        try:
            return session.query(Visit)\
                .options(
                    joinedload(Visit.patient),
                    joinedload(Visit.test_results),
                    joinedload(Visit.prescriptions)
                )\
                .filter(Visit.id == visit_id)\
                .first()
        finally:
            session.close()
    
    def update_visit(self, visit_id: int, **kwargs) -> Optional[Visit]:
        """Update visit information"""
        with self.db_manager.session_scope() as session:
            visit = session.query(Visit).filter(Visit.id == visit_id).first()
            if visit:
                for key, value in kwargs.items():
                    if hasattr(visit, key):
                        setattr(visit, key, value)
                session.flush()
                session.refresh(visit)
                return visit
            return None
    
    def delete_visit(self, visit_id: int) -> bool:
        """Delete a visit"""
        with self.db_manager.session_scope() as session:
            visit = session.query(Visit).filter(Visit.id == visit_id).first()
            if visit:
                session.delete(visit)
                return True
            return False
    
    def get_patient_visits(self, patient_id: int, limit: int = 100) -> List[Visit]:
        """Get all visits for a specific patient"""
        session = self.db_manager.get_session()
        try:
            return session.query(Visit)\
                .filter(Visit.patient_id == patient_id)\
                .order_by(Visit.visit_date.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def get_recent_visits(self, limit: int = 50) -> List[Visit]:
        """Get recent visits across all patients"""
        session = self.db_manager.get_session()
        try:
            return session.query(Visit)\
                .options(joinedload(Visit.patient))\
                .order_by(Visit.visit_date.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def get_visits_by_date_range(self, start_date: date, end_date: date) -> List[Visit]:
        """Get visits within a date range"""
        session = self.db_manager.get_session()
        try:
            return session.query(Visit)\
                .options(joinedload(Visit.patient))\
                .filter(Visit.visit_date >= start_date)\
                .filter(Visit.visit_date <= end_date)\
                .order_by(Visit.visit_date.desc())\
                .all()
        finally:
            session.close()
    
    def get_visit_count(self) -> int:
        """Get total number of visits"""
        session = self.db_manager.get_session()
        try:
            return session.query(Visit).count()
        finally:
            session.close()
    
    def get_patient_last_visit(self, patient_id: int) -> Optional[Visit]:
        """Get the most recent visit for a patient"""
        session = self.db_manager.get_session()
        try:
            return session.query(Visit)\
                .filter(Visit.patient_id == patient_id)\
                .order_by(Visit.visit_date.desc())\
                .first()
        finally:
            session.close()
