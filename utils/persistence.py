import os
import logging

DATA_DIR = "data"
PROCESSED_VIDEOS_FILE = os.path.join(DATA_DIR, "processed_bvids.txt")

def _ensure_data_dir_exists():
    """Ensures the data directory exists."""
    if not os.path.exists(DATA_DIR):
        try:
            os.makedirs(DATA_DIR)
            logging.info(f"已创建数据目录: {DATA_DIR}")
        except OSError as e:
            logging.error(f"无法创建数据目录 {DATA_DIR}: {e}")

def load_processed_bvids() -> set:
    """Loads the set of processed bvid's from the local file."""
    _ensure_data_dir_exists()
    if not os.path.exists(PROCESSED_VIDEOS_FILE):
        return set()
    try:
        with open(PROCESSED_VIDEOS_FILE, 'r', encoding='utf-8') as f:
            # Read lines, strip whitespace, and filter out empty lines
            bvids = {line.strip() for line in f if line.strip()}
            logging.info(f"成功从 {PROCESSED_VIDEOS_FILE} 加载 {len(bvids)} 个已处理的bvid。")
            return bvids
    except IOError as e:
        logging.error(f"无法读取已处理视频文件 {PROCESSED_VIDEOS_FILE}: {e}")
        return set()

def add_processed_bvid(bvid: str):
    """Appends a new processed bvid to the local file."""
    _ensure_data_dir_exists()
    try:
        with open(PROCESSED_VIDEOS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{bvid}\n")
    except IOError as e:
        logging.error(f"无法写入已处理视频文件 {PROCESSED_VIDEOS_FILE}: {e}")

def clear_processed_bvids():
    """Deletes the local file of processed bvid's."""
    if os.path.exists(PROCESSED_VIDEOS_FILE):
        try:
            os.remove(PROCESSED_VIDEOS_FILE)
            logging.info(f"成功删除已处理视频记录文件: {PROCESSED_VIDEOS_FILE}")
            return True
        except OSError as e:
            logging.error(f"删除已处理视频记录文件失败: {e}")
            return False
    else:
        logging.info("已处理视频记录文件不存在，无需删除。")
        return True 