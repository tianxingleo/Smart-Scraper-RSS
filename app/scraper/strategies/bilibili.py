from app.scraper.strategies.base import BaseScraper
from app.scraper.browser import BrowserManager
from app.database.models import ScrapedItem
import time
import time

class BilibiliScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedItem:
        page = BrowserManager().get_page()
        page.get(url)
        time.sleep(2)  # Wait for load
        
        title = page.ele('tag:h1').text
        # This is a simplified selector, might need adjustment
        content = page.ele('#v_desc').text 
        
        return ScrapedItem(
            url=url,
            title=title,
            content=content,
            source_id=None # To be filled by caller
        )
