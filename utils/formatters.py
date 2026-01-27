"""
Formatters
Data formatting utilities for display
"""
from datetime import datetime, date
from typing import Optional
import config


class Formatters:
    """Collection of formatting functions"""
    
    @staticmethod
    def format_date(date_obj: Optional[date], format_str: str = None) -> str:
        """Format date object to string"""
        if not date_obj:
            return ""
        
        if format_str is None:
            format_str = config.DATE_FORMAT
        
        try:
            return date_obj.strftime(format_str)
        except:
            return str(date_obj)
    
    @staticmethod
    def format_datetime(datetime_obj: Optional[datetime], format_str: str = None) -> str:
        """Format datetime object to string"""
        if not datetime_obj:
            return ""
        
        if format_str is None:
            format_str = config.DATETIME_FORMAT
        
        try:
            return datetime_obj.strftime(format_str)
        except:
            return str(datetime_obj)
    
    @staticmethod
    def parse_date(date_str: str, format_str: str = None) -> Optional[date]:
        """Parse date string to date object"""
        if not date_str:
            return None
        
        if format_str is None:
            format_str = config.DATE_FORMAT
        
        try:
            return datetime.strptime(date_str, format_str).date()
        except:
            return None
    
    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number for display"""
        if not phone:
            return ""
        
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        
        # Format as 0123-456-789
        if len(digits) == 10 and digits.startswith('0'):
            return f"{digits[:4]}-{digits[4:7]}-{digits[7:]}"
        
        return phone
    
    @staticmethod
    def format_number(value: Optional[float], decimal_places: int = 2) -> str:
        """Format number with specified decimal places"""
        if value is None:
            return ""
        
        try:
            return f"{float(value):.{decimal_places}f}"
        except:
            return str(value)
    
    @staticmethod
    def format_currency(value: Optional[float]) -> str:
        """Format currency (VND)"""
        if value is None:
            return ""
        
        try:
            return f"{int(value):,} đ"
        except:
            return str(value)
    
    @staticmethod
    def format_gender(gender: str) -> str:
        """Format gender for display"""
        gender_map = {
            "Nam": "Nam",
            "Nữ": "Nữ",
            "Khác": "Khác",
            "M": "Nam",
            "F": "Nữ",
            "O": "Khác"
        }
        return gender_map.get(gender, gender or "")
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 50) -> str:
        """Truncate text with ellipsis"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + "..."
    
    @staticmethod
    def format_test_result(value: Optional[float], text: Optional[str], 
                          normal_min: Optional[float] = None,
                          normal_max: Optional[float] = None) -> tuple:
        """
        Format test result and determine if it's normal
        Returns (formatted_value, is_normal)
        """
        if value is not None:
            formatted = Formatters.format_number(value)
            
            # Check if within normal range
            is_normal = True
            if normal_min is not None and value < normal_min:
                is_normal = False
            if normal_max is not None and value > normal_max:
                is_normal = False
            
            return formatted, is_normal
        elif text:
            return text, True
        else:
            return "", True


# Import re for phone formatting
import re
