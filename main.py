"""
Main Application Entry Point
"""
import customtkinter as ctk
from database.db_manager import initialize_database
from ui.main_window import MainWindow
import config


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(f"{config.APP_TITLE} v{config.APP_VERSION}")
        self.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.minsize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
        
        # Set icon (optional)
        # self.iconbitmap("assets/icon.ico")
        
        # Initialize database
        print("Initializing database...")
        initialize_database()
        
        # Theme settings
        ctk.set_appearance_mode(config.THEME_MODE)
        ctk.set_default_color_theme(config.COLOR_THEME)
        
        # Main Window Component
        self.main_window = MainWindow(self)
        self.main_window.pack(fill="both", expand=True)

    def run(self):
        """Run the application"""
        self.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
