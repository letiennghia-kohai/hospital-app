"""
Medicine and Prescription Management Panel
"""
import customtkinter as ctk
from tkinter import messagebox
from services import MedicineService
import config


class MedicinePanel(ctk.CTkFrame):
    """Panel for medicine catalog and prescription management"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.medicine_service = MedicineService()
        
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create UI
        self.create_header()
        self.create_content()
        
        # Load data
        self.load_medicines()
    
    def create_header(self):
        """Create header"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        title = ctk.CTkLabel(
            header,
            text="💊 Quản Lý Thuốc",
            font=("Arial", 24, "bold")
        )
        title.pack(side="left", padx=10, pady=10)
        
        add_btn = ctk.CTkButton(
            header,
            text="➕ Thêm Thuốc",
            command=self.add_medicine,
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
        content.grid_rowconfigure(1, weight=1)
        
        # Search bar
        search_frame = ctk.CTkFrame(content, fg_color="transparent")
        search_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Tìm thuốc theo tên...",
            width=400,
            height=40
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.search_medicines())
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Tìm Kiếm",
            command=self.search_medicines,
            width=120,
            height=40
        )
        search_btn.pack(side="left")
        
        # Medicine list
        self.list_frame = ctk.CTkScrollableFrame(content)
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.list_frame.grid_columnconfigure(0, weight=1)
    
    def load_medicines(self, keyword=""):
        """Load medicines"""
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        
        medicines = self.medicine_service.search_medicines(keyword, active_only=True)
        
        if not medicines:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Không tìm thấy thuốc nào",
                font=("Arial", 14),
                text_color="gray"
            )
            no_data.grid(row=0, column=0, pady=50)
            return
        
        # Group by category
        by_category = {}
        for med in medicines:
            cat = med.category or "Khác"
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(med)
        
        # Display by category
        row = 0
        for category, meds in sorted(by_category.items()):
            # Category header
            cat_label = ctk.CTkLabel(
                self.list_frame,
                text=f"📁 {category}",
                font=("Arial", 16, "bold"),
                anchor="w"
            )
            cat_label.grid(row=row, column=0, sticky="ew", padx=10, pady=(15, 5))
            row += 1
            
            # Medicines in category
            for med in meds:
                self.create_medicine_card(med, row)
                row += 1
    
    def create_medicine_card(self, medicine, row):
        """Create medicine card"""
        card = ctk.CTkFrame(self.list_frame, fg_color="#f0f0f0", corner_radius=8)
        card.grid(row=row, column=0, sticky="ew", pady=3, padx=5)
        card.grid_columnconfigure(1, weight=1)
        
        # Medicine info
        name_label = ctk.CTkLabel(
            card,
            text=f"💊 {medicine.name}",
            font=("Arial", 14, "bold"),
            anchor="w"
        )
        name_label.grid(row=0, column=0, sticky="w", padx=15, pady=10)
        
        if medicine.unit:
            unit_label = ctk.CTkLabel(
                card,
                text=f"Đơn vị: {medicine.unit}",
                font=("Arial", 11),
                text_color="gray",
                anchor="w"
            )
            unit_label.grid(row=0, column=1, sticky="w", padx=10, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=10, pady=10)
        
        edit_btn = ctk.CTkButton(
            btn_frame,
            text="✏️ Sửa",
            command=lambda m=medicine: self.edit_medicine(m),
            width=80,
            fg_color="#FF9800"
        )
        edit_btn.pack(side="left", padx=2)
        
        deactivate_btn = ctk.CTkButton(
            btn_frame,
            text="🗑️ Xóa",
            command=lambda m=medicine: self.deactivate_medicine(m),
            width=80,
            fg_color="#F44336"
        )
        deactivate_btn.pack(side="left", padx=2)
    
    def search_medicines(self):
        """Search medicines"""
        keyword = self.search_entry.get()
        self.load_medicines(keyword)
    
    def add_medicine(self):
        """Add new medicine"""
        dialog = MedicineDialog(self, title="Thêm Thuốc Mới")
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.medicine_service.create_medicine(**dialog.result)
                messagebox.showinfo("Thành Công", "Đã thêm thuốc mới")
                self.load_medicines()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm: {str(e)}")
    
    def edit_medicine(self, medicine):
        """Edit medicine"""
        dialog = MedicineDialog(self, title="Sửa Thông Tin Thuốc", medicine=medicine)
        dialog.wait_window()
        
        if dialog.result:
            try:
                self.medicine_service.update_medicine(medicine.id, **dialog.result)
                messagebox.showinfo("Thành Công", "Đã cập nhật thông tin")
                self.load_medicines()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {str(e)}")
    
    def deactivate_medicine(self, medicine):
        """Deactivate medicine"""
        if messagebox.askyesno("Xác Nhận", f"Bạn có chắc muốn xóa thuốc {medicine.name}?"):
            try:
                self.medicine_service.deactivate_medicine(medicine.id)
                messagebox.showinfo("Thành Công", "Đã xóa thuốc")
                self.load_medicines()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {str(e)}")


class MedicineDialog(ctk.CTkToplevel):
    """Dialog for medicine"""
    
    def __init__(self, master, title="Thuốc", medicine=None):
        super().__init__(master)
        
        self.title(title)
        self.geometry("500x450")
        
        self.medicine = medicine
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
        ctk.CTkLabel(form, text="Tên Thuốc *:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.name_entry = ctk.CTkEntry(form, width=300)
        self.name_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.medicine:
            self.name_entry.insert(0, self.medicine.name)
        row += 1
        
        # Category
        ctk.CTkLabel(form, text="Phân Loại:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.category_combo = ctk.CTkComboBox(form, values=config.MEDICINE_CATEGORIES)
        self.category_combo.grid(row=row, column=1, sticky="ew", pady=10)
        if self.medicine:
            self.category_combo.set(self.medicine.category or "")
        row += 1
        
        # Unit
        ctk.CTkLabel(form, text="Đơn Vị:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="w", pady=10
        )
        self.unit_entry = ctk.CTkEntry(form, placeholder_text="viên, gói, ml...")
        self.unit_entry.grid(row=row, column=1, sticky="ew", pady=10)
        if self.medicine:
            self.unit_entry.insert(0, self.medicine.unit or "")
        row += 1
        
        # Description
        ctk.CTkLabel(form, text="Mô Tả:", font=("Arial", 13, "bold")).grid(
            row=row, column=0, sticky="nw", pady=10
        )
        self.desc_text = ctk.CTkTextbox(form, height=100)
        self.desc_text.grid(row=row, column=1, sticky="ew", pady=10)
        if self.medicine:
            self.desc_text.insert("1.0", self.medicine.description or "")
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
            messagebox.showerror("Lỗi", "Vui lòng nhập tên thuốc")
            return
        
        self.result = {
            'name': name,
            'category': self.category_combo.get() or None,
            'unit': self.unit_entry.get().strip() or None,
            'description': self.desc_text.get("1.0", "end-1c").strip() or None
        }
        
        self.destroy()
