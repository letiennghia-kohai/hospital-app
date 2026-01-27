"""
Validators
Input validation utilities
"""
import re
from datetime import datetime, date
from typing import Optional


class Validators:
    """Collection of validation functions"""
    
    @staticmethod
    def validate_phone_number(phone: str) -> bool:
        """
        Validate Vietnamese phone number
        Accepts formats: 0123456789, +84123456789, 84123456789
        """
        if not phone:
            return True  # Optional field
        
        # Remove spaces and dashes
        phone = phone.replace(" ", "").replace("-", "")
        
        # Check patterns
        patterns = [
            r'^0\d{9}$',  # 0123456789
            r'^\+84\d{9}$',  # +84123456789
            r'^84\d{9}$'  # 84123456789
        ]
        
        return any(re.match(pattern, phone) for pattern in patterns)
    
    @staticmethod
    def validate_patient_code(code: str) -> bool:
        """Validate patient code format"""
        if not code:
            return False
        
        # Allow alphanumeric codes
        return bool(re.match(r'^[A-Z0-9]{3,20}$', code.upper()))
    
    @staticmethod
    def validate_date(date_str: str, date_format: str = "%d/%m/%Y") -> Optional[date]:
        """
        Validate and parse date string
        Returns date object if valid, None otherwise
        """
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, date_format).date()
        except ValueError:
            return None
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> bool:
        """Validate that start_date is before or equal to end_date"""
        if not start_date or not end_date:
            return True
        return start_date <= end_date
    
    @staticmethod
    def validate_numeric(value: str) -> bool:
        """Validate if string can be converted to number"""
        if not value:
            return True
        
        try:
            float(value)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_positive_number(value: float) -> bool:
        """Validate if number is positive"""
        try:
            return float(value) > 0
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_required(value: str) -> bool:
        """Validate required field is not empty"""
        return bool(value and value.strip())
    
    @staticmethod
    def validate_length(value: str, min_len: int = 0, max_len: int = 1000) -> bool:
        """Validate string length"""
        if not value:
            return min_len == 0
        return min_len <= len(value) <= max_len
