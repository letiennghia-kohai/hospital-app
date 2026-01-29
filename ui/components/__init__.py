"""UI Components package initialization"""
from .patient_panel import PatientPanel
from .visit_panel import VisitPanel
from .test_panel import TestPanel
from .appointment_panel import AppointmentPanel
from .medicine_panel import MedicinePanel
from .import_panel import ImportPanel

__all__ = [
    'PatientPanel',
    'VisitPanel',
    'TestPanel',
    'AppointmentPanel',
    'MedicinePanel',
    'ImportPanel'
]
