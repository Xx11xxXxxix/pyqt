import json
# database/db_manager.py
import sqlite3
from datetime import datetime
from pathlib import Path

from database.models import CREATE_USERS_TABLE, CREATE_API_LOG_TABLE


class DatabaseManager:
    def __init__(self, db_file="pyqt.db"):
        db_path = Path("database") / db_file
        db_path.parent.mkdir(exist_ok=True)
        self.db_file = str(db_path)
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_file)

    def init_database(self):
        with self.get_connection() as conn:
            conn.execute(CREATE_API_LOG_TABLE)
            conn.execute(CREATE_USERS_TABLE)
            conn.commit()

    def add_or_update_user(self, mobile,netease_id=0):
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
                user = cursor.fetchone()
                print(user)

                if user:
                    user_id=user[0]
                    cursor.execute("""
                        UPDATE users 
                        SET login_counts = login_counts + 1,
                            last_login_time = ?,
                            netease_id = COALESCE(?, netease_id)
                        WHERE mobile = ?
                    """, (datetime.now(), netease_id, mobile))
                    conn.commit()
                    return user_id
                else:
                    cursor.execute("""
                        INSERT INTO users (mobile, netease_id, login_counts, last_login_time)
                        VALUES (?, ?, 1, ?)
                    """, (mobile, netease_id, datetime.now()))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            print(f"add_or_update_user: {e}")
            return None

    def update_user_cookies(self, user_id, cookies):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET cookies = ? 
                WHERE id = ?
            """, (cookies, user_id))
            conn.commit()

    def get_user_cookies(self, user_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT cookies FROM users WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None

    def get_user_by_mobile(self, mobile):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE mobile = ?", (mobile,))
            return cursor.fetchone()

    def get_all_users(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users ORDER BY last_login_time DESC")
            return cursor.fetchall()

    def delete_user(self, mobile):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE mobile = ?", (mobile,))
            conn.commit()
            return cursor.rowcount

    def log_api_call(self, user_id, api_name, request_params, response_data, status_code, error_message=None):
        # 记录
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_logs (user_id, api_name, request_params, response_data, status_code, error_message)
                VALUES (?, ?, ?, ?, ?, ?)  
            """, (
                user_id,
                api_name,
                json.dumps(request_params),
                json.dumps(response_data),
                status_code,
                error_message
            ))
            conn.commit()
            return cursor.lastrowid

    def update_netease_user(self, profile, music_u):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            current_time = datetime.now()

            cursor.execute("""
                INSERT OR REPLACE INTO netease_users (
                    user_id, nickname, music_u, avatar_url, vip_type,
                    last_login_time, last_login_ip, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.get('userId'),
                profile.get('nickname'),
                music_u,
                profile.get('avatarUrl'),
                profile.get('vipType'),
                profile.get('lastLoginTime'),
                profile.get('lastLoginIP'),
                current_time
            ))
            conn.commit()
            return cursor.lastrowid
