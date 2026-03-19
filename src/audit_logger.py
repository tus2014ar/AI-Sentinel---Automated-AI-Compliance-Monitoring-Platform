import sqlite3
import os
import hashlib
from datetime import datetime
import pandas as pd

class AuditLogger:
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, 'data', 'audit_log.db')
        else:
            self.db_path = db_path
            
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_runs (
                run_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                dataset_filename TEXT NOT NULL,
                resident_count INTEGER NOT NULL,
                review_recommended_count INTEGER NOT NULL,
                monitor_count INTEGER NOT NULL,
                no_issue_count INTEGER NOT NULL,
                sha256_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def log_run(self, dataset_filename: str, resident_count: int, 
                review_recommended_count: int, monitor_count: int, 
                no_issue_count: int) -> int:
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Calculate SHA256 of the record content to ensure immutability/tamper-evidence
        record_str = f"{timestamp}|{dataset_filename}|{resident_count}|{review_recommended_count}|{monitor_count}|{no_issue_count}"
        sha256_hash = hashlib.sha256(record_str.encode('utf-8')).hexdigest()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_runs (
                timestamp, dataset_filename, resident_count, 
                review_recommended_count, monitor_count, no_issue_count, sha256_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, dataset_filename, resident_count, review_recommended_count, monitor_count, no_issue_count, sha256_hash))
        run_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return run_id

    def get_all_runs(self) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM audit_runs ORDER BY timestamp DESC", conn)
        conn.close()
        return df
