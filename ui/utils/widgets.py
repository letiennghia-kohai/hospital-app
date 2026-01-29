"""
Reusable UI Widgets
Custom widgets for consistency across the application
"""
import customtkinter as ctk
from datetime import date
from typing import Callable, Any, List

class IconButton(ctk.CTkButton):
    """Button with standardized styling"""
    def __init__(self, master, text="", command=None, width=120, height=35, **kwargs):
        super().__init__(
            master, 
            text=text, 
            command=command,
            width=width, 
            height=height,
            corner_radius=8,
            font=("Arial", 13, "bold"),
            **kwargs
        )

class DataCard(ctk.CTkFrame):
    """Card for displaying data statistics"""
    def __init__(self, master, title: str, value: str, icon_text: str = "", color: str = "#2196F3"):
        super().__init__(master, corner_radius=10, fg_color=color)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self, 
            text=title, 
            font=("Arial", 14), 
            text_color="white"
        )
        self.title_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        
        self.value_label = ctk.CTkLabel(
            self, 
            text=str(value), 
            font=("Arial", 28, "bold"), 
            text_color="white"
        )
        self.value_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="w")
        
        if icon_text:
            self.icon_label = ctk.CTkLabel(
                self,
                text=icon_text,
                font=("Arial", 40),
                text_color="white",
                alpha=0.2
            )
            self.icon_label.place(relx=0.85, rely=0.5, anchor="center")

class FormLabel(ctk.CTkLabel):
    """Standard label for forms"""
    def __init__(self, master, text, **kwargs):
        super().__init__(
            master, 
            text=text, 
            font=("Arial", 13, "bold"),
            anchor="w",
            **kwargs
        )

class SearchBar(ctk.CTkFrame):
    """Search bar component with button"""
    def __init__(self, master, command: Callable[[str], None], placeholder: str = "Tìm kiếm...", **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.entry = ctk.CTkEntry(
            self, 
            placeholder_text=placeholder,
            width=300,
            height=35
        )
        self.entry.pack(side="left", padx=(0, 10))
        self.entry.bind("<Return>", lambda e: command(self.entry.get()))
        
        self.btn = IconButton(
            self, 
            text="Tìm", 
            width=80, 
            command=lambda: command(self.entry.get())
        )
        self.btn.pack(side="left")

    def get(self):
        return self.entry.get()

class ScrollableFrame(ctk.CTkScrollableFrame):
    """Standard scrollable frame"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

class Toast(ctk.CTkToplevel):
    """Notification toast"""
    def __init__(self, master, title: str, message: str, type: str = "info"):
        super().__init__(master)
        
        self.geometry("400x150")
        self.title(title)
        self.attributes("-topmost", True)
        
        # Center on screen
        # Note: Actual centering requires update_idletasks logic
        
        color = "#2196F3" if type == "info" else "#F44336" if type == "error" else "#4CAF50"
        
        self.frame = ctk.CTkFrame(self, fg_color=color, corner_radius=0)
        self.frame.pack(fill="both", expand=True)
        
        self.msg_label = ctk.CTkLabel(
            self.frame, 
            text=message, 
            font=("Arial", 14), 
            text_color="white", 
            wraplength=350
        )
        self.msg_label.pack(expand=True, padx=20, pady=20)
        
        self.ok_btn = ctk.CTkButton(
            self.frame, 
            text="OK", 
            fg_color="white", 
            text_color=color, 
            hover_color="#EEE",
            command=self.destroy,
            width=100
        )
        self.ok_btn.pack(pady=(0, 20))

class AutocompleteEntry(ctk.CTkComboBox):
    """Simple wrapper for ComboBox to act as autocomplete"""
    def __init__(self, master, values: List[str], **kwargs):
        super().__init__(master, values=values, **kwargs)
