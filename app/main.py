from nicegui import ui
from app.database import create_db_and_tables
from app.core import scheduler_manager, task_queue
from app.config import settings
from app.database.crud import get_sources
from app.services.scraper_service import scrape_source_async
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 初始化数据库
create_db_and_tables()

# 启动任务队列
task_queue.start(num_workers=2)

def init_scheduler():
    """初始化调度器 - 为所有活跃源添加定时任务"""
    sources = get_sources(active_only=True)
    for source in sources:
        job_id = f"scrape_source_{source.id}"
        scheduler_manager.add_job(
            job_id=job_id,
            func=scrape_source_async,
            minutes=source.frequency,
            source_id=source.id
        )
    logging.info(f"调度器初始化完成，已添加 {len(sources)} 个定时任务")

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
    # 初始化调度器
    init_scheduler()
    
    ui.run(
        port=settings.UI_PORT,
        title=settings.APP_NAME,
        reload=False,
        show=True  # 自动打开浏览器
    )
