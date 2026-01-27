"""
SQLAlchemy ORM Models
Defines all database tables and relationships
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Float, Boolean,
    ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Patient(Base):
    """Patient (Bệnh nhân) table"""
    __tablename__ = 'patients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_code = Column(String(50), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    phone_number = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    visits = relationship("Visit", back_populates="patient", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(code={self.patient_code}, name={self.full_name})>"


class Visit(Base):
    """Visit (Lần khám) table"""
    __tablename__ = 'visits'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    visit_date = Column(Date, nullable=False, index=True)
    symptoms = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    conclusion = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    patient = relationship("Patient", back_populates="visits")
    test_results = relationship("TestResult", back_populates="visit", cascade="all, delete-orphan")
    prescriptions = relationship("Prescription", back_populates="visit", cascade="all, delete-orphan")
    appointment = relationship("Appointment", back_populates="visit", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Visit(id={self.id}, patient_id={self.patient_id}, date={self.visit_date})>"


class TestType(Base):
    """TestType (Loại xét nghiệm) table"""
    __tablename__ = 'test_types'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), unique=True, nullable=False)
    category = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    normal_range_min = Column(Float, nullable=True)
    normal_range_max = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    test_results = relationship("TestResult", back_populates="test_type")
    
    def __repr__(self):
        return f"<TestType(name={self.name}, category={self.category})>"


class TestResult(Base):
    """TestResult (Kết quả xét nghiệm) table"""
    __tablename__ = 'test_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_id = Column(Integer, ForeignKey('visits.id'), nullable=False)
    test_type_id = Column(Integer, ForeignKey('test_types.id'), nullable=False)
    result_value = Column(Float, nullable=True)
    result_text = Column(Text, nullable=True)
    unit = Column(String(50), nullable=True)
    test_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    visit = relationship("Visit", back_populates="test_results")
    test_type = relationship("TestType", back_populates="test_results")
    
    # Composite index for efficient queries
    __table_args__ = (
        Index('idx_visit_test', 'visit_id', 'test_type_id'),
    )
    
    def __repr__(self):
        return f"<TestResult(visit_id={self.visit_id}, test={self.test_type_id}, value={self.result_value})>"


class Medicine(Base):
    """Medicine (Thuốc) table"""
    __tablename__ = 'medicines'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(100), nullable=True)
    unit = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    
    # Relationships
    prescriptions = relationship("Prescription", back_populates="medicine")
    
    def __repr__(self):
        return f"<Medicine(name={self.name}, category={self.category})>"


class Prescription(Base):
    """Prescription (Đơn thuốc) table"""
    __tablename__ = 'prescriptions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_id = Column(Integer, ForeignKey('visits.id'), nullable=False)
    medicine_id = Column(Integer, ForeignKey('medicines.id'), nullable=False)
    dosage = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)
    duration_days = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    visit = relationship("Visit", back_populates="prescriptions")
    medicine = relationship("Medicine", back_populates="prescriptions")
    
    # Composite index
    __table_args__ = (
        Index('idx_visit_medicine', 'visit_id', 'medicine_id'),
    )
    
    def __repr__(self):
        return f"<Prescription(visit_id={self.visit_id}, medicine_id={self.medicine_id})>"


class Appointment(Base):
    """Appointment (Lịch hẹn) table"""
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    visit_id = Column(Integer, ForeignKey('visits.id'), unique=True, nullable=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False, index=True)
    appointment_date = Column(Date, nullable=False, index=True)
    reason = Column(Text, nullable=True)
    status = Column(String(50), default="PENDING")  # PENDING, COMPLETED, OVERDUE, CANCELLED
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    visit = relationship("Visit", back_populates="appointment")
    patient = relationship("Patient", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment(patient_id={self.patient_id}, date={self.appointment_date}, status={self.status})>"
