from DrissionPage import ChromiumPage, ChromiumOptions
import os
from app.config import settings

class BrowserManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BrowserManager, cls).__new__(cls)
            cls._instance.page = cls._init_page()
        return cls._instance

    @staticmethod
    def _init_page():
        co = ChromiumOptions()
        # Use absolute path for user data to avoid issues
        user_data_path = os.path.abspath(settings.BROWSER_USER_DATA_PATH)
        co.set_user_data_path(user_data_path)
        co.set_argument('--no-sandbox')
        # Anti-detection
        co.set_argument('--disable-blink-features=AutomationControlled')
        
        # Proxy Configuration
        if settings.PROXY_SERVER:
            co.set_argument(f'--proxy-server={settings.PROXY_SERVER}')
            
        return ChromiumPage(addr_or_opts=co)

    def get_page(self):
        return self.page
