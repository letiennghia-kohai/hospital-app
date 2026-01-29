
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
1. Chọn loại dữ liệu muốn nhập (Bệnh Nhân hoặc Kết Quả Xét Nghiệm)
2. Xem format yêu cầu bên dưới
3. Chuẩn bị file CSV hoặc Excel (.csv, .xlsx, .xls) theo đúng format
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
            format_text = """
CÁC CỘT BẮT BUỘC (*):
  • patient_code (*): Mã bệnh nhân (VD: BN001, BN002...)
  • full_name (*): Họ và tên đầy đủ (VD: Nguyễn Văn A)
  • date_of_birth (*): Ngày sinh (dd/mm/yyyy) (VD: 15/03/1990)
  • gender (*): Giới tính (Nam hoặc Nữ)

CÁC CỘT TÙY CHỌN:
  • phone: Số điện thoại (VD: 0912345678)
  • address: Địa chỉ
  • email: Email
  • blood_type: Nhóm máu (A, B, AB, O)
  • allergies: Dị ứng
  • medical_history: Tiền sử bệnh

VÍ DỤ FILE CSV:
patient_code,full_name,date_of_birth,gender,phone,address
BN001,Nguyễn Văn A,15/03/1990,Nam,0912345678,Hà Nội
BN002,Trần Thị B,20/05/1985,Nữ,0987654321,TP.HCM
            """
        else:  # test_results
            format_text = """
CÁC CỘT BẮT BUỘC (*):
  • patient_code (*): Mã bệnh nhân (VD: BN001)
  • test_type (*): Tên loại xét nghiệm (phải tồn tại trong hệ thống)
  • test_date (*): Ngày xét nghiệm (dd/mm/yyyy)
  • result_value hoặc result_text (*): Kết quả số hoặc kết quả định tính

CÁC CỘT TÙY CHỌN:
  • unit: Đơn vị (nếu có kết quả số)
  • notes: Ghi chú

VÍ DỤ FILE CSV (Kết quả số):
patient_code,test_type,test_date,result_value,unit,notes
BN001,Glucose,25/01/2026,120,mg/dL,Bình thường
BN002,Hemoglobin,26/01/2026,14.5,g/dL,

VÍ DỤ FILE CSV (Kết quả định tính):
patient_code,test_type,test_date,result_text,notes
BN001,HBsAg,25/01/2026,Âm tính,
BN002,HIV,26/01/2026,Âm tính,
            """
        
        format_label = ctk.CTkLabel(
            self.format_frame,
            text=format_text.strip(),
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
        file_path = filedialog.askopenfilename(
            title="Chọn File CSV hoặc Excel",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx *.xls"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            filename = file_path.split("/")[-1]
            self.file_label.configure(text=f"✓ {filename}", text_color="green")
            self.load_preview()
