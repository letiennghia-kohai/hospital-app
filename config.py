"""
Application Configuration
Centralized configuration for the Hospital Management Application
"""
import os
from pathlib import Path

# Base Directory
BASE_DIR = Path(__file__).parent.absolute()

# Database Configuration
DATABASE_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "hospital.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Ensure data directory exists
DATABASE_DIR.mkdir(exist_ok=True)

# UI Configuration
APP_TITLE = "Quản Lý Phòng Khám"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 700

# Theme Configuration
THEME_MODE = "light"  # "light" or "dark"
COLOR_THEME = "blue"  # "blue", "green", "dark-blue"

# Date Format
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"
DB_DATE_FORMAT = "%Y-%m-%d"

# Pagination
ITEMS_PER_PAGE = 50

# Gender Options
GENDER_OPTIONS = ["Nam", "Nữ", "Khác"]

# Appointment Status
APPOINTMENT_STATUS = {
    "PENDING": "Chờ khám",
    "COMPLETED": "Đã khám",
    "OVERDUE": "Quá hẹn",
    "CANCELLED": "Đã hủy"
}

# Medicine Categories
MEDICINE_CATEGORIES = [
    "Kháng sinh",
    "Giảm đau",
    "Hạ sốt",
    "Vitamin & Khoáng chất",
    "Tiêu hóa",
    "Tim mạch",
    "Hô hấp",
    "Da liễu",
    "Khác"
]

# Test Categories
TEST_CATEGORIES = [
    "Huyết học",
    "Sinh hóa",
    "Miễn dịch",
    "Vi sinh",
    "Nước tiểu",
    "Hình ảnh",
    "Khác"
]

# Import/Export Configuration
ALLOWED_IMPORT_EXTENSIONS = [".csv", ".xlsx", ".xls"]
MAX_IMPORT_ROWS = 10000

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "app.log"
