"""
Import Service
Business logic for importing data from CSV/Excel files
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import pandas as pd
from datetime import datetime
from services.patient_service import PatientService
from services.test_service import TestService
import config


class ImportService:
    """Service class for data import operations"""
    
    def __init__(self):
        self.patient_service = PatientService()
        self.test_service = TestService()
    
    def read_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Read CSV or Excel file and return DataFrame
        Returns None if file cannot be read
        """
        try:
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            elif file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            return df
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def get_column_names(self, file_path: str) -> List[str]:
        """Get list of column names from file"""
        df = self.read_file(file_path)
        if df is not None:
            return df.columns.tolist()
        return []
    
    def preview_data(self, file_path: str, rows: int = 10) -> Optional[pd.DataFrame]:
        """Preview first N rows of data"""
        df = self.read_file(file_path)
        if df is not None:
            return df.head(rows)
        return None
    
    def import_patients(self, file_path: str, column_mapping: Dict[str, str],
                       skip_duplicates: bool = True) -> Dict[str, Any]:
        """
        Import patients from file
        
        Args:
            file_path: Path to CSV/Excel file
            column_mapping: Dict mapping file columns to patient fields
                Example: {
                    'patient_code': 'Mã BN',
                    'full_name': 'Họ tên',
                    'date_of_birth': 'Ngày sinh',
                    'gender': 'Giới tính',
                    'phone_number': 'SĐT',
                    'address': 'Địa chỉ',
                    'notes': 'Ghi chú'
                }
            skip_duplicates: Skip patients with existing patient_code
        
        Returns:
            Dict with import statistics
        """
        df = self.read_file(file_path)
        if df is None:
            return {'success': False, 'error': 'Cannot read file'}
        
        # Reverse mapping for easier lookup
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        
        stats = {
            'total': len(df),
            'imported': 0,
            'skipped': 0,
            'errors': []
        }
        
        for idx, row in df.iterrows():
            try:
                # Extract patient data
                patient_data = {}
                
                for file_col, field_name in reverse_mapping.items():
                    if file_col in row and pd.notna(row[file_col]):
                        value = row[file_col]
                        
                        # Handle date conversion
                        if field_name == 'date_of_birth' and value:
                            try:
                                if isinstance(value, str):
                                    value = pd.to_datetime(value, dayfirst=True, errors='coerce').date()
                                elif isinstance(value, pd.Timestamp):
                                    value = value.date()
                            except:
                                value = None
                        
                        patient_data[field_name] = value
                
                # Check required fields
                if 'patient_code' not in patient_data or 'full_name' not in patient_data:
                    stats['errors'].append(f"Row {idx + 1}: Missing required fields")
                    stats['skipped'] += 1
                    continue
                
                # Check for duplicates
                if skip_duplicates:
                    existing = self.patient_service.get_patient_by_code(patient_data['patient_code'])
                    if existing:
                        stats['skipped'] += 1
                        continue
                
                # Create patient
                self.patient_service.create_patient(**patient_data)
                stats['imported'] += 1
                
            except Exception as e:
                stats['errors'].append(f"Row {idx + 1}: {str(e)}")
                stats['skipped'] += 1
        
        stats['success'] = True
        return stats
    
    def import_test_results(self, file_path: str, column_mapping: Dict[str, str],
                           patient_id: int, visit_id: int) -> Dict[str, Any]:
        """
        Import test results for a specific visit
        
        Args:
            file_path: Path to CSV/Excel file
            column_mapping: Dict mapping file columns to test result fields
                Example: {
                    'test_name': 'Tên xét nghiệm',
                    'result_value': 'Kết quả',
                    'unit': 'Đơn vị',
                    'test_date': 'Ngày XN'
                }
            patient_id: Patient ID
            visit_id: Visit ID
        
        Returns:
            Dict with import statistics
        """
        df = self.read_file(file_path)
        if df is None:
            return {'success': False, 'error': 'Cannot read file'}
        
        reverse_mapping = {v: k for k, v in column_mapping.items()}
        
        stats = {
            'total': len(df),
            'imported': 0,
            'skipped': 0,
            'errors': []
        }
        
        for idx, row in df.iterrows():
            try:
                # Extract test result data
                test_name = None
                result_value = None
                result_text = None
                unit = None
                test_date = None
                notes = None
                
                for file_col, field_name in reverse_mapping.items():
                    if file_col in row and pd.notna(row[file_col]):
                        value = row[file_col]
                        
                        if field_name == 'test_name':
                            test_name = str(value)
                        elif field_name == 'result_value':
                            try:
                                result_value = float(value)
                            except:
                                result_text = str(value)
                        elif field_name == 'unit':
                            unit = str(value)
                        elif field_name == 'test_date':
                            try:
                                if isinstance(value, str):
                                    test_date = pd.to_datetime(value).date()
                                elif isinstance(value, pd.Timestamp):
                                    test_date = value.date()
                            except:
                                test_date = None
                        elif field_name == 'notes':
                            notes = str(value)
                
                # Validate required fields
                if not test_name:
                    stats['errors'].append(f"Row {idx + 1}: Missing test name")
                    stats['skipped'] += 1
                    continue
                
                # Get or create test type
                test_type = self.test_service.get_test_type_by_name(test_name)
                if not test_type:
                    test_type = self.test_service.create_test_type(
                        name=test_name,
                        unit=unit
                    )
                
                # Use visit date if test_date not provided
                if not test_date:
                    from services.visit_service import VisitService
                    visit_service = VisitService()
                    visit = visit_service.get_visit_by_id(visit_id)
                    test_date = visit.visit_date if visit else datetime.now().date()
                
                # Create test result
                self.test_service.create_test_result(
                    visit_id=visit_id,
                    test_type_id=test_type.id,
                    test_date=test_date,
                    result_value=result_value,
                    result_text=result_text,
                    unit=unit,
                    notes=notes
                )
                
                stats['imported'] += 1
                
            except Exception as e:
                stats['errors'].append(f"Row {idx + 1}: {str(e)}")
                stats['skipped'] += 1
        
        stats['success'] = True
        return stats
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate file before import
        Returns validation results
        """
        result = {
            'valid': False,
            'error': None,
            'row_count': 0,
            'column_count': 0,
            'columns': []
        }
        
        try:
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in config.ALLOWED_IMPORT_EXTENSIONS:
                result['error'] = f"File type {file_ext} not supported"
                return result
            
            # Check file exists
            if not Path(file_path).exists():
                result['error'] = "File does not exist"
                return result
            
            # Read file
            df = self.read_file(file_path)
            if df is None:
                result['error'] = "Cannot read file"
                return result
            
            # Check size
            if len(df) > config.MAX_IMPORT_ROWS:
                result['error'] = f"File too large (max {config.MAX_IMPORT_ROWS} rows)"
                return result
            
            result['valid'] = True
            result['row_count'] = len(df)
            result['column_count'] = len(df.columns)
            result['columns'] = df.columns.tolist()
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def load_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Alias for read_file"""
        return self.read_file(file_path)
    
    def import_medicines(self, file_path: str, column_mapping: dict, 
                        skip_duplicates: bool = True) -> dict:
        """Import medicines from CSV/Excel"""
        from services import MedicineService
        
        try:
            df = self.load_file(file_path)
            if df is None or df.empty:
                return {'success': False, 'error': 'File is empty'}
            
            medicine_service = MedicineService()
            imported, skipped, errors = 0, 0, []
            
            for idx, row in df.iterrows():
                try:
                    data = {}
                    for field, column in column_mapping.items():
                        if column in row.index and pd.notna(row[column]):
                            data[field] = str(row[column]).strip()
                    
                    if 'name' not in data or not data['name']:
                        errors.append(f"Row {idx + 2}: Missing medicine name")
                        continue
                    
                    if skip_duplicates:
                        existing = medicine_service.search_medicines(data['name'], active_only=False)
                        if existing:
                            skipped += 1
                            continue
                    
                    # Map usage/notes to description field
                    description = data.get('usage') or data.get('notes')
                    
                    medicine_service.create_medicine(
                        name=data.get('name'),
                        category=data.get('category'),
                        unit=data.get('unit'),
                        description=description
                    )
                    imported += 1
                except Exception as e:
                    errors.append(f"Row {idx + 2}: {str(e)}")
            
            return {'success': True, 'total': len(df), 'imported': imported, 'skipped': skipped, 'errors': errors}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def import_test_types(self, file_path: str, column_mapping: dict, 
                         skip_duplicates: bool = True) -> dict:
        """Import test types from CSV/Excel"""
        try:
            df = self.load_file(file_path)
            if df is None or df.empty:
                return {'success': False, 'error': 'File is empty'}
            
            imported, skipped, errors = 0, 0, []
            
            for idx, row in df.iterrows():
                try:
                    data = {}
                    for field, column in column_mapping.items():
                        if column in row.index and pd.notna(row[column]):
                            value = row[column]
                            if field in ['normal_range_min', 'normal_range_max']:
                                try:
                                    data[field] = float(value)
                                except:
                                    data[field] = None
                            else:
                                data[field] = str(value).strip()
                    
                    if 'name' not in data or 'unit' not in data:
                        errors.append(f"Row {idx + 2}: Missing name or unit")
                        continue
                    
                    if skip_duplicates:
                        existing = self.test_service.get_test_type_by_name(data['name'])
                        if existing:
                            skipped += 1
                            continue
                    
                    # Map notes to description field
                    description = data.get('notes')
                    
                    self.test_service.create_test_type(
                        name=data.get('name'),
                        unit=data.get('unit'),
                        normal_range_min=data.get('normal_range_min'),
                        normal_range_max=data.get('normal_range_max'),
                        description=description
                    )
                    imported += 1
                except Exception as e:
                    errors.append(f"Row {idx + 2}: {str(e)}")
            
            return {'success': True, 'total': len(df), 'imported': imported, 'skipped': skipped, 'errors': errors}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def import_visits(self, file_path: str, column_mapping: dict) -> dict:
        """Import visits from CSV/Excel"""
        from services import VisitService
        
        try:
            df = self.load_file(file_path)
            if df is None or df.empty:
                return {'success': False, 'error': 'File is empty'}
            
            visit_service = VisitService()
            imported, skipped, errors = 0, 0, []
            
            for idx, row in df.iterrows():
                try:
                    data = {}
                    for field, column in column_mapping.items():
                        if column in row.index and pd.notna(row[column]):
                            value = row[column]
                            if field == 'visit_date':
                                try:
                                    data[field] = pd.to_datetime(value, dayfirst=True, errors='coerce').date()
                                except:
                                    data[field] = None
                            else:
                                data[field] = str(value).strip()
                    
                    if 'patient_code' not in data or 'visit_date' not in data:
                        errors.append(f"Row {idx + 2}: Missing patient_code or visit_date")
                        continue
                    
                    # Get patient by code
                    patient = self.patient_service.get_patient_by_code(data['patient_code'])
                    if not patient:
                        errors.append(f"Row {idx + 2}: Patient {data['patient_code']} not found")
                        continue
                    
                    visit_service.create_visit(
                        patient_id=patient.id,
                        visit_date=data.get('visit_date'),
                        symptoms=data.get('symptoms'),
                        diagnosis=data.get('diagnosis'),
                        conclusion=data.get('conclusion'),
                        notes=data.get('notes')
                    )
                    imported += 1
                except Exception as e:
                    errors.append(f"Row {idx + 2}: {str(e)}")
            
            return {'success': True, 'total': len(df), 'imported': imported, 'skipped': skipped, 'errors': errors}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def import_test_results_batch(self, file_path: str, column_mapping: dict) -> dict:
        """Import test results from CSV/Excel"""
        from services import VisitService
        
        try:
            df = self.load_file(file_path)
            if df is None or df.empty:
                return {'success': False, 'error': 'File is empty'}
            
            visit_service = VisitService()
            imported, skipped, errors = 0, 0, []
            
            for idx, row in df.iterrows():
                try:
                    data = {}
                    for field, column in column_mapping.items():
                        if column in row.index and pd.notna(row[column]):
                            value = row[column]
                            if field == 'test_date':
                                data[field] = pd.to_datetime(value, dayfirst=True, errors='coerce').date()
                            elif field == 'result_value':
                                try:
                                    data[field] = float(value)
                                except:
                                    data['result_text'] = str(value)
                            else:
                                data[field] = str(value).strip()
                    
                    if 'patient_code' not in data or 'test_type_name' not in data:
                        errors.append(f"Row {idx + 2}: Missing required fields")
                        continue
                    
                    # Get patient
                    patient = self.patient_service.get_patient_by_code(data['patient_code'])
                    if not patient:
                        errors.append(f"Row {idx + 2}: Patient {data['patient_code']} not found")
                        continue
                    
                    # Get test type
                    test_type = self.test_service.get_test_type_by_name(data['test_type_name'])
                    if not test_type:
                        errors.append(f"Row {idx + 2}: Test type '{data['test_type_name']}' not found")
                        continue
                    
                    # Get test date
                    test_date = data.get('test_date', datetime.now().date())
                    
                    # Find or create visit for this date
                    # Try to find existing visit on the same date
                    from database.models import Visit
                    from database.db_manager import get_db_manager
                    db_manager = get_db_manager()
                    session = db_manager.get_session()
                    
                    try:
                        visit = session.query(Visit).filter(
                            Visit.patient_id == patient.id,
                            Visit.visit_date == test_date
                        ).first()
                        
                        if not visit:
                            # Create new visit for this test
                            visit = visit_service.create_visit(
                                patient_id=patient.id,
                                visit_date=test_date,
                                symptoms=f"Xét nghiệm {data['test_type_name']}",
                                diagnosis="Xét nghiệm",
                                conclusion="",
                                notes=f"Tự động tạo từ import test results"
                            )
                        
                        # Create test result with visit_id
                        self.test_service.create_test_result(
                            visit_id=visit.id,
                            test_type_id=test_type.id,
                            test_date=test_date,
                            result_value=data.get('result_value'),
                            result_text=data.get('result_text'),
                            unit=test_type.unit,
                            notes=data.get('notes')
                        )
                        imported += 1
                    finally:
                        session.close()
                        
                except Exception as e:
                    errors.append(f"Row {idx + 2}: {str(e)}")
            
            return {'success': True, 'total': len(df), 'imported': imported, 'skipped': skipped, 'errors': errors}
        except Exception as e:
            return {'success': False, 'error': str(e)}
