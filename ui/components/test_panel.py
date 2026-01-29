"""
Test Management Panel with Timeline View
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import date
from services import TestService, PatientService, VisitService
from utils import Formatters, ChartHelper
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import config


class TestPanel(ctk.CTkFrame):
    """Panel for test management and timeline view"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.test_service = TestService()
        self.patient_service = PatientService()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI
        self.create_header()
        self.create_tabs()
    
    def create_header(self):
        """Create header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        title = ctk.CTkLabel(
            header,
            text="🧪 Quản Lý Xét Nghiệm",
            font=("Arial", 24, "bold")
        )
        title.pack(side="left", padx=10, pady=10)
    
    def create_tabs(self):
        """Create tabbed interface"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add tabs
        self.tabview.add("Loại Xét Nghiệm")
        self.tabview.add("Theo Dõi Kết Quả")
        
        # Test types tab
        self.create_test_types_tab()
        
        # Timeline tab
        self.create_timeline_tab()
    
    def create_test_types_tab(self):
        """Create test types management tab"""
        tab = self.tabview.tab("Loại Xét Nghiệm")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # Add button
        add_btn = ctk.CTkButton(
            tab,
            text="➕ Thêm Loại Xét Nghiệm",
            command=self.add_test_type,
            fg_color="#4CAF50"
        )
        add_btn.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        
        # List
        self.test_types_list = ctk.CTkScrollableFrame(tab)
        self.test_types_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        self.load_test_types()
    
    def load_test_types(self):
        """Load test types"""
        for widget in self.test_types_list.winfo_children():
            widget.destroy()
        
        test_types = self.test_service.get_all_test_types()
        
        for idx, tt in enumerate(test_types):
            card = ctk.CTkFrame(self.test_types_list, fg_color="#f0f0f0", corner_radius=8)
            card.pack(fill="x", pady=5, padx=5)
            
            info = ctk.CTkLabel(
                card,
                text=f"🧪 {tt.name} | {tt.category or 'N/A'} | {tt.unit or 'N/A'}",
                font=("Arial", 13),
                anchor="w"
            )
            info.pack(side="left", padx=15, pady=10, fill="x", expand=True)
            
            edit_btn = ctk.CTkButton(
                card,
                text="✏️",
                width=40,
                command=lambda t=tt: self.edit_test_type(t)
            )
            edit_btn.pack(side="right", padx=5, pady=5)
    
    def add_test_type(self):
        """Add new test type"""
        dialog = TestTypeDialog(self, title="Thêm Loại Xét Nghiệm")
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.test_service.create_test_type(**dialog.result)
                messagebox.showinfo("Thành Công", "Đã thêm loại xét nghiệm")
                self.load_test_types()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
    
    def edit_test_type(self, test_type):
        """Edit test type"""
        dialog = TestTypeDialog(self, title="Sửa Loại Xét Nghiệm", test_type=test_type)
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.test_service.update_test_type(test_type.id, **dialog.result)
                messagebox.showinfo("Thành Công", "Đã cập nhật")
                self.load_test_types()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
    
    def create_timeline_tab(self):
        """Create timeline view tab"""
        tab = self.tabview.tab("Theo Dõi Kết Quả")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)
        
        # Selection frame
        select_frame = ctk.CTkFrame(tab, fg_color="transparent")
        select_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Patient selection
        ctk.CTkLabel(select_frame, text="Bệnh Nhân:", font=("Arial", 13, "bold")).pack(
            side="left", padx=5
        )
        
        patients = self.patient_service.get_all_patients(limit=500)
        patient_names = [f"{p.patient_code} - {p.full_name}" for p in patients]
        
        self.timeline_patient_combo = ctk.CTkComboBox(
            select_frame,
            values=patient_names,
            width=300,
            command=self.on_patient_selected
        )
        self.timeline_patient_combo.pack(side="left", padx=10)
        self.patients_list = patients
        
        # Test type selection
        ctk.CTkLabel(select_frame, text="Loại XN:", font=("Arial", 13, "bold")).pack(
            side="left", padx=5
        )
        
        self.timeline_test_combo = ctk.CTkComboBox(select_frame, values=[], width=250)
        self.timeline_test_combo.pack(side="left", padx=10)
        
        # View button
        view_btn = ctk.CTkButton(
            select_frame,
            text="📊 Xem Timeline",
            command=self.show_timeline,
            fg_color="#2196F3"
        )
        view_btn.pack(side="left", padx=10)
        
        # Results frame
        self.timeline_results = ctk.CTkScrollableFrame(tab)
        self.timeline_results.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
    
    def on_patient_selected(self, choice):
        """When patient is selected, load their test types"""
        selected_text = self.timeline_patient_combo.get()
        
        # Find patient by matching text
        patient = None
        for p in self.patients_list:
            if f"{p.patient_code} - {p.full_name}" == selected_text:
                patient = p
                break
        
        if not patient:
            return
        
        # Get all test types this patient has
        latest_tests = self.test_service.get_patient_all_tests_latest(patient.id)
        test_names = list(set([t['test_name'] for t in latest_tests]))
        
        self.timeline_test_combo.configure(values=test_names)
        if test_names:
            self.timeline_test_combo.set(test_names[0])
    
    def show_timeline(self):
        """Show timeline for selected patient and test"""
        # Clear results
        for widget in self.timeline_results.winfo_children():
            widget.destroy()
        
        # Get selections
        selected_text = self.timeline_patient_combo.get()
        
        # Find patient by matching text
        patient = None
        for p in self.patients_list:
            if f"{p.patient_code} - {p.full_name}" == selected_text:
                patient = p
                break
        
        if not patient:
            messagebox.showwarning("Cảnh Báo", "Vui lòng chọn bệnh nhân")
            return
        
        test_name = self.timeline_test_combo.get()
        
        if not test_name:
            messagebox.showwarning("Cảnh Báo", "Vui lòng chọn loại xét nghiệm")
            return
        
        # Get test type
        test_type = self.test_service.get_test_type_by_name(test_name)
        if not test_type:
            messagebox.showerror("Lỗi", "Không tìm thấy loại xét nghiệm")
            return
        
        # Get timeline data
        timeline = self.test_service.get_patient_test_timeline(patient.id, test_type.id)
        
        if not timeline:
            no_data = ctk.CTkLabel(
                self.timeline_results,
                text="Không có dữ liệu",
                font=("Arial", 14),
                text_color="gray"
            )
            no_data.pack(pady=50)
            return
        
        # Display table
        self.display_timeline_table(timeline, test_type)
        
        # Display chart
        self.display_timeline_chart(timeline, test_type)
    
    def display_timeline_table(self, timeline, test_type):
        """Display timeline as table"""
        table_frame = ctk.CTkFrame(self.timeline_results, fg_color="#f9f9f9", corner_radius=10)
        table_frame.pack(fill="x", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            table_frame,
            text=f"📋 Lịch Sử Kết Quả: {test_type.name}",
            font=("Arial", 16, "bold")
        )
        title.pack(padx=15, pady=15, anchor="w")
        
        for item in reversed(timeline):  # Show newest first
            row = ctk.CTkFrame(table_frame, fg_color="white", corner_radius=5)
            row.pack(fill="x", padx=15, pady=5)
            
            date_str = Formatters.format_date(item['date'])
            value_str = str(item['value']) if item['value'] else item.get('text', 'N/A')
            unit_str = item.get('unit', test_type.unit or '')
            
            text = f"📅 {date_str} | 📊 {value_str} {unit_str}"
            
            label = ctk.CTkLabel(row, text=text, font=("Arial", 13), anchor="w")
            label.pack(padx=10, pady=8, anchor="w")
    
    def display_timeline_chart(self, timeline, test_type):
        """Display timeline as chart"""
        chart_frame = ctk.CTkFrame(self.timeline_results, fg_color="white", corner_radius=10)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(
            chart_frame,
            text=f"📈 Biểu Đồ: {test_type.name}",
            font=("Arial", 16, "bold")
        )
        title.pack(padx=15, pady=15, anchor="w")
        
        # Create chart
        fig = ChartHelper.create_timeline_chart(
            timeline,
            test_type.name,
            test_type.normal_range_min,
            test_type.normal_range_max,
            figsize=(10, 5)
        )
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)


class TestTypeDialog(ctk.CTkToplevel):
    """Dialog for test type"""
    
    def __init__(self, master, title="Loại Xét Nghiệm", test_type=None):
        super().__init__(master)
        
        self.title(title)
        self.geometry("500x500")
        
        self.test_type = test_type
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
        
        # Name
        ctk.CTkLabel(form, text="Tên *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.name_entry = ctk.CTkEntry(form, width=300)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.test_type:
            self.name_entry.insert(0, self.test_type.name)
        row += 1
        
        # Category
        ctk.CTkLabel(form, text="Phân Loại:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.category_combo = ctk.CTkComboBox(form, values=config.TEST_CATEGORIES)
        self.category_combo.grid(row=row, column=1, sticky="ew", pady=10)
        if self.test_type:
            self.category_combo.set(self.test_type.category or "")
        row += 1
        
        # Unit
        ctk.CTkLabel(form, text="Đơn Vị:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.unit_entry = ctk.CTkEntry(form)
        self.unit_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.test_type:
            self.unit_entry.insert(0, self.test_type.unit or "")
        row += 1
        
        # Normal range min
        ctk.CTkLabel(form, text="Giới Hạn Dưới:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.min_entry = ctk.CTkEntry(form)
        self.min_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.test_type and self.test_type.normal_range_min:
            self.min_entry.insert(0, str(self.test_type.normal_range_min))
        row += 1
        
        # Normal range max
        ctk.CTkLabel(form, text="Giới Hạn Trên:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.max_entry = ctk.CTkEntry(form)
        self.max_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.test_type and self.test_type.normal_range_max:
            self.max_entry.insert(0, str(self.test_type.normal_range_max))
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
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên")
            return
        
        # Parse numbers
        try:
            min_val = float(self.min_entry.get()) if self.min_entry.get().strip() else None
            max_val = float(self.max_entry.get()) if self.max_entry.get().strip() else None
        except ValueError:
            messagebox.showerror("Lỗi", "Giới hạn phải là số")
            return
        
        self.result = {
            'name': name,
            'category': self.category_combo.get() or None,
            'unit': self.unit_entry.get().strip() or None,
            'normal_range_min': min_val,
            'normal_range_max': max_val
        }
        
        self.destroy()
