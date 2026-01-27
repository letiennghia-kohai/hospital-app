"""
Test Service
Business logic for test types and test results management
"""
from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import joinedload
from sqlalchemy import and_
from database.models import TestType, TestResult, Visit
from database.db_manager import get_db_manager


class TestService:
    """Service class for test operations"""
    
    def __init__(self):
        self.db_manager = get_db_manager()
    
    # ===== Test Type Management =====
    
    def create_test_type(self, name: str, category: str = None,
                        unit: str = None, normal_range_min: float = None,
                        normal_range_max: float = None, description: str = None) -> TestType:
        """Create a new test type"""
        with self.db_manager.session_scope() as session:
            test_type = TestType(
                name=name,
                category=category,
                unit=unit,
                normal_range_min=normal_range_min,
                normal_range_max=normal_range_max,
                description=description
            )
            session.add(test_type)
            session.flush()
            session.refresh(test_type)
            return test_type
    
    def get_test_type_by_id(self, test_type_id: int) -> Optional[TestType]:
        """Get test type by ID"""
        session = self.db_manager.get_session()
        try:
            return session.query(TestType).filter(TestType.id == test_type_id).first()
        finally:
            session.close()
    
    def get_test_type_by_name(self, name: str) -> Optional[TestType]:
        """Get test type by name"""
        session = self.db_manager.get_session()
        try:
            return session.query(TestType).filter(TestType.name == name).first()
        finally:
            session.close()
    
    def get_all_test_types(self) -> List[TestType]:
        """Get all test types"""
        session = self.db_manager.get_session()
        try:
            return session.query(TestType).order_by(TestType.category, TestType.name).all()
        finally:
            session.close()
    
    def get_test_types_by_category(self, category: str) -> List[TestType]:
        """Get test types by category"""
        session = self.db_manager.get_session()
        try:
            return session.query(TestType)\
                .filter(TestType.category == category)\
                .order_by(TestType.name)\
                .all()
        finally:
            session.close()
    
    def update_test_type(self, test_type_id: int, **kwargs) -> Optional[TestType]:
        """Update test type"""
        with self.db_manager.session_scope() as session:
            test_type = session.query(TestType).filter(TestType.id == test_type_id).first()
            if test_type:
                for key, value in kwargs.items():
                    if hasattr(test_type, key):
                        setattr(test_type, key, value)
                session.flush()
                session.refresh(test_type)
                return test_type
            return None
    
    def delete_test_type(self, test_type_id: int) -> bool:
        """Delete a test type"""
        with self.db_manager.session_scope() as session:
            test_type = session.query(TestType).filter(TestType.id == test_type_id).first()
            if test_type:
                session.delete(test_type)
                return True
            return False
    
    # ===== Test Result Management =====
    
    def create_test_result(self, visit_id: int, test_type_id: int,
                          test_date: date, result_value: float = None,
                          result_text: str = None, unit: str = None,
                          notes: str = None) -> TestResult:
        """Create a new test result"""
        with self.db_manager.session_scope() as session:
            test_result = TestResult(
                visit_id=visit_id,
                test_type_id=test_type_id,
                test_date=test_date,
                result_value=result_value,
                result_text=result_text,
                unit=unit,
                notes=notes
            )
            session.add(test_result)
            session.flush()
            session.refresh(test_result)
            return test_result
    
    def get_test_result_by_id(self, result_id: int) -> Optional[TestResult]:
        """Get test result by ID"""
        session = self.db_manager.get_session()
        try:
            return session.query(TestResult)\
                .options(joinedload(TestResult.test_type))\
                .filter(TestResult.id == result_id)\
                .first()
        finally:
            session.close()
    
    def get_visit_test_results(self, visit_id: int) -> List[TestResult]:
        """Get all test results for a visit"""
        session = self.db_manager.get_session()
        try:
            return session.query(TestResult)\
                .options(joinedload(TestResult.test_type))\
                .filter(TestResult.visit_id == visit_id)\
                .order_by(TestResult.test_date.desc())\
                .all()
        finally:
            session.close()
    
    def update_test_result(self, result_id: int, **kwargs) -> Optional[TestResult]:
        """Update test result"""
        with self.db_manager.session_scope() as session:
            result = session.query(TestResult).filter(TestResult.id == result_id).first()
            if result:
                for key, value in kwargs.items():
                    if hasattr(result, key):
                        setattr(result, key, value)
                session.flush()
                session.refresh(result)
                return result
            return None
    
    def delete_test_result(self, result_id: int) -> bool:
        """Delete a test result"""
        with self.db_manager.session_scope() as session:
            result = session.query(TestResult).filter(TestResult.id == result_id).first()
            if result:
                session.delete(result)
                return True
            return False
    
    # ===== Timeline Queries (Key Feature) =====
    
    def get_patient_test_timeline(self, patient_id: int, test_type_id: int,
                                  start_date: date = None, end_date: date = None) -> List[Dict[str, Any]]:
        """
        Get timeline of a specific test for a patient
        Returns list of dicts with date and value for easy charting
        """
        session = self.db_manager.get_session()
        try:
            query = session.query(TestResult, Visit)\
                .join(Visit, TestResult.visit_id == Visit.id)\
                .filter(and_(
                    Visit.patient_id == patient_id,
                    TestResult.test_type_id == test_type_id
                ))
            
            if start_date:
                query = query.filter(TestResult.test_date >= start_date)
            if end_date:
                query = query.filter(TestResult.test_date <= end_date)
            
            results = query.order_by(TestResult.test_date.asc()).all()
            
            # Format for easy display/charting
            timeline = []
            for test_result, visit in results:
                timeline.append({
                    'date': test_result.test_date,
                    'value': test_result.result_value,
                    'text': test_result.result_text,
                    'unit': test_result.unit,
                    'visit_id': visit.id,
                    'notes': test_result.notes
                })
            
            return timeline
        finally:
            session.close()
    
    def get_patient_all_tests_latest(self, patient_id: int) -> List[Dict[str, Any]]:
        """
        Get the latest result for each test type for a patient
        Useful for dashboard/summary view
        """
        session = self.db_manager.get_session()
        try:
            # Get all test results for patient
            results = session.query(TestResult, Visit, TestType)\
                .join(Visit, TestResult.visit_id == Visit.id)\
                .join(TestType, TestResult.test_type_id == TestType.id)\
                .filter(Visit.patient_id == patient_id)\
                .order_by(TestResult.test_date.desc())\
                .all()
            
            # Get latest for each test type
            latest_by_type = {}
            for test_result, visit, test_type in results:
                if test_type.id not in latest_by_type:
                    latest_by_type[test_type.id] = {
                        'test_name': test_type.name,
                        'test_category': test_type.category,
                        'date': test_result.test_date,
                        'value': test_result.result_value,
                        'text': test_result.result_text,
                        'unit': test_result.unit or test_type.unit,
                        'normal_min': test_type.normal_range_min,
                        'normal_max': test_type.normal_range_max
                    }
            
            return list(latest_by_type.values())
        finally:
            session.close()
