"""
Visit Details Dialog with Test Results and Prescriptions
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from services import TestService, MedicineService
from utils import Formatters
import config


class VisitDetailsDialog(ctk.CTkToplevel):
    """Comprehensive visit details with tabs for info, tests, and prescriptions"""
    
    def __init__(self, master, visit, visit_service):
        super().__init__(master)
        
        self.title(f"Chi Tiết Lần Khám - {visit.patient.full_name}")
        self.geometry("900x700")
        
        self.visit = visit
        self.visit_service = visit_service
        self.test_service = TestService()
        self.medicine_service = MedicineService()
        
        self.create_ui()
        
        self.transient(master)
        self.grab_set()
    
    def create_ui(self):
        """Create tabbed interface"""
        # Header
        header = ctk.CTkFrame(self, fg_color="#2196F3", corner_radius=0)
        header.pack(fill="x", pady=(0, 10))
        
        title = ctk.CTkLabel(
            header,
            text=f"🩺 Lần Khám: {Formatters.format_date(self.visit.visit_date)}",
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        title.pack(padx=20, pady=15, anchor="w")
        
        patient_info = ctk.CTkLabel(
            header,
            text=f"Bệnh nhân: {self.visit.patient.full_name} ({self.visit.patient.patient_code})",
            font=("Arial", 14),
            text_color="white"
        )
        patient_info.pack(padx=20, pady=(0, 15), anchor="w")
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("Thông Tin Khám")
        self.tabview.add("Kết Quả Xét Nghiệm")
        self.tabview.add("Đơn Thuốc")
        
        self.create_info_tab()
        self.create_tests_tab()
        self.create_prescriptions_tab()
        
        # Close button
        close_btn = ctk.CTkButton(
            self,
            text="Đóng",
            command=self.destroy,
            width=120,
            height=40,
            fg_color="#9E9E9E"
        )
        close_btn.pack(pady=(0, 10))
    
    def create_info_tab(self):
        """Create visit information tab"""
        tab = self.tabview.tab("Thông Tin Khám")
        tab.grid_columnconfigure(0, weight=1)
        
        info_frame = ctk.CTkScrollableFrame(tab)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Symptoms
        ctk.CTkLabel(
            info_frame,
            text="Triệu Chứng:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        symptoms_box = ctk.CTkTextbox(info_frame, height=100)
        symptoms_box.pack(fill="x", padx=10, pady=5)
        symptoms_box.insert("1.0", self.visit.symptoms or "Không có")
        symptoms_box.configure(state="disabled")
        
        # Diagnosis
        ctk.CTkLabel(
            info_frame,
            text="Chẩn Đoán:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        diagnosis_box = ctk.CTkTextbox(info_frame, height=100)
        diagnosis_box.pack(fill="x", padx=10, pady=5)
        diagnosis_box.insert("1.0", self.visit.diagnosis or "Không có")
        diagnosis_box.configure(state="disabled")
        
        # Conclusion
        ctk.CTkLabel(
            info_frame,
            text="Kết Luận:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        conclusion_box = ctk.CTkTextbox(info_frame, height=100)
        conclusion_box.pack(fill="x", padx=10, pady=5)
        conclusion_box.insert("1.0", self.visit.conclusion or "Không có")
        conclusion_box.configure(state="disabled")
        
        # Notes
        if self.visit.notes:
            ctk.CTkLabel(
                info_frame,
                text="Ghi Chú:",
                font=("Arial", 14, "bold")
            ).pack(anchor="w", padx=10, pady=(10, 5))
            
            notes_box = ctk.CTkTextbox(info_frame, height=80)
            notes_box.pack(fill="x", padx=10, pady=5)
            notes_box.insert("1.0", self.visit.notes)
            notes_box.configure(state="disabled")
    
    def create_tests_tab(self):
        """Create test results tab"""
        tab = self.tabview.tab("Kết Quả Xét Nghiệm")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Add button
        add_btn = ctk.CTkButton(
            tab,
            text="➕ Thêm Kết Quả Xét Nghiệm",
            command=self.add_test_result,
            fg_color="#4CAF50",
            height=40
        )
        add_btn.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Test results list
        self.tests_list = ctk.CTkScrollableFrame(tab)
        self.tests_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.load_test_results()
    
    def load_test_results(self):
        """Load test results for this visit"""
        for widget in self.tests_list.winfo_children():
            widget.destroy()
        
        # Get test results
        test_results = self.test_service.get_visit_test_results(self.visit.id)
        
        if not test_results:
            no_data = ctk.CTkLabel(
                self.tests_list,
                text="Chưa có kết quả xét nghiệm nào",
                font=("Arial", 13),
                text_color="gray"
            )
            no_data.pack(pady=50)
            return
        
        for test_result in test_results:
            self.create_test_result_card(test_result)
    
    def create_test_result_card(self, test_result):
        """Create test result card"""
        card = ctk.CTkFrame(self.tests_list, fg_color="#f0f0f0", corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # Test name
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"🧪 {test_result.test_type.name}",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Result value or text
        if test_result.result_value is not None:
            result_text = f"{test_result.result_value} {test_result.unit or test_result.test_type.unit or ''}"
        else:
            result_text = test_result.result_text or "N/A"
        
        result_label = ctk.CTkLabel(
            info_frame,
            text=f"Kết quả: {result_text}",
            font=("Arial", 13),
            anchor="w"
        )
        result_label.pack(anchor="w", pady=(5, 0))
        
        # Date
        date_label = ctk.CTkLabel(
            info_frame,
            text=f"Ngày: {Formatters.format_date(test_result.test_date)}",
            font=("Arial", 11),
            text_color="gray",
            anchor="w"
        )
        date_label.pack(anchor="w", pady=(3, 0))
        
        # Notes
        if test_result.notes:
            notes_label = ctk.CTkLabel(
                info_frame,
                text=f"Ghi chú: {test_result.notes}",
                font=("Arial", 11),
                text_color="#555",
                anchor="w"
            )
            notes_label.pack(anchor="w", pady=(3, 0))
    
    def add_test_result(self):
        """Add test result for this visit"""
        dialog = TestResultDialog(self, visit=self.visit, test_service=self.test_service)
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.test_service.create_test_result(**dialog.result)
                messagebox.showinfo("Thành Công", "Đã thêm kết quả xét nghiệm")
                self.load_test_results()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm: {str(e)}")
    
    def create_prescriptions_tab(self):
        """Create prescriptions tab"""
        tab = self.tabview.tab("Đơn Thuốc")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Add button
        add_btn = ctk.CTkButton(
            tab,
            text="➕ Kê Đơn Thuốc",
            command=self.add_prescription,
            fg_color="#4CAF50",
            height=40
        )
        add_btn.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # Prescriptions list
        self.prescriptions_list = ctk.CTkScrollableFrame(tab)
        self.prescriptions_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.load_prescriptions()
    
    def load_prescriptions(self):
        """Load prescriptions for this visit"""
        for widget in self.prescriptions_list.winfo_children():
            widget.destroy()
        
        # Get prescriptions
        prescriptions = self.medicine_service.get_visit_prescriptions(self.visit.id)
        
        if not prescriptions:
            no_data = ctk.CTkLabel(
                self.prescriptions_list,
                text="Chưa có đơn thuốc nào",
                font=("Arial", 13),
                text_color="gray"
            )
            no_data.pack(pady=50)
            return
        
        for prescription in prescriptions:
            self.create_prescription_card(prescription)
    
    def create_prescription_card(self, prescription):
        """Create prescription card"""
        card = ctk.CTkFrame(self.prescriptions_list, fg_color="#f0f0f0", corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # Medicine name
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"💊 {prescription.medicine.name}",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        name_label.pack(anchor="w")
        
        # Dosage
        dosage_label = ctk.CTkLabel(
            info_frame,
            text=f"Liều lượng: {prescription.dosage}",
            font=("Arial", 13),
            anchor="w"
        )
        dosage_label.pack(anchor="w", pady=(5, 0))
        
        # Frequency and duration
        details = f"Tần suất: {prescription.frequency} | Số ngày: {prescription.duration_days}"
        details_label = ctk.CTkLabel(
            info_frame,
            text=details,
            font=("Arial", 12),
            text_color="#555",
            anchor="w"
        )
        details_label.pack(anchor="w", pady=(3, 0))
        
        
        # Instructions
        if prescription.notes:
            inst_label = ctk.CTkLabel(
                info_frame,
                text=f"Hướng dẫn: {prescription.notes}",
                font=("Arial", 11),
                text_color="#555",
                anchor="w"
            )
            inst_label.pack(anchor="w", pady=(3, 0))
    
    def add_prescription(self):
        """Add prescription for this visit"""
        dialog = PrescriptionDialog(self, visit=self.visit, medicine_service=self.medicine_service)
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.medicine_service.create_prescription(**dialog.result)
                messagebox.showinfo("Thành Công", "Đã kê đơn thuốc")
                self.load_prescriptions()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm: {str(e)}")


class TestResultDialog(ctk.CTkToplevel):
    """Dialog for adding test result"""
    
    def __init__(self, master, visit, test_service):
        super().__init__(master)
        
        self.title("Thêm Kết Quả Xét Nghiệm")
        self.geometry("500x550")
        
        self.visit = visit
        self.test_service = test_service
        self.result = None
        
        self.create_form()
        
        self.transient(master)
        self.grab_set()
    
    def create_form(self):
        """Create form"""
        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        form.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Test type selection
        ctk.CTkLabel(form, text="Loại Xét Nghiệm *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        
        test_types = self.test_service.get_all_test_types()
        test_type_names = [tt.name for tt in test_types]
        
        self.test_type_combo = ctk.CTkComboBox(form, values=test_type_names, width=300)
        self.test_type_combo.grid(row=row, column=1, sticky="ew", pady=10)
        self.test_type_combo.bind("<<ComboboxSelected>>", self.on_test_type_selected)
        
        self.test_types_list = test_types
        row += 1
        
        # Test date
        ctk.CTkLabel(form, text="Ngày Xét Nghiệm *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.date_entry = ctk.CTkEntry(form, placeholder_text="dd/mm/yyyy")
        self.date_entry.grid(row=row, column=1, sticky="ew", pady=10)
        self.date_entry.insert(0, Formatters.format_date(self.visit.visit_date))
        row += 1
        
        # Result value
        ctk.CTkLabel(form, text="Kết Quả Số:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.value_entry = ctk.CTkEntry(form, placeholder_text="Nhập số nếu có")
        self.value_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Unit
        ctk.CTkLabel(form, text="Đơn Vị:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.unit_entry = ctk.CTkEntry(form)
        self.unit_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Result text (for qualitative results)
        ctk.CTkLabel(form, text="Kết Quả Định Tính:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.text_entry = ctk.CTkEntry(form, placeholder_text="Âm tính, Dương tính...")
        self.text_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Notes
        ctk.CTkLabel(form, text="Ghi Chú:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.notes_text = ctk.CTkTextbox(form, height=80)
        self.notes_text.grid(row=row, column=1, sticky="ew", pady=10)
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
    
    def on_test_type_selected(self, event=None):
        """Auto-fill unit when test type is selected"""
        selected_text = self.test_type_combo.get()
        
        for tt in self.test_types_list:
            if tt.name == selected_text:
                if tt.unit:
                    self.unit_entry.delete(0, "end")
                    self.unit_entry.insert(0, tt.unit)
                break
    
    def save(self):
        """Save test result"""
        selected_text = self.test_type_combo.get()
        
        # Find test type
        test_type = None
        for tt in self.test_types_list:
            if tt.name == selected_text:
                test_type = tt
                break
        
        if not test_type:
            messagebox.showerror("Lỗi", "Vui lòng chọn loại xét nghiệm")
            return
        
        # Parse date
        test_date = Formatters.parse_date(self.date_entry.get())
        if not test_date:
            messagebox.showerror("Lỗi", "Ngày xét nghiệm không hợp lệ")
            return
        
        # Get value or text
        result_value = None
        value_str = self.value_entry.get().strip()
        if value_str:
            try:
                result_value = float(value_str)
            except ValueError:
                messagebox.showerror("Lỗi", "Kết quả số phải là số")
                return
        
        result_text = self.text_entry.get().strip() or None
        
        if result_value is None and not result_text:
            messagebox.showerror("Lỗi", "Vui lòng nhập kết quả số hoặc kết quả định tính")
            return
        
        self.result = {
            'visit_id': self.visit.id,
            'test_type_id': test_type.id,
            'test_date': test_date,
            'result_value': result_value,
            'result_text': result_text,
            'unit': self.unit_entry.get().strip() or None,
            'notes': self.notes_text.get("1.0", "end-1c").strip() or None
        }
        
        self.destroy()


class PrescriptionDialog(ctk.CTkToplevel):
    """Dialog for adding prescription"""
    
    def __init__(self, master, visit, medicine_service):
        super().__init__(master)
        
        self.title("Kê Đơn Thuốc")
        self.geometry("500x500")
        
        self.visit = visit
        self.medicine_service = medicine_service
        self.result = None
        
        self.create_form()
        
        self.transient(master)
        self.grab_set()
    
    def create_form(self):
        """Create form"""
        form = ctk.CTkFrame(self)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        form.grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Medicine selection
        ctk.CTkLabel(form, text="Thuốc *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        
        medicines = self.medicine_service.search_medicines("", active_only=True)
        medicine_names = [m.name for m in medicines]
        
        self.medicine_combo = ctk.CTkComboBox(form, values=medicine_names, width=300)
        self.medicine_combo.grid(row=row, column=1, sticky="ew", pady=10)
        
        self.medicines_list = medicines
        row += 1
        
        # Dosage
        ctk.CTkLabel(form, text="Liều Lượng *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.dosage_entry = ctk.CTkEntry(form, placeholder_text="VD: 1 viên, 5ml...")
        self.dosage_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Frequency
        ctk.CTkLabel(form, text="Tần Suất *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.frequency_combo = ctk.CTkComboBox(
            form,
            values=["1 lần/ngày", "2 lần/ngày", "3 lần/ngày", "4 lần/ngày", "Khi cần"]
        )
        self.frequency_combo.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Duration
        ctk.CTkLabel(form, text="Số Ngày *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.duration_entry = ctk.CTkEntry(form, placeholder_text="Số ngày dùng thuốc")
        self.duration_entry.grid(row=row, column=1, sticky="ew", pady=10)
        row += 1
        
        # Instructions
        ctk.CTkLabel(form, text="Hướng Dẫn:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.instructions_text = ctk.CTkTextbox(form, height=100)
        self.instructions_text.grid(row=row, column=1, sticky="ew", pady=10)
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
        """Save prescription"""
        selected_text = self.medicine_combo.get()
        
        # Find medicine
        medicine = None
        for m in self.medicines_list:
            if m.name == selected_text:
                medicine = m
                break
        
        if not medicine:
            messagebox.showerror("Lỗi", "Vui lòng chọn thuốc")
            return
        
        dosage = self.dosage_entry.get().strip()
        if not dosage:
            messagebox.showerror("Lỗi", "Vui lòng nhập liều lượng")
            return
        
        frequency = self.frequency_combo.get().strip()
        if not frequency:
            messagebox.showerror("Lỗi", "Vui lòng chọn tần suất")
            return
        
        try:
            duration = int(self.duration_entry.get().strip())
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số ngày phải là số nguyên dương")
            return
        
        self.result = {
            'visit_id': self.visit.id,
            'medicine_id': medicine.id,
            'dosage': dosage,
            'frequency': frequency,
            'duration_days': duration,
            'notes': self.instructions_text.get("1.0", "end-1c").strip() or None
        }
        
        self.destroy()
