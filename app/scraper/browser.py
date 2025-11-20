from DrissionPage import ChromiumPage, ChromiumOptions
import os
import threading
from app.config import settings

class BrowserManager:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BrowserManager, cls).__new__(cls)
                cls._instance.page = None # 先占位
                cls._instance._init_page()
            return cls._instance

    def _init_page(self):
        """初始化浏览器 (仅执行一次)"""
        if self.page is not None:
            return

        try:
            co = ChromiumOptions()
            # Use absolute path for user data to avoid issues
            user_data_path = os.path.abspath(settings.BROWSER_USER_DATA_PATH)
            co.set_user_data_path(user_data_path)
            co.set_argument('--no-sandbox')
            # Anti-detection
            co.set_argument('--disable-blink-features=AutomationControlled')
            
            # Headless Configuration
            if settings.BROWSER_HEADLESS:
                co.headless(True)
            
            # Proxy Configuration
            if settings.PROXY_SERVER:
                co.set_argument(f'--proxy-server={settings.PROXY_SERVER}')
                
            self.page = ChromiumPage(addr_or_opts=co)
            print("✅ BrowserManager: Browser instance initialized.")
            
        except Exception as e:
            print(f"❌ BrowserManager: Failed to initialize browser: {e}")
            # 如果初始化失败，确保 page 仍然是 None (或者抛出异常)
            self.page = None
            raise e

    def get_new_tab(self):
        """获取一个新的标签页用于抓取任务"""
        if self.page is None:
            # 尝试重新初始化 (自我恢复)
            self._init_page()
            
        if self.page:
            return self.page.new_tab()
        else:
            raise RuntimeError("Browser instance is not available.")
