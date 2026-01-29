"""
Main Window - Application Container
"""
import customtkinter as ctk
from datetime import date
from services import AppointmentService
from ui.components import PatientPanel, VisitPanel, TestPanel, AppointmentPanel, MedicinePanel, ImportPanel
import config


class MainWindow(ctk.CTkFrame):
    """Main application window with sidebar navigation"""
    
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.appointment_service = AppointmentService()
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create content area
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Initialize panels
        self.current_panel = None
        self.panels = {}
        
        # Show dashboard by default
        self.show_dashboard()
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color="#1a1a1a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Logo/Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar,
            text="🏥 Phòng Khám",
            font=("Arial", 20, "bold"),
            text_color="white"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=30)
        
        # Navigation buttons
        self.nav_buttons = []
        
        buttons_config = [
            ("📊 Trang Chủ", self.show_dashboard),
            ("👤 Bệnh Nhân", self.show_patients),
            ("🩺 Khám Bệnh", self.show_visits),
            ("🧪 Xét Nghiệm", self.show_tests),
            ("💊 Thuốc", self.show_medicine),
            ("📅 Lịch Hẹn", self.show_appointments),
            ("📥 Nhập Dữ Liệu", self.show_import),
        ]
        
        for idx, (text, command) in enumerate(buttons_config, start=1):
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                width=180,
                height=45,
                corner_radius=8,
                font=("Arial", 14),
                fg_color="transparent",
                hover_color="#2a2a2a",
                anchor="w",
                text_color="white"
            )
            btn.grid(row=idx, column=0, padx=10, pady=5)
            self.nav_buttons.append(btn)
        
        # Version info at bottom
        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text=f"v{config.APP_VERSION}",
            font=("Arial", 10),
            text_color="gray"
        )
        self.version_label.grid(row=11, column=0, padx=20, pady=10, sticky="s")
    
    def clear_content(self):
        """Clear current content"""
        if self.current_panel:
            self.current_panel.destroy()
            self.current_panel = None
    
    def show_dashboard(self):
        """Show dashboard with statistics and alerts"""
        self.clear_content()
        
        dashboard = ctk.CTkFrame(self.content_frame)
        dashboard.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        dashboard.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Title
        title = ctk.CTkLabel(
            dashboard,
            text="📊 Trang Chủ",
            font=("Arial", 24, "bold")
        )
        title.grid(row=0, column=0, columnspan=3, padx=20, pady=20, sticky="w")
        
        # Statistics cards
        try:
            from services import PatientService, VisitService
            patient_service = PatientService()
            visit_service = VisitService()
            
            patient_count = patient_service.get_patient_count()
            visit_count = visit_service.get_visit_count()
            overdue_count = self.appointment_service.get_overdue_count()
            
            # Patient count card
            patient_card = self.create_stat_card(
                dashboard, 
                "Tổng Bệnh Nhân", 
                str(patient_count),
                "#2196F3"
            )
            patient_card.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
            
            # Visit count card
            visit_card = self.create_stat_card(
                dashboard,
                "Tổng Lượt Khám",
                str(visit_count),
                "#4CAF50"
            )
            visit_card.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
            
            # Overdue appointments card
            overdue_card = self.create_stat_card(
                dashboard,
                "Lịch Hẹn Quá Hạn",
                str(overdue_count),
                "#F44336" if overdue_count > 0 else "#9E9E9E"
            )
            overdue_card.grid(row=1, column=2, padx=10, pady=10, sticky="ew")
            
            # Alerts section
            if overdue_count > 0:
                alerts_frame = ctk.CTkFrame(dashboard, fg_color="#FFF3E0", corner_radius=10)
                alerts_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=20, sticky="ew")
                
                alert_label = ctk.CTkLabel(
                    alerts_frame,
                    text=f"⚠️ Có {overdue_count} lịch hẹn quá hạn. Vui lòng kiểm tra!",
                    font=("Arial", 14, "bold"),
                    text_color="#E65100"
                )
                alert_label.pack(padx=20, pady=15)
                
                view_btn = ctk.CTkButton(
                    alerts_frame,
                    text="Xem Chi Tiết",
                    command=self.show_appointments,
                    fg_color="#FF9800",
                    hover_color="#F57C00"
                )
                view_btn.pack(pady=(0, 15))
            
        except Exception as e:
            error_label = ctk.CTkLabel(
                dashboard,
                text=f"Lỗi tải dữ liệu: {str(e)}",
                font=("Arial", 14),
                text_color="red"
            )
            error_label.grid(row=1, column=0, columnspan=3, padx=20, pady=20)
        
        self.current_panel = dashboard
    
    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 14),
            text_color="white"
        )
        title_label.pack(padx=20, pady=(20, 5), anchor="w")
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 32, "bold"),
            text_color="white"
        )
        value_label.pack(padx=20, pady=(0, 20), anchor="w")
        
        return card
    
    def show_patients(self):
        """Show patient management panel"""
        self.clear_content()
        panel = PatientPanel(self.content_frame)
        panel.grid(row=0, column=0, sticky="nsew")
        self.current_panel = panel
    
    def show_visits(self):
        """Show visit management panel"""
        self.clear_content()
        panel = VisitPanel(self.content_frame)
        panel.grid(row=0, column=0, sticky="nsew")
        self.current_panel = panel
    
    def show_tests(self):
        """Show test management panel"""
        self.clear_content()
        panel = TestPanel(self.content_frame)
        panel.grid(row=0, column=0, sticky="nsew")
        self.current_panel = panel
    
    def show_medicine(self):
        """Show medicine management panel"""
        self.clear_content()
        panel = MedicinePanel(self.content_frame)
        panel.grid(row=0, column=0, sticky="nsew")
        self.current_panel = panel
    
    def show_appointments(self):
        """Show appointment management panel"""
        self.clear_content()
        panel = AppointmentPanel(self.content_frame)
        panel.grid(row=0, column=0, sticky="nsew")
        self.current_panel = panel
    
    def show_import(self):
        """Show data import panel"""
        self.clear_content()
        panel = ImportPanel(self.content_frame)
        panel.grid(row=0, column=0, sticky="nsew")
        self.current_panel = panel
