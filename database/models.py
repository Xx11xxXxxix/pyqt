import sqlite3
import datetime

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mobile VARCHAR(11) UNIQUE NOT NULL,
    netease_id VARCHAR(50),
    login_counts INTEGER DEFAULT 0,
    last_login_time DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    cookies text
)
"""

CREATE_API_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS api_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    api_name VARCHAR(100) NOT NULL,
    request_params TEXT NOT NULL,
    response_data TEXT NOT NULL,
    status_code INTEGER NOT NULL,
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
"""