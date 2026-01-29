"""
Data Import Panel
"""
import customtkinter as ctk
from tkinter import messagebox, filedialog
import pandas as pd
from services import ImportService
import config


class ImportPanel(ctk.CTkFrame):
    """Panel for importing data from CSV/Excel files"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.import_service = ImportService()
        self.selected_file = None
        self.preview_data = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_header()
        self.create_content()
    
    def create_header(self):
        """Create header section"""
        header = ctk.CTkFrame(self, fg_color="#2196F3", corner_radius=10)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            header,
            text="📥 Nhập Dữ Liệu",
            font=("Arial", 24, "bold"),
            text_color="white"
        )
        title.pack(padx=20, pady=20)
    
    def create_content(self):
        """Create main content area"""
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        content.grid_columnconfigure(0, weight=1)
        
        # Instructions with detailed format
        self.create_instructions(content)
        
        # Import type selection
        type_frame = ctk.CTkFrame(content)
        type_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(
            type_frame,
            text="Loại Dữ Liệu:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        self.import_type = ctk.StringVar(value="patients")
        
        types = [
            ("Bệnh Nhân", "patients"),
            ("Thuốc", "medicines"),
            ("Loại Xét Nghiệm", "test_types"),
            ("Lần Khám", "visits"),
            ("Kết Quả Xét Nghiệm", "test_results"),
        ]
        
        for text, value in types:
            rb = ctk.CTkRadioButton(
                type_frame,
                text=text,
                variable=self.import_type,
                value=value,
                font=("Arial", 13),
                command=self.on_type_changed
            )
            rb.pack(anchor="w", padx=30, pady=5)
        
        # File selection
        file_frame = ctk.CTkFrame(content)
        file_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(
            file_frame,
            text="Chọn File:",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=10)
        
        btn_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.file_label = ctk.CTkLabel(
            btn_frame,
            text="Chưa chọn file",
            font=("Arial", 12),
            text_color="gray"
        )
        self.file_label.pack(side="left", padx=10)
        
        select_btn = ctk.CTkButton(
            btn_frame,
            text="📁 Chọn File",
            command=self.select_file,
            width=120,
            fg_color="#4CAF50"
        )
        select_btn.pack(side="left", padx=5)
        
        # Format requirements panel
        self.format_frame = ctk.CTkFrame(content, fg_color="#FFF9C4", corner_radius=10)
        self.format_frame.pack(fill="x", pady=20, padx=20)
        self.update_format_instructions()
        
        # Preview area
        preview_label = ctk.CTkLabel(
            content,
            text="Xem Trước Dữ Liệu (10 dòng đầu):",
            font=("Arial", 14, "bold")
        )
        preview_label.pack(anchor="w", padx=30, pady=(20, 10))
        
        self.preview_frame = ctk.CTkFrame(content)
        self.preview_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.preview_text = ctk.CTkTextbox(self.preview_frame, height=200)
        self.preview_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.preview_text.insert("1.0", "Chưa có dữ liệu để xem trước...")
        self.preview_text.configure(state="disabled")
        
        # Import button
        import_btn = ctk.CTkButton(
            content,
            text="📥 Nhập Dữ Liệu",
            command=self.import_data,
            height=45,
            font=("Arial", 14, "bold"),
            fg_color="#4CAF50",
            hover_color="#45A049"
        )
        import_btn.pack(pady=20)
    
    def create_instructions(self, parent):
        """Create general instructions section"""
        instructions = ctk.CTkFrame(parent, fg_color="#E3F2FD", corner_radius=10)
        instructions.pack(fill="x", pady=20, padx=20)
        
        inst_title = ctk.CTkLabel(
            instructions,
            text="📋 Hướng Dẫn Sử Dụng",
            font=("Arial", 16, "bold"),
            text_color="#1976D2"
        )
        inst_title.pack(padx=20, pady=(15, 10), anchor="w")
        
        inst_text = """
1. Chọn loại dữ liệu muốn nhập (Bệnh Nhân)
2. Xem format yêu cầu bên dưới (màu vàng)
3. Chuẩn bị file CSV hoặc Excel (.csv, xlsx, .xls) theo đúng format
4. Chọn file và xem trước dữ liệu
5. Ánh xạ các cột trong file với các trường của hệ thống
6. Nhấn "Nhập Dữ Liệu" để hoàn tất

⚠️ Lưu ý: 
  • File PHẢI có dòng header (dòng đầu tiên là tên cột)
  • Các cột được đánh dấu (*) là BẮT BUỘC
  • Định dạng ngày: dd/mm/yyyy (VD: 25/01/2026)
        """
        
        inst_label = ctk.CTkLabel(
            instructions,
            text=inst_text.strip(),
            font=("Arial", 12),
            text_color="#424242",
            justify="left"
        )
        inst_label.pack(padx=20, pady=(5, 15), anchor="w")
    
    def update_format_instructions(self):
        """Update format instructions based on import type"""
        for widget in self.format_frame.winfo_children():
            widget.destroy()
        
        format_title = ctk.CTkLabel(
            self.format_frame,
            text="📄 Format File Yêu Cầu",
            font=("Arial", 15, "bold"),
            text_color="#F57F17"
        )
        format_title.pack(padx=20, pady=(15, 10), anchor="w")
        
        import_type = self.import_type.get()
        
        if import_type == "patients":
            format_text = """CÁC CỘT BẮT BUỘC (*):
  • patient_code (*): Mã bệnh nhân (VD: BN001, BN002...)
  • full_name (*): Họ và tên đầy đủ (VD: Nguyễn Văn A)
  • date_of_birth (*): Ngày sinh dd/mm/yyyy (VD: 15/03/1990)
  • gender (*): Giới tính (Nam hoặc Nữ)

CÁC CỘT TÙY CHỌN:
  • phone, address, email, blood_type, allergies, medical_history

VÍ DỤ:
patient_code,full_name,date_of_birth,gender,phone
BN001,Nguyễn Văn A,15/03/1990,Nam,0912345678"""
        
        elif import_type == "medicines":
            format_text = """CÁC CỘT BẮT BUỘC (*):
  • name (*): Tên thuốc (VD: Paracetamol, Amoxicillin)

CÁC CỘT TÙY CHỌN:
  • category: Phân loại (VD: Kháng sinh, Giảm đau)
  • unit: Đơn vị (VD: viên, chai, ống)
  • usage: Hướng dẫn sử dụng
  • notes: Ghi chú

VÍ DỤ:
name,category,unit,usage
Paracetamol,Giảm đau,viên,Uống sau ăn
Amoxicillin,Kháng sinh,viên,Uống 3 lần/ngày"""
        
        elif import_type == "test_types":
            format_text = """CÁC CỘT BẮT BUỘC (*):
  • name (*): Tên xét nghiệm (VD: Glucose, Hemoglobin)
  • unit (*): Đơn vị (VD: mg/dL, g/dL)

CÁC CỘT TÙY CHỌN:
  • normal_range_min: Giới hạn dưới bình thường
  • normal_range_max: Giới hạn trên bình thường
  • notes: Ghi chú

VÍ DỤ:
name,unit,normal_range_min,normal_range_max
Glucose,mg/dL,70,110
Hemoglobin,g/dL,12,16"""
        
        elif import_type == "visits":
            format_text = """CÁC CỘT BẮT BUỘC (*):
  • patient_code (*): Mã bệnh nhân (VD: BN001)
  • visit_date (*): Ngày khám dd/mm/yyyy (VD: 25/01/2026)

CÁC CỘT TÙY CHỌN:
  • symptoms: Triệu chứng
  • diagnosis: Chẩn đoán
  • conclusion: Kết luận
  • notes: Ghi chú

VÍ DỤ:
patient_code,visit_date,symptoms,diagnosis
BN001,25/01/2026,Sốt cao,Cảm cúm"""
        
        elif import_type == "test_results":
            format_text = """CÁC CỘT BẮT BUỘC (*):
  • patient_code (*): Mã bệnh nhân (VD: BN001)
  • test_type_name (*): Tên loại XN (phải tồn tại)
  • test_date (*): Ngày XN dd/mm/yyyy
  • result_value hoặc result_text (*): Kết quả

CÁC CỘT TÙY CHỌN:
  • notes: Ghi chú

VÍ DỤ (Kết quả số):
patient_code,test_type_name,test_date,result_value
BN001,Glucose,25/01/2026,105

VÍ DỤ (Kết quả text):
patient_code,test_type_name,test_date,result_text
BN001,HIV,25/01/2026,Âm tính"""
        
        else:
            format_text = "Chọn loại dữ liệu để xem format yêu cầu"
        
        format_label = ctk.CTkLabel(
            self.format_frame,
            text=format_text,
            font=("Courier New", 11),
            text_color="#424242",
            justify="left"
        )
        format_label.pack(padx=20, pady=(5, 15), anchor="w")
    
    def on_type_changed(self):
        """Handle import type change"""
        self.update_format_instructions()
    
    def select_file(self):
        """Open file dialog to select CSV/Excel file"""
        filetypes = [
            ("CSV files", "*.csv"),
            ("Excel files", "*.xlsx *.xls"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Chọn File",
            filetypes=filetypes
        )
        
        if filename:
            # Validate file
            validation = self.import_service.validate_file(filename)
            
            if not validation['valid']:
                messagebox.showerror("Lỗi", f"File không hợp lệ: {validation['error']}")
                return
            
            self.selected_file = filename
            self.file_label.configure(text=filename.split("/")[-1])
            
            # Show preview
            self.show_preview(filename, validation)
    
    def show_preview(self, filename, validation):
        """Show file preview"""
        preview_df = self.import_service.preview_data(filename, rows=10)
        
        if preview_df is None:
            return
        
        # Format preview
        preview_text = f"Tổng số dòng: {validation['row_count']}\n"
        preview_text += f"Số cột: {validation['column_count']}\n"
        preview_text += f"Các cột: {', '.join(validation['columns'])}\n\n"
        preview_text += "10 dòng đầu tiên:\n"
        preview_text += "=" * 80 + "\n"
        preview_text += preview_df.to_string()
        
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", preview_text)
        self.preview_text.configure(state="disabled")
    
    def import_data(self):
        """Import data"""
        if not self.selected_file:
            messagebox.showwarning("Cảnh Báo", "Vui lòng chọn file")
            return
        
        import_type = self.import_type.get()
        
        if import_type == "patients":
            self.import_patients()
        elif import_type == "medicines":
            self.import_medicines()
        elif import_type == "test_types":
            self.import_test_types()
        elif import_type == "visits":
            self.import_visits()
        elif import_type == "test_results":
            self.import_test_results()
        else:
            messagebox.showinfo("Thông Báo", f"Tính năng nhập {import_type} đang được phát triển")
    
    
    def import_patients(self):
        """Import patients from file"""
        dialog = ColumnMappingDialog(
            self,
            title="Ánh Xạ Cột - Bệnh Nhân",
            file_path=self.selected_file,
            import_type="patient"
        )
        dialog.wait_window()
        
        if not dialog.result:
            return
        
        try:
            result = self.import_service.import_patients(
                self.selected_file,
                dialog.result,
                skip_duplicates=True
            )
            self.show_import_result(result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập dữ liệu: {str(e)}")
    
    def import_medicines(self):
        """Import medicines from file"""
        dialog = ColumnMappingDialog(
            self,
            title="Ánh Xạ Cột - Thuốc",
            file_path=self.selected_file,
            import_type="medicine"
        )
        dialog.wait_window()
        
        if not dialog.result:
            return
        
        try:
            result = self.import_service.import_medicines(
                self.selected_file,
                dialog.result,
                skip_duplicates=True
            )
            self.show_import_result(result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập dữ liệu: {str(e)}")
    
    def import_test_types(self):
        """Import test types from file"""
        dialog = ColumnMappingDialog(
            self,
            title="Ánh Xạ Cột - Loại Xét Nghiệm",
            file_path=self.selected_file,
            import_type="test_type"
        )
        dialog.wait_window()
        
        if not dialog.result:
            return
        
        try:
            result = self.import_service.import_test_types(
                self.selected_file,
                dialog.result,
                skip_duplicates=True
            )
            self.show_import_result(result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập dữ liệu: {str(e)}")
    
    def import_visits(self):
        """Import visits from file"""
        dialog = ColumnMappingDialog(
            self,
            title="Ánh Xạ Cột - Lần Khám",
            file_path=self.selected_file,
            import_type="visit"
        )
        dialog.wait_window()
        
        if not dialog.result:
            return
        
        try:
            result = self.import_service.import_visits(
                self.selected_file,
                dialog.result
            )
            self.show_import_result(result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập dữ liệu: {str(e)}")
    
    def import_test_results(self):
        """Import test results from file"""
        dialog = ColumnMappingDialog(
            self,
            title="Ánh Xạ Cột - Kết Quả XN",
            file_path=self.selected_file,
            import_type="test_result"
        )
        dialog.wait_window()
        
        if not dialog.result:
            return
        
        try:
            result = self.import_service.import_test_results_batch(
                self.selected_file,
                dialog.result
            )
            self.show_import_result(result)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể nhập dữ liệu: {str(e)}")
    
    def show_import_result(self, result):
        """Show import result message"""
        if result['success']:
            message = f"""
Nhập dữ liệu thành công!

Tổng số dòng: {result['total']}
Đã nhập: {result['imported']}
Bỏ qua: {result['skipped']}
            """
            
            if result['errors']:
                message += f"\n\nLỗi ({len(result['errors'])} dòng):\n"
                message += "\n".join(result['errors'][:5])
                if len(result['errors']) > 5:
                    message += f"\n... và {len(result['errors']) - 5} lỗi khác"
            
            messagebox.showinfo("Thành Công", message.strip())
        else:
            messagebox.showerror("Lỗi", result.get('error', 'Unknown error'))


class ColumnMappingDialog(ctk.CTkToplevel):
    """Dialog for mapping file columns to database fields"""
    
    def __init__(self, master, title="Ánh Xạ Cột", file_path=None, import_type="patient"):
        super().__init__(master)
        
        self.title(title)
        self.geometry("600x500")
        
        self.file_path = file_path
        self.import_type = import_type
        self.result = None
        
        self.import_service = ImportService()
        
        # Get columns from file
        self.file_columns = self.import_service.get_column_names(file_path)
        
        self.create_form()
        
        self.transient(master)
        self.grab_set()
    
    def create_form(self):
        """Create mapping form"""
        form = ctk.CTkScrollableFrame(self)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        form.grid_columnconfigure(1, weight=1)
        
        # Instructions
        inst = ctk.CTkLabel(
            form,
            text="Chọn cột trong file tương ứng với từng trường dữ liệu:",
            font=("Arial", 12),
            wraplength=500
        )
        inst.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # Field mappings based on import type
        if self.import_type == "patient":
            fields = {
                'patient_code': 'Mã Bệnh Nhân *',
                'full_name': 'Họ Tên *',
                'date_of_birth': 'Ngày Sinh',
                'gender': 'Giới Tính',
                'phone_number': 'Số Điện Thoại',
                'address': 'Địa Chỉ',
                'email': 'Email',
                'blood_type': 'Nhóm Máu',
                'allergies': 'Dị Ứng',
                'medical_history': 'Tiền Sử Bệnh',
                'notes': 'Ghi Chú'
            }
        elif self.import_type == "medicine":
            fields = {
                'name': 'Tên Thuốc *',
                'category': 'Phân Loại',
                'unit': 'Đơn Vị',
                'usage': 'Hướng Dẫn Sử Dụng',
                'notes': 'Ghi Chú'
            }
        elif self.import_type == "test_type":
            fields = {
                'name': 'Tên Xét Nghiệm *',
                'unit': 'Đơn Vị *',
                'normal_range_min': 'Giới Hạn Dưới',
                'normal_range_max': 'Giới Hạn Trên',
                'notes': 'Ghi Chú'
            }
        elif self.import_type == "visit":
            fields = {
                'patient_code': 'Mã Bệnh Nhân *',
                'visit_date': 'Ngày Khám *',
                'symptoms': 'Triệu Chứng',
                'diagnosis': 'Chẩn Đoán',
                'conclusion': 'Kết Luận',
                'notes': 'Ghi Chú'
            }
        elif self.import_type == "test_result":
            fields = {
                'patient_code': 'Mã Bệnh Nhân *',
                'test_type_name': 'Tên Loại XN *',
                'test_date': 'Ngày Xét Nghiệm *',
                'result_value': 'Kết Quả Số',
                'result_text': 'Kết Quả Text',
                'notes': 'Ghi Chú'
            }
        else:
            fields = {}
        
        self.mapping_combos = {}
        row = 1
        
        for field_key, field_label in fields.items():
            ctk.CTkLabel(
                form,
                text=field_label,
                font=("Arial", 13, "bold")
            ).grid(row=row, column=0, sticky="w", pady=10, padx=(0, 20))
            
            combo = ctk.CTkComboBox(
                form,
                values=["-- Không chọn --"] + self.file_columns,
                width=300
            )
            combo.grid(row=row, column=1, sticky="ew", pady=10)
            combo.set("-- Không chọn --")
            
            # Try to auto-match
            for col in self.file_columns:
                col_lower = col.lower()
                if any(keyword in col_lower for keyword in [
                    field_key.replace('_', ''),
                    field_label.lower().replace(' ', ''),
                    field_label.lower()
                ]):
                    combo.set(col)
                    break
            
            self.mapping_combos[field_key] = combo
            row += 1
        
        # Buttons
        btn_frame = ctk.CTkFrame(form, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        ctk.CTkButton(
            btn_frame,
            text="✅ Xác Nhận",
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
        """Save mapping"""
        mapping = {}
        
        for field_key, combo in self.mapping_combos.items():
            selected = combo.get()
            if selected and selected != "-- Không chọn --":
                mapping[field_key] = selected
        
        # Validate required fields
        if self.import_type == "patient":
            if 'patient_code' not in mapping or 'full_name' not in mapping:
                messagebox.showerror("Lỗi", "Vui lòng chọn Mã Bệnh Nhân và Họ Tên")
                return
        
        self.result = mapping
        self.destroy()
