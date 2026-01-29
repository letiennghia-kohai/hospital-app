"""
Visit Management Panel
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date
from services import VisitService, PatientService
from utils import Formatters
from ui.components.visit_details_dialog import VisitDetailsDialog
import config


class VisitPanel(ctk.CTkFrame):
    """Panel for visit/examination management"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.visit_service = VisitService()
        self.patient_service = PatientService()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI
        self.create_header()
        self.create_content()
        
        # Load initial data
        self.load_visits()
    
    def create_header(self):
        """Create header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        title = ctk.CTkLabel(
            header,
            text="🩺 Quản Lý Khám Bệnh",
            font=("Arial", 24, "bold")
        )
        title.pack(side="left", padx=10, pady=10)
        
        add_btn = ctk.CTkButton(
            header,
            text="➕ Thêm Lần Khám",
            command=self.show_add_dialog,
            width=150,
            height=40,
            font=("Arial", 13, "bold"),
            fg_color="#4CAF50"
        )
        add_btn.pack(side="right", padx=10, pady=10)
    
    def create_content(self):
        """Create content area"""
        self.list_frame = ctk.CTkScrollableFrame(self)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.list_frame.grid_columnconfigure(0, weight=1)
    
    def load_visits(self):
        """Load recent visits"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        visits = self.visit_service.get_recent_visits(limit=50)
        
        if not visits:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Chưa có lần khám nào",
                font=("Arial", 14),
                text_color="gray"
            )
            no_data.grid(row=0, column=0, pady=50)
            return
        
        for idx, visit in enumerate(visits):
            self.create_visit_card(visit, idx)
    
    def create_visit_card(self, visit, row):
        """Create visit card"""
        card = ctk.CTkFrame(self.list_frame, fg_color="#f0f0f0", corner_radius=10)
        card.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Patient and date
        header_text = f"👤 {visit.patient.full_name} | 📅 {Formatters.format_date(visit.visit_date)}"
        header_label = ctk.CTkLabel(
            info_frame,
            text=header_text,
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        header_label.pack(anchor="w")
        
        # Diagnosis
        if visit.diagnosis:
            diag_label = ctk.CTkLabel(
                info_frame,
                text=f"🔍 Chẩn đoán: {visit.diagnosis[:100]}...",
                font=("Arial", 12),
                text_color="#555",
                anchor="w"
            )
            diag_label.pack(anchor="w", pady=(5, 0))
        
        # Buttons
        btn_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=(10, 0))
        
        view_btn = ctk.CTkButton(
            btn_frame,
            text="👁️ Xem Chi Tiết",
            command=lambda v=visit: self.view_visit(v),
            width=120,
            fg_color="#2196F3"
        )
        view_btn.pack(side="left", padx=(0, 5))
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Sửa",
            command=lambda v=visit: self.edit_visit(v),
            width=80,
            fg_color="#FF9800"
        )
        edit_btn.pack(side="left", padx=5)
    
    def show_add_dialog(self):
        """Show add visit dialog"""
        dialog = VisitDialog(self, title="Thêm Lần Khám Mới")
        dialog.wait_window()
        
        if dialog.result:
            try:
                # Create visit
                new_visit = self.visit_service.create_visit(**dialog.result)
                messagebox.showinfo("Thành Công", "Đã thêm lần khám mới")
                self.load_visits()
                
                # Ask if user wants to add test results and prescriptions
                if messagebox.askyesno(
                    "Thêm Chi Tiết?", 
                    "Bạn có muốn thêm kết quả xét nghiệm và đơn thuốc cho lần khám này không?"
                ):
                    # Open details dialog to add test results and prescriptions
                    details_dialog = VisitDetailsDialog(
                        self, 
                        visit=new_visit, 
                        visit_service=self.visit_service
                    )
                    details_dialog.wait_window()
                    self.load_visits()
                    
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm: {str(e)}")
    
    def view_visit(self, visit):
        """View visit details with test results and prescriptions"""
        dialog = VisitDetailsDialog(self, visit=visit, visit_service=self.visit_service)
        dialog.wait_window()
        self.load_visits()  # Refresh in case changes were made
    
    def edit_visit(self, visit):
        """Edit visit"""
        dialog = VisitDialog(self, title="Sửa Thông Tin Khám", visit=visit)
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.visit_service.update_visit(visit.id, **dialog.result)
                messagebox.showinfo("Thành Công", "Đã cập nhật thông tin")
                self.load_visits()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {str(e)}")


class VisitDialog(ctk.CTkToplevel):
    """Dialog for adding/editing visit"""
    
    def __init__(self, master, title="Lần Khám", visit=None):
        super().__init__(master)
        
        self.title(title)
        self.geometry("600x700")
        
        self.visit = visit
        self.result = None
        self.patient_service = PatientService()
        
        self.create_form()
        
        self.transient(master)
        self.grab_set()
    
    def create_form(self):
        """Create visit form"""
        form = ctk.CTkScrollableFrame(self)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        form.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Patient selection
        ctk.CTkLabel(form, text="Bệnh Nhân *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        
        # Get all patients for dropdown
        patients = self.patient_service.get_all_patients(limit=500)
        patient_names = [f"{p.patient_code} - {p.full_name}" for p in patients]
        
        self.patient_combo = ctk.CTkComboBox(form, values=patient_names, width=400)
        self.patient_combo.grid(row=row, column=1, sticky="ew", pady=10)
        
        if self.visit:
            patient_text = f"{self.visit.patient.patient_code} - {self.visit.patient.full_name}"
            self.patient_combo.set(patient_text)
        
        self.patients_list = patients
        row += 1
        
        # Visit date
        ctk.CTkLabel(form, text="Ngày Khám *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.date_entry = ctk.CTkEntry(form, placeholder_text="dd/mm/yyyy")
        self.date_entry.grid(row=row, column=1, sticky="ew", pady=10)
        
        if self.visit:
            self.date_entry.insert(0, Formatters.format_date(self.visit.visit_date))
        else:
            self.date_entry.insert(0, Formatters.format_date(date.today()))
        row += 1
        
        # Symptoms
        ctk.CTkLabel(form, text="Triệu Chứng:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.symptoms_text = ctk.CTkTextbox(form, height=100)
        self.symptoms_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.visit:
            self.symptoms_text.insert("1.0", self.visit.symptoms or "")
        row += 1
        
        # Diagnosis
        ctk.CTkLabel(form, text="Chẩn Đoán:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.diagnosis_text = ctk.CTkTextbox(form, height=100)
        self.diagnosis_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.visit:
            self.diagnosis_text.insert("1.0", self.visit.diagnosis or "")
        row += 1
        
        # Conclusion
        ctk.CTkLabel(form, text="Kết Luận:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.conclusion_text = ctk.CTkTextbox(form, height=100)
        self.conclusion_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.visit:
            self.conclusion_text.insert("1.0", self.visit.conclusion or "")
        row += 1
        
        # Notes
        ctk.CTkLabel(form, text="Ghi Chú:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.notes_text = ctk.CTkTextbox(form, height=80)
        self.notes_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.visit:
            self.notes_text.insert("1.0", self.visit.notes or "")
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
        """Save visit data"""
        # Get selected patient
        selected_text = self.patient_combo.get()
        
        # Find patient index by matching the text
        patient_idx = -1
        for idx, patient in enumerate(self.patients_list):
            expected_text = f"{patient.patient_code} - {patient.full_name}"
            if expected_text == selected_text:
                patient_idx = idx
                break
        
        if patient_idx < 0:
            messagebox.showerror("Lỗi", "Vui lòng chọn bệnh nhân")
            return
        
        patient = self.patients_list[patient_idx]
        
        # Parse date
        visit_date = Formatters.parse_date(self.date_entry.get())
        if not visit_date:
            messagebox.showerror("Lỗi", "Ngày khám không hợp lệ")
            return
        
        self.result = {
            'patient_id': patient.id,
            'visit_date': visit_date,
            'symptoms': self.symptoms_text.get("1.0", "end-1c").strip() or None,
            'diagnosis': self.diagnosis_text.get("1.0", "end-1c").strip() or None,
            'conclusion': self.conclusion_text.get("1.0", "end-1c").strip() or None,
            'notes': self.notes_text.get("1.0", "end-1c").strip() or None
        }
        
        self.destroy()
