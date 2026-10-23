"""
Configuration settings for Diabetes Risk Classification System.
Reads configuration from environment variables with local development fallbacks.
"""

import os

class Config:
    # Secret key for Flask session security
    SECRET_KEY = os.environ.get("SECRET_KEY", "diarisk-classification-mca-secret-key-2026")

    # MySQL Database Connection Parameters
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "Vishu8580")
    MYSQL_DB = os.environ.get("MYSQL_DB", "diabetes_db")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))

    # Application settings
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
