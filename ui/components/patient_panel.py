"""
Patient Management Panel
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from services import PatientService
from utils import Formatters, Validators
import config


class PatientPanel(ctk.CTkFrame):
    """Panel for patient management"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.patient_service = PatientService()
        self.selected_patient = None
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI
        self.create_header()
        self.create_content()
        
        # Load initial data
        self.load_patients()
    
    def create_header(self):
        """Create header with title and actions"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header.grid_columnconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(
            header,
            text="👤 Quản Lý Bệnh Nhân",
            font=("Arial", 24, "bold")
        )
        title.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Add button
        add_btn = ctk.CTkButton(
            header,
            text="➕ Thêm Bệnh Nhân",
            command=self.show_add_dialog,
            width=150,
            height=40,
            font=("Arial", 13, "bold"),
            fg_color="#4CAF50",
            hover_color="#45a049"
        )
        add_btn.grid(row=0, column=2, padx=10, pady=10)
    
    def create_content(self):
        """Create content area with search and list"""
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        
        # Search bar
        search_frame = ctk.CTkFrame(content, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Tìm theo tên, số điện thoại, hoặc mã bệnh nhân...",
            width=400,
            height=40
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_patients())
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Tìm Kiếm",
            command=self.search_patients,
            width=120,
            height=40
        )
        search_btn.pack(side="left")
        
        # Patient list (scrollable)
        self.list_frame = ctk.CTkScrollableFrame(content)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.list_frame.grid_columnconfigure(0, weight=1)
    
    def load_patients(self, keyword=""):
        """Load and display patients"""
        # Clear current list
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        # Load patients
        patients = self.patient_service.search_patients(keyword, limit=100)
        
        if not patients:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Không tìm thấy bệnh nhân nào",
                font=("Arial", 14),
                text_color="gray"
            )
            no_data.grid(row=0, column=0, pady=50)
            return
        
        # Display patients
        for idx, patient in enumerate(patients):
            self.create_patient_card(patient, idx)
    
    def create_patient_card(self, patient, row):
        """Create a patient card"""
        card = ctk.CTkFrame(self.list_frame, fg_color="#f0f0f0", corner_radius=10)
        card.grid(row=row, column=0, sticky="ew", pady=5, padx=5)
        card.grid_columnconfigure(1, weight=1)
        
        # Patient info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=10)
        
        # Name and code
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"👤 {patient.full_name}",
            font=("Arial", 16, "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        code_label = ctk.CTkLabel(
            info_frame,
            text=f"Mã BN: {patient.patient_code}",
            font=("Arial", 12),
            text_color="gray",
            anchor="w"
        )
        code_label.pack(anchor="w")
        
        # Details
        details_text = f"📅 {Formatters.format_date(patient.date_of_birth) if patient.date_of_birth else 'N/A'} | "
        details_text += f"⚥ {patient.gender or 'N/A'} | "
        details_text += f"📞 {patient.phone_number or 'N/A'}"
        
        details_label = ctk.CTkLabel(
            info_frame,
            text=details_text,
            font=("Arial", 12),
            text_color="#555",
            anchor="w"
        )
        details_label.pack(anchor="w", pady=(5, 0))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=3, padx=10, pady=10)
        
        view_btn = ctk.CTkButton(
            btn_frame,
            text="👁️ Xem",
            command=lambda p=patient: self.view_patient(p),
            width=80,
            fg_color="#2196F3"
        )
        view_btn.pack(side="left", padx=2)
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Sửa",
            command=lambda p=patient: self.edit_patient(p),
            width=80,
            fg_color="#FF9800"
        )
        edit_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Xóa",
            command=lambda p=patient: self.delete_patient(p),
            width=80,
            fg_color="#F44336"
        )
        delete_btn.pack(side="left", padx=2)
    
    def search_patients(self):
        """Search patients"""
        keyword = self.search_entry.get()
        self.load_patients(keyword)
    
    def show_add_dialog(self):
        """Show add patient dialog"""
        dialog = PatientDialog(self, title="Thêm Bệnh Nhân Mới")
        dialog.wait_window()
        
        if dialog.result:
            try:
                # Auto-generate patient code
                patient_code = self.patient_service.generate_patient_code()
                
                self.patient_service.create_patient(
                    patient_code=patient_code,
                    full_name=dialog.result['full_name'],
                    date_of_birth=dialog.result.get('date_of_birth'),
                    gender=dialog.result.get('gender'),
                    phone_number=dialog.result.get('phone_number'),
                    address=dialog.result.get('address'),
                    notes=dialog.result.get('notes')
                )
                
                messagebox.showinfo("Thành Công", f"Đã thêm bệnh nhân: {patient_code}")
                self.load_patients()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm bệnh nhân: {str(e)}")
    
    def view_patient(self, patient):
        """View patient details"""
        details = f"""
Mã Bệnh Nhân: {patient.patient_code}
Họ Tên: {patient.full_name}
Ngày Sinh: {Formatters.format_date(patient.date_of_birth) if patient.date_of_birth else 'N/A'}
Giới Tính: {patient.gender or 'N/A'}
Số Điện Thoại: {patient.phone_number or 'N/A'}
Địa Chỉ: {patient.address or 'N/A'}
Ghi Chú: {patient.notes or 'N/A'}
        """
        messagebox.showinfo(f"Thông Tin Bệnh Nhân", details.strip())
    
    def edit_patient(self, patient):
        """Edit patient"""
        dialog = PatientDialog(self, title="Sửa Thông Tin Bệnh Nhân", patient=patient)
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.patient_service.update_patient(
                    patient.id,
                    **dialog.result
                )
                messagebox.showinfo("Thành Công", "Đã cập nhật thông tin bệnh nhân")
                self.load_patients()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {str(e)}")
    
    def delete_patient(self, patient):
        """Delete patient"""
        if messagebox.askyesno("Xác Nhận", f"Bạn có chắc muốn xóa bệnh nhân {patient.full_name}?"):
            try:
                self.patient_service.delete_patient(patient.id)
                messagebox.showinfo("Thành Công", "Đã xóa bệnh nhân")
                self.load_patients()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {str(e)}")


class PatientDialog(ctk.CTkToplevel):
    """Dialog for adding/editing patient"""
    
    def __init__(self, master, title="Bệnh Nhân", patient=None):
        super().__init__(master)
        
        self.title(title)
        self.geometry("500x600")
        self.resizable(False, False)
        
        self.patient = patient
        self.result = None
        
        # Create form
        self.create_form()
        
        # Center window
        self.transient(master)
        self.grab_set()
    
    def create_form(self):
        """Create patient form"""
        form = ctk.CTkScrollableFrame(self)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        form.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Full Name
        ctk.CTkLabel(form, text="Họ Tên *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.name_entry = ctk.CTkEntry(form, width=300)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.patient:
            self.name_entry.insert(0, self.patient.full_name)
        row += 1
        
        # Date of Birth
        ctk.CTkLabel(form, text="Ngày Sinh:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.dob_entry = ctk.CTkEntry(form, placeholder_text="dd/mm/yyyy")
        self.dob_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.patient and self.patient.date_of_birth:
            self.dob_entry.insert(0, Formatters.format_date(self.patient.date_of_birth))
        row += 1
        
        # Gender
        ctk.CTkLabel(form, text="Giới Tính:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.gender_combo = ctk.CTkComboBox(form, values=config.GENDER_OPTIONS)
        self.gender_combo.grid(row=row, column=1, sticky="ew", pady=10)
        if self.patient and self.patient.gender:
            self.gender_combo.set(self.patient.gender)
        row += 1
        
        # Phone
        ctk.CTkLabel(form, text="Số Điện Thoại:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.phone_entry = ctk.CTkEntry(form)
        self.phone_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.patient:
            self.phone_entry.insert(0, self.patient.phone_number or "")
        row += 1
        
        # Address
        ctk.CTkLabel(form, text="Địa Chỉ:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.address_text = ctk.CTkTextbox(form, height=80)
        self.address_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.patient:
            self.address_text.insert("1.0", self.patient.address or "")
        row += 1
        
        # Notes
        ctk.CTkLabel(form, text="Ghi Chú:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.notes_text = ctk.CTkTextbox(form, height=80)
        self.notes_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.patient:
            self.notes_text.insert("1.0", self.patient.notes or "")
        row += 1
        
        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Lưu",
            command=self.save,
            width=120,
            fg_color="#4CAF50"
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Hủy",
            command=self.destroy,
            width=120,
            fg_color="#9E9E9E"
        )
        cancel_btn.pack(side="left", padx=10)
    
    def save(self):
        """Save patient data"""
        # Validate
        full_name = self.name_entry.get().strip()
        if not full_name:
            messagebox.showerror("Lỗi", "Vui lòng nhập họ tên")
            return
        
        # Parse date
        dob_str = self.dob_entry.get().strip()
        dob = Formatters.parse_date(dob_str) if dob_str else None
        
        # Build result
        self.result = {
            'full_name': full_name,
            'date_of_birth': dob,
            'gender': self.gender_combo.get(),
            'phone_number': self.phone_entry.get().strip() or None,
            'address': self.address_text.get("1.0", "end-1c").strip() or None,
            'notes': self.notes_text.get("1.0", "end-1c").strip() or None
        }
        
        self.destroy()
