"""
Medicine Service
Business logic for medicine catalog and prescription management
"""
from typing import List, Optional
from sqlalchemy.orm import joinedload
from database.models import Medicine, Prescription, Visit
from database.db_manager import get_db_manager


class MedicineService:
    """Service class for medicine and prescription operations"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    # ===== Medicine Catalog Management =====
    
    def create_medicine(self, name: str, category: str = None,
                       unit: str = None, description: str = None) -> Medicine:
        """Create a new medicine"""
        session = self.db_manager.get_session()
        try:
            medicine = Medicine(
                name=name,
                category=category,
                unit=unit,
                description=description,
                active=True  # Default to active when creating
            )
            session.add(medicine)
            session.commit()  # CRITICAL: Commit to save to database
            session.refresh(medicine)
            return medicine
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_medicine_by_id(self, medicine_id: int) -> Optional[Medicine]:
        """Get medicine by ID"""
        session = self.db_manager.get_session()
        try:
            return session.query(Medicine).filter(Medicine.id == medicine_id).first()
        finally:
            session.close()
    
    def get_medicine_by_name(self, name: str) -> Optional[Medicine]:
        """Get medicine by name"""
        session = self.db_manager.get_session()
        try:
            return session.query(Medicine).filter(Medicine.name == name).first()
        finally:
            session.close()
    
    def get_all_medicines(self, active_only: bool = True) -> List[Medicine]:
        """Get all medicines"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Medicine)
            if active_only:
                query = query.filter(Medicine.active == True)
            return query.order_by(Medicine.category, Medicine.name).all()
        finally:
            session.close()
    
    def get_medicines_by_category(self, category: str, active_only: bool = True) -> List[Medicine]:
        """Get medicines by category"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Medicine).filter(Medicine.category == category)
            if active_only:
                query = query.filter(Medicine.active == True)
            return query.order_by(Medicine.name).all()
        finally:
            session.close()
    
    def search_medicines(self, keyword: str, active_only: bool = True) -> List[Medicine]:
        """Search medicines by name"""
        session = self.db_manager.get_session()
        try:
            query = session.query(Medicine)
            if keyword:
                query = query.filter(Medicine.name.like(f"%{keyword}%"))
            if active_only:
                query = query.filter(Medicine.active == True)
            return query.order_by(Medicine.name).all()
        finally:
            session.close()
    
    def update_medicine(self, medicine_id: int, **kwargs) -> Optional[Medicine]:
        """Update medicine"""
        with self.db_manager.session_scope() as session:
            medicine = session.query(Medicine).filter(Medicine.id == medicine_id).first()
            if medicine:
                for key, value in kwargs.items():
                    if hasattr(medicine, key):
                        setattr(medicine, key, value)
                session.flush()
                session.refresh(medicine)
                return medicine
            return None
    
    def deactivate_medicine(self, medicine_id: int) -> bool:
        """Deactivate a medicine (soft delete)"""
        return self.update_medicine(medicine_id, active=False) is not None
    
    def delete_medicine(self, medicine_id: int) -> bool:
        """Delete a medicine (hard delete)"""
        with self.db_manager.session_scope() as session:
            medicine = session.query(Medicine).filter(Medicine.id == medicine_id).first()
            if medicine:
                session.delete(medicine)
                return True
            return False
    
    # ===== Prescription Management =====
    
    def create_prescription(self, visit_id: int, medicine_id: int,
                          dosage: str = None, frequency: str = None,
                          duration_days: int = None, notes: str = None) -> Prescription:
        """Create a new prescription"""
        with self.db_manager.session_scope() as session:
            prescription = Prescription(
                visit_id=visit_id,
                medicine_id=medicine_id,
                dosage=dosage,
                frequency=frequency,
                duration_days=duration_days,
                notes=notes
            )
            session.add(prescription)
            session.flush()
            session.refresh(prescription)
            return prescription
    
    def get_prescription_by_id(self, prescription_id: int) -> Optional[Prescription]:
        """Get prescription by ID"""
        session = self.db_manager.get_session()
        try:
            return session.query(Prescription)\
                .options(joinedload(Prescription.medicine))\
                .filter(Prescription.id == prescription_id)\
                .first()
        finally:
            session.close()
    
    def get_visit_prescriptions(self, visit_id: int) -> List[Prescription]:
        """Get all prescriptions for a visit"""
        session = self.db_manager.get_session()
        try:
            return session.query(Prescription)\
                .options(joinedload(Prescription.medicine))\
                .filter(Prescription.visit_id == visit_id)\
                .all()
        finally:
            session.close()
    
    def get_patient_prescriptions(self, patient_id: int, limit: int = 100) -> List[Prescription]:
        """Get all prescriptions for a patient"""
        session = self.db_manager.get_session()
        try:
            return session.query(Prescription)\
                .join(Visit, Prescription.visit_id == Visit.id)\
                .options(joinedload(Prescription.medicine))\
                .filter(Visit.patient_id == patient_id)\
                .order_by(Visit.visit_date.desc())\
                .limit(limit)\
                .all()
        finally:
            session.close()
    
    def update_prescription(self, prescription_id: int, **kwargs) -> Optional[Prescription]:
        """Update prescription"""
        with self.db_manager.session_scope() as session:
            prescription = session.query(Prescription).filter(Prescription.id == prescription_id).first()
            if prescription:
                for key, value in kwargs.items():
                    if hasattr(prescription, key):
                        setattr(prescription, key, value)
                session.flush()
                session.refresh(prescription)
                return prescription
            return None
    
    def delete_prescription(self, prescription_id: int) -> bool:
        """Delete a prescription"""
        with self.db_manager.session_scope() as session:
            prescription = session.query(Prescription).filter(Prescription.id == prescription_id).first()
            if prescription:
                session.delete(prescription)
                return True
            return False
