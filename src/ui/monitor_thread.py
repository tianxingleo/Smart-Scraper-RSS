import asyncio
import logging
from typing import Optional
from PyQt6.QtCore import QThread, pyqtSignal
from scrapers.bilibili import BilibiliScraper

logger = logging.getLogger(__name__)

class MonitorThread(QThread):
    """监控线程 (纯QThread + asyncio)"""
    
    video_found = pyqtSignal(dict)
    error = pyqtSignal(str)
    
    def __init__(self, scraper: BilibiliScraper, interval: int = 300):
        super().__init__()
        self.scraper = scraper
        self.interval = interval
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._is_running = False

    async def _monitor_task(self):
        """监控任务"""
        try:
            logger.info("监控任务启动，正在初始化浏览器...")
            if not await self.scraper.init_browser(headless=True):
                self.error.emit("浏览器初始化失败，监控任务无法启动")
                return

            while self._is_running:
                try:
                    logger.info("开始新一轮视频抓取...")
                    videos = await self.scraper.get_recommended_videos()
                    
                    if self._is_running:
                        for video in videos:
                            self.video_found.emit(video)
                    
                    logger.info(f"本轮抓取完成，将休眠 {self.interval} 秒")
                    # 使用 asyncio.sleep 实现可中断的等待
                    for _ in range(self.interval):
                        if not self._is_running: break
                        await asyncio.sleep(1)
                        
                except Exception as e:
                    logger.error(f"监控循环出错: {e}")
                    self.error.emit(f"监控循环出错: {e}")
                    if self._is_running:
                        await asyncio.sleep(30)
                    
        except Exception as e:
            logger.error(f"监控任务异常退出: {e}")
            self.error.emit(f"监控任务异常退出: {e}")
        finally:
            logger.info("监控任务即将结束，正在关闭浏览器...")
            await self.scraper.close_browser()
            logger.info("浏览器已关闭，任务彻底结束")

    def run(self):
        """在新线程中设置并运行独立的事件循环"""
        self._is_running = True
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self._monitor_task())
        finally:
            # 确保即使有异常，循环也能被关闭
            if self.loop.is_running():
                self.loop.close()
            self.loop = None
            logger.info("监控线程事件循环已关闭")

    def stop(self):
        """请求停止监控"""
        logger.info("正在请求监控线程停止...")
        self._is_running = False
        # 不再直接与loop交互，让任务自然结束 