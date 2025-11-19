from abc import ABC, abstractmethod
from app.database.models import ScrapedItem


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> ScrapedItem:
        pass
