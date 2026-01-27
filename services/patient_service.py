"""
Patient Service
Business logic for patient management
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy.orm import Session
from database.models import Patient
from database.db_manager import get_db_manager


class PatientService:
    """Service class for patient operations"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    def create_patient(self, patient_code: str, full_name: str, 
                      date_of_birth=None, gender=None, 
                      phone_number=None, address=None, notes=None) -> Patient:
        """Create a new patient"""
        with self.db_manager.session_scope() as session:
            patient = Patient(
                patient_code=patient_code,
                full_name=full_name,
                date_of_birth=date_of_birth,
                gender=gender,
                phone_number=phone_number,
                address=address,
                notes=notes
            )
            session.add(patient)
            session.flush()
            session.refresh(patient)
            return patient
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        session = self.db_manager.get_session()
        try:
            return session.query(Patient).filter(Patient.id == patient_id).first()
        finally:
            session.close()
    
    def get_patient_by_code(self, patient_code: str) -> Optional[Patient]:
        """Get patient by patient code"""
        session = self.db_manager.get_session()
        try:
            return session.query(Patient).filter(Patient.patient_code == patient_code).first()
        finally:
            session.close()
    
    def update_patient(self, patient_id: int, **kwargs) -> Optional[Patient]:
        """Update patient information"""
        with self.db_manager.session_scope() as session:
            patient = session.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                for key, value in kwargs.items():
                    if hasattr(patient, key):
                        setattr(patient, key, value)
                patient.updated_at = datetime.now()
                session.flush()
                session.refresh(patient)
                return patient
            return None
    
    def delete_patient(self, patient_id: int) -> bool:
        """Delete a patient"""
        with self.db_manager.session_scope() as session:
            patient = session.query(Patient).filter(Patient.id == patient_id).first()
            if patient:
                session.delete(patient)
                return True
            return False
    
    def search_patients(self, keyword: str = "", limit: int = 100) -> List[Patient]:
        """
        Search patients by name, phone, or patient code
        Returns list of matching patients
        """
        session = self.db_manager.get_session()
        try:
            query = session.query(Patient)
            
            if keyword:
                search_pattern = f"%{keyword}%"
                query = query.filter(
                    or_(
                        Patient.full_name.like(search_pattern),
                        Patient.phone_number.like(search_pattern),
                        Patient.patient_code.like(search_pattern)
                    )
                )
            
            return query.order_by(Patient.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_all_patients(self, limit: int = 1000) -> List[Patient]:
        """Get all patients"""
        session = self.db_manager.get_session()
        try:
            return session.query(Patient).order_by(Patient.created_at.desc()).limit(limit).all()
        finally:
            session.close()
    
    def generate_patient_code(self) -> str:
        """Generate a unique patient code"""
        session = self.db_manager.get_session()
        try:
            # Get the latest patient
            latest = session.query(Patient).order_by(Patient.id.desc()).first()
            
            if latest and latest.patient_code.startswith("BN"):
                try:
                    last_number = int(latest.patient_code[2:])
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            
            return f"BN{new_number:06d}"  # BN000001, BN000002, etc.
        finally:
            session.close()
    
    def get_patient_count(self) -> int:
        """Get total number of patients"""
        session = self.db_manager.get_session()
        try:
            return session.query(Patient).count()
        finally:
            session.close()
