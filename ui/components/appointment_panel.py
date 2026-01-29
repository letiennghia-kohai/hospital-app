"""
Appointment Management Panel with Alerts
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date, timedelta
from services import AppointmentService, PatientService
from utils import Formatters
import config


class AppointmentPanel(ctk.CTkFrame):
    """Panel for appointment management"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.appointment_service = AppointmentService()
        self.patient_service = PatientService()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI
        self.create_header()
        self.create_content()
        
        # Load data
        self.load_appointments()
    
    def create_header(self):
        """Create header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        title = ctk.CTkLabel(
            header,
            text="📅 Quản Lý Lịch Hẹn",
            font=("Arial", 24, "bold")
        )
        title.pack(side="left", padx=10, pady=10)
        
        add_btn = ctk.CTkButton(
            header,
            text="➕ Thêm Lịch Hẹn",
            command=self.add_appointment,
            width=150,
            height=40,
            font=("Arial", 13, "bold"),
            fg_color="#4CAF50"
        )
        add_btn.pack(side="right", padx=10, pady=10)
    
    def create_content(self):
        """Create content area"""
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)
        
        # Overdue alerts
        self.alerts_frame = ctk.CTkFrame(content, fg_color="#FFF3E0", corner_radius=10)
        self.alerts_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Filter buttons
        filter_frame = ctk.CTkFrame(content, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        ctk.CTkButton(
            filter_frame,
            text="⚠️ Quá Hạn",
            command=lambda: self.load_appointments("overdue"),
            width=120,
            fg_color="#F44336"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            filter_frame,
            text="📅 Sắp Tới",
            command=lambda: self.load_appointments("upcoming"),
            width=120,
            fg_color="#2196F3"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            filter_frame,
            text="📋 Tất Cả",
            command=lambda: self.load_appointments("all"),
            width=120,
            fg_color="#9E9E9E"
        ).pack(side="left", padx=5)
        
        # Appointment list
        self.list_frame = ctk.CTkScrollableFrame(content)
        self.list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.list_frame.grid_columnconfigure(0, weight=1)
    
    def load_appointments(self, filter_type="upcoming"):
        """Load appointments"""
        # Clear list
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # Clear alerts
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()
        
        # Load based on filter
        if filter_type == "overdue":
            appointments = self.appointment_service.get_overdue_appointments()
        elif filter_type == "upcoming":
            appointments = self.appointment_service.get_upcoming_appointments(days=30)
        else:
            today = date.today()
            appointments = self.appointment_service.get_appointments_by_date_range(
                today - timedelta(days=30),
                today + timedelta(days=90)
            )
        
        # Show overdue alert
        overdue_count = len([a for a in appointments if a.status == "OVERDUE"])
        if overdue_count > 0:
            alert_label = ctk.CTkLabel(
                self.alerts_frame,
                text=f"⚠️ Có {overdue_count} lịch hẹn quá hạn!",
                font=("Arial", 14, "bold"),
                text_color="#E65100"
            )
            alert_label.pack(padx=20, pady=15)
        
        if not appointments:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Không có lịch hẹn nào",
                font=("Arial", 14),
                text_color="gray"
            )
            no_data.grid(row=0, column=0, pady=50)
            return
        
        # Display appointments
        for idx, appt in enumerate(appointments):
            self.create_appointment_card(appt, idx)
    
    def create_appointment_card(self, appointment, row):
        """Create appointment card"""
        # Color based on status
        if appointment.status == "OVERDUE":
            fg_color = "#FFEBEE"
        elif appointment.status == "COMPLETED":
            fg_color = "#E8F5E9"
        else:
            fg_color = "#f0f0f0"
        
        card = ctk.CTkFrame(self.list_frame, fg_color=fg_color, corner_radius=10)
        card.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Patient and date
        header_text = f"👤 {appointment.patient.full_name} | 📅 {Formatters.format_date(appointment.appointment_date)}"
        header_label = ctk.CTkLabel(
            info_frame,
            text=header_text,
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        header_label.pack(anchor="w")
        
        # Status
        status_text = config.APPOINTMENT_STATUS.get(appointment.status, appointment.status)
        status_color = "#F44336" if appointment.status == "OVERDUE" else "#4CAF50" if appointment.status == "COMPLETED" else "#2196F3"
        
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"📊 Trạng thái: {status_text}",
            font=("Arial", 12),
            text_color=status_color,
            anchor="w"
        )
        status_label.pack(anchor="w", pady=(5, 0))
        
        # Reason
        if appointment.reason:
            reason_label = ctk.CTkLabel(
                info_frame,
                text=f"📝 Lý do: {appointment.reason}",
                font=("Arial", 12),
                text_color="#555",
                anchor="w"
            )
            reason_label.pack(anchor="w", pady=(5, 0))
        
        # Buttons
        btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=(10, 0))
        
        if appointment.status != "COMPLETED":
            complete_btn = ctk.CTkButton(
                btn_frame,
                text="✅ Hoàn Thành",
                command=lambda a=appointment: self.complete_appointment(a),
                width=120,
                fg_color="#4CAF50"
            )
            complete_btn.pack(side="left", padx=(0, 5))
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Sửa",
            command=lambda a=appointment: self.edit_appointment(a),
            width=80,
            fg_color="#FF9800"
        )
        edit_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Hủy",
            command=lambda a=appointment: self.cancel_appointment(a),
            width=80,
            fg_color="#F44336"
        )
        cancel_btn.pack(side="left", padx=5)
    
    def add_appointment(self):
        """Add new appointment"""
        dialog = AppointmentDialog(self, title="Thêm Lịch Hẹn Mới")
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.appointment_service.create_appointment(**dialog.result)
                messagebox.showinfo("Thành Công", "Đã thêm lịch hẹn")
                self.load_appointments()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm: {str(e)}")
    
    def edit_appointment(self, appointment):
        """Edit appointment"""
        dialog = AppointmentDialog(self, title="Sửa Lịch Hẹn", appointment=appointment)
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.appointment_service.update_appointment(appointment.id, **dialog.result)
                messagebox.showinfo("Thành Công", "Đã cập nhật lịch hẹn")
                self.load_appointments()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {str(e)}")
    
    def complete_appointment(self, appointment):
        """Mark appointment as completed"""
        try:
            self.appointment_service.mark_as_completed(appointment.id)
            messagebox.showinfo("Thành Công", "Đã đánh dấu hoàn thành")
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
    
    def cancel_appointment(self, appointment):
        """Cancel appointment"""
        if messagebox.askyesno("Xác Nhận", "Bạn có chắc muốn hủy lịch hẹn này?"):
            try:
                self.appointment_service.mark_as_cancelled(appointment.id)
                messagebox.showinfo("Thành Công", "Đã hủy lịch hẹn")
                self.load_appointments()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))


class AppointmentDialog(ctk.CTkToplevel):
    """Dialog for appointment"""
    
    def __init__(self, master, title="Lịch Hẹn", appointment=None):
        super().__init__(master)
        
        self.title(title)
        self.geometry("500x400")
        
        self.appointment = appointment
        self.result = None
        self.patient_service = PatientService()
        
        self.create_form()
        
        self.transient(master)
        self.grab_set()
    
    def create_form(self):
        """Create form"""
        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        form.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Patient
        ctk.CTkLabel(form, text="Bệnh Nhân *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        
        patients = self.patient_service.get_all_patients(limit=500)
        patient_names = [f"{p.patient_code} - {p.full_name}" for p in patients]
        
        self.patient_combo = ctk.CTkComboBox(form, values=patient_names, width=300)
        self.patient_combo.grid(row=row, column=1, sticky="ew", pady=10)
        
        if self.appointment:
            patient_text = f"{self.appointment.patient.patient_code} - {self.appointment.patient.full_name}"
            self.patient_combo.set(patient_text)
        
        self.patients_list = patients
        row += 1
        
        # Date
        ctk.CTkLabel(form, text="Ngày Hẹn *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.date_entry = ctk.CTkEntry(form, placeholder_text="dd/mm/yyyy")
        self.date_entry.grid(row=row, column=1, sticky="ew", pady=10)
        
        if self.appointment:
            self.date_entry.insert(0, Formatters.format_date(self.appointment.appointment_date))
        row += 1
        
        # Reason
        ctk.CTkLabel(form, text="Lý Do:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.reason_text = ctk.CTkTextbox(form, height=80)
        self.reason_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.appointment:
            self.reason_text.insert("1.0", self.appointment.reason or "")
        row += 1
        
        # Notes
        ctk.CTkLabel(form, text="Ghi Chú:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.notes_text = ctk.CTkTextbox(form, height=60)
        self.notes_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.appointment:
            self.notes_text.insert("1.0", self.appointment.notes or "")
        row += 1
        
        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="💾 Lưu",
            command=self.save,
            width=120,
            fg_color="#4CAF50"
        ).pack(side="left", padx=10)
        
        ctk.CTkButton(
            btn_frame,
            text="❌ Hủy",
            command=self.destroy,
            width=120,
            fg_color="#9E9E9E"
        ).pack(side="left", padx=10)
    
    def save(self):
        """Save"""
        # Get patient
        selected_text = self.patient_combo.get()
        
        # Find patient by matching text
        patient = None
        for p in self.patients_list:
            if f"{p.patient_code} - {p.full_name}" == selected_text:
                patient = p
                break
        
        if not patient:
            messagebox.showerror("Lỗi", "Vui lòng chọn bệnh nhân")
            return
        
        # Parse date
        appt_date = Formatters.parse_date(self.date_entry.get())
        if not appt_date:
            messagebox.showerror("Lỗi", "Ngày hẹn không hợp lệ")
            return
        
        self.result = {
            'patient_id': patient.id,
            'appointment_date': appt_date,
            'reason': self.reason_text.get("1.0", "end-1c").strip() or None,
            'notes': self.notes_text.get("1.0", "end-1c").strip() or None
        }
        
        self.destroy()
