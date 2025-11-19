import sqlite3
import os
import logging
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/smart_scraper.db"):
        self.db_path = db_path
        self._ensure_data_dir()
        self._init_db()

    def _ensure_data_dir(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create videos table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS videos (
                        bvid TEXT PRIMARY KEY,
                        title TEXT,
                        desc TEXT,
                        url TEXT,
                        subtitle TEXT,
                        fetch_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Create analysis_results table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS analysis_results (
                        bvid TEXT PRIMARY KEY,
                        score INTEGER,
                        tags TEXT,
                        analysis TEXT,
                        is_negative BOOLEAN,
                        analysis_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (bvid) REFERENCES videos (bvid)
                    )
                ''')
                
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")

    def add_video(self, video_data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO videos (bvid, title, desc, url, subtitle)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    video_data.get('bvid'),
                    video_data.get('title'),
                    video_data.get('desc'),
                    video_data.get('url'),
                    video_data.get('subtitle')
                ))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding video: {e}")

    def add_analysis(self, analysis_data):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO analysis_results (bvid, score, tags, analysis, is_negative)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    analysis_data.get('bvid'),
                    analysis_data.get('score'),
                    str(analysis_data.get('tags')), # Store list as string
                    analysis_data.get('analysis'),
                    analysis_data.get('is_negative')
                ))
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error adding analysis: {e}")

    def video_exists(self, bvid):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT 1 FROM videos WHERE bvid = ?', (bvid,))
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logging.error(f"Error checking video existence: {e}")
            return False

    def get_processed_bvids(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT bvid FROM videos')
                return {row[0] for row in cursor.fetchall()}
        except sqlite3.Error as e:
            logging.error(f"Error getting processed bvids: {e}")
            return set()

    def clear_all(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM analysis_results')
                cursor.execute('DELETE FROM videos')
                conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error clearing database: {e}")
