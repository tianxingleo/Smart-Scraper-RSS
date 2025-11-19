import sys
import os
import asyncio
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from utils.database import DatabaseManager
from scrapers.bilibili import BilibiliScraper
from analysis.content_analyzer import ContentAnalyzer
from feed_generation.feed_generator import generate_rss

logging.basicConfig(level=logging.INFO)

def test_database():
    logging.info("Testing DatabaseManager...")
    db = DatabaseManager("test_data/test.db")
    db.clear_all()
    
    video_data = {
        'bvid': 'BV1xx411c7mD',
        'title': 'Test Video',
        'desc': 'Test Description',
        'url': 'http://test.com',
        'subtitle': 'Test Subtitle'
    }
    db.add_video(video_data)
    
    if db.video_exists('BV1xx411c7mD'):
        logging.info("Database: Video added successfully.")
    else:
        logging.error("Database: Video not found.")

async def test_scraper():
    logging.info("Testing BilibiliScraper...")
    scraper = BilibiliScraper()
    
    # Test get_popular_videos (async)
    logging.info("Fetching popular videos...")
    videos = await scraper.get_popular_videos()
    if videos:
        logging.info(f"Scraper: Fetched {len(videos)} popular videos.")
        first_video = videos[0]
        logging.info(f"First video: {first_video.get('title')}")
        
        # Test get_video_subtitle (async)
        bvid = first_video.get('bvid')
        if bvid:
            logging.info(f"Fetching subtitle for {bvid}...")
            subtitle = await scraper.get_video_subtitle(bvid)
            logging.info(f"Subtitle length: {len(subtitle)}")
    else:
        logging.error("Scraper: Failed to fetch popular videos.")

def test_analyzer():
    logging.info("Testing ContentAnalyzer...")
    # Mock API key for initialization if not in env
    api_key = os.getenv("DEEPSEEK_API_KEY") or "test_key"
    analyzer = ContentAnalyzer(api_key=api_key)
    if hasattr(analyzer, 'analyze_content'):
        logging.info("Analyzer: Class and method found.")
    else:
        logging.error("Analyzer: Missing method.")

def test_rss():
    logging.info("Testing RSS Generation...")
    items = [{
        'bvid': 'BV1xx411c7mD',
        'title': 'Test Video',
        'url': 'http://test.com',
        'score': 8,
        'tags': ['test'],
        'analysis': 'Good',
        'desc': 'Desc',
        'pubdate': 1678886400
    }]
    try:
        generate_rss(items, "test_output.xml")
        if os.path.exists("test_output.xml"):
            logging.info("RSS: File generated successfully.")
            os.remove("test_output.xml")
        else:
            logging.error("RSS: File not generated.")
    except Exception as e:
        logging.error(f"RSS: Generation failed: {e}")

async def main():
    test_database()
    await test_scraper()
    test_analyzer()
    test_rss()
    logging.info("Verification complete.")

if __name__ == "__main__":
    asyncio.run(main())
