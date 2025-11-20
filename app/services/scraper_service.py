import logging
from sqlmodel import Session
from app.database import engine
from app.database.models import Source
from app.database.crud import update_source_last_scraped, item_exists
from app.scraper.strategies import BilibiliScraper, XiaohongshuScraper, XiaoheiheScraper, CoolAPKScraper
from app.ai.client import AIProcessor
from app.core import task_queue

# 配置日志
logger = logging.getLogger(__name__)

def scrape_source(source_id: int):
    """抓取指定源（同步）"""
    with Session(engine) as session:
        source = session.get(Source, source_id)
        if not source:
            logger.error(f'源不存在: {source_id}')
            return
        
        # 去重检查
        if item_exists(source.url):
            logger.info(f'URL已存在，跳过: {source.url}')
            return
        
        # 选择爬虫
        if source.platform == 'bilibili':
            scraper = BilibiliScraper()
        elif source.platform == 'xiaohongshu':
            scraper = XiaohongshuScraper()
        elif source.platform == 'xiaoheihe':
            scraper = XiaoheiheScraper()
        elif source.platform == 'coolapk':
            scraper = CoolAPKScraper()
        else:
            logger.error(f'未知的平台类型: {source.platform}')
            return
        
        try:
            item = scraper.scrape(source.url)
            item.source_id = source_id
            
            # AI 分析
            try:
                ai = AIProcessor()
                analysis = ai.analyze(item.content)
                item.ai_summary = analysis.get('summary', '分析失败')
                item.sentiment = analysis.get('sentiment', 'Neutral')
                item.ai_score = analysis.get('score', 0)
                item.risk_level = analysis.get('risk_level', 'Unknown')
            except Exception as e:
                logger.error(f'AI 分析失败: {e}')
                item.ai_summary = '分析失败'
                item.sentiment = 'Neutral'
                item.ai_score = 0
                item.risk_level = 'Unknown'
            
            session.add(item)
            update_source_last_scraped(source_id)
            session.commit()
            
            logger.info(f'✅ 抓取成功: {item.title}')
        except Exception as e:
            logger.error(f'❌ 抓取失败 [源ID={source_id}]: {str(e)}')

def scrape_source_async(source_id: int):
    """异步抓取源（供调度器调用）"""
    task_queue.add_task(scrape_source, source_id)

def open_login_browser():
    """打开浏览器进行手动登录"""
    from app.scraper.browser import BrowserManager
    import time
    
    try:
        browser = BrowserManager()
        # 获取一个新标签页
        tab = browser.get_new_tab()
        
        # 导航到一个导航页或直接打开小红书/B站
        tab.get('https://www.xiaohongshu.com')
        
        # 提示用户
        logger.info("Browser opened for login. Please login manually.")
        
        # 注意：如果浏览器是 headless 模式，用户将看不到窗口。
        # 实际生产中可能需要检测并提示用户关闭 headless 模式，或者重启浏览器实例。
        
    except Exception as e:
        logger.error(f"Failed to open login browser: {e}")
