from app.scraper.strategies.base import BaseScraper
from app.scraper.browser import BrowserManager
from app.database.models import ScrapedItem
import time


class XiaohongshuScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedItem:
        page = BrowserManager().get_page()
        page.get(url)
        time.sleep(2)
        
        title = page.ele('.title').text
        content = page.ele('.desc').text
        
        return ScrapedItem(
            url=url,
            title=title,
            content=content,
            source_id=None
        )
