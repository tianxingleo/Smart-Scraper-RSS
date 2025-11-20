from nicegui import ui, app
from dotenv import load_dotenv
import os
import logging

# ===== 1. 首先加载 .env 文件 =====
load_dotenv()  # 确保所有环境变量被正确加载

from app.database import create_db_and_tables
from app.core import scheduler_manager, task_queue
from app.config import settings
from app.database.crud import get_sources
from app.services.scraper_service import scrape_source_async

# 配置日志格式
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# 初始化数据库
create_db_and_tables()

def init_app():
    """应用启动时的初始化逻辑"""
    # 1. 启动任务队列
    if not task_queue.running:
        task_queue.start(num_workers=2)
    
    # 2. 初始化调度器
    # 先清除所有现有任务，防止热重载导致的重复
    existing_jobs = scheduler_manager.get_jobs()
    if not existing_jobs:
        sources = get_sources(active_only=True)
        count = 0
        for source in sources:
            job_id = f"scrape_source_{source.id}"
            # 检查是否已存在，避免重复添加
            if not scheduler_manager.scheduler.get_job(job_id):
                scheduler_manager.add_job(
                    job_id=job_id,
                    func=scrape_source_async,
                    minutes=source.frequency,
                    source_id=source.id
                )
                count += 1
        logger.info(f"🚀 系统启动完成，已加载 {count} 个定时抓取任务")

# 使用 NiceGUI 的生命周期钩子
app.on_startup(init_app)

# 导入页面（会注册路由）
from app.ui.pages import dashboard, sources, settings_page

@ui.page('/')
def index():
    """首页 - 重定向到 dashboard"""
    ui.navigate.to('/dashboard')

# RSS Feed 端点
@ui.page('/feed.xml')
def feed():
    """RSS feed 端点"""
    from app.database.crud import get_scraped_items
    from app.rss.feed_gen import RSSGenerator
    
    items = get_scraped_items(limit=settings.RSS_MAX_ITEMS)
    
    rss = RSSGenerator(
        title=settings.RSS_FEED_TITLE,
        link=settings.RSS_FEED_LINK,
        description=settings.RSS_FEED_DESCRIPTION
    )
    rss.add_items(items)
    
    return rss.generate_rss(), {'Content-Type': 'application/rss+xml; charset=utf-8'}

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        port=settings.UI_PORT,
        title=settings.APP_NAME,
        reload=False, # 生产环境建议关闭 reload
        show=True,
        favicon='🚀'
    )
