import logging
from .database import DatabaseManager

# Global database instance
db = DatabaseManager()

def load_processed_bvids() -> set:
    """Loads the set of processed bvid's from the database."""
    return db.get_processed_bvids()

def add_processed_bvid(video_data):
    """
    Appends a new processed video to the database.
    Args:
        video_data (dict or str): Video data dictionary or bvid string.
                                  If string, only bvid is stored.
    """
    if isinstance(video_data, str):
        video_data = {'bvid': video_data}
    
    db.add_video(video_data)

def add_analysis_result(analysis_data):
    """Saves analysis result to the database."""
    db.add_analysis(analysis_data)

def clear_processed_bvids():
    """Deletes all records from the database."""
    db.clear_all()
    logging.info("已清空数据库记录。")