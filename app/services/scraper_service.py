import logging
import os
from sqlmodel import Session, select
from app.database import engine
from app.database.models import Source, ScrapedItem
from app.database.crud import update_source_last_scraped
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
        
        # 注意：这里不需要检查 source.url 是否存在于 ScrapedItem
        # 因为 ScrapedItem 存的是具体的帖子/视频 URL，而 source.url 是列表页/主页 URL
        
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
            
            # === 关键修复：入库前检查 item.url 是否已存在 ===
            # 1. 检查无效标题
            if item.title == '无标题':
                logger.warning(f'⚠️ 抓取失败 (无标题), 跳过入库: {item.url}')
                return

            statement = select(ScrapedItem).where(ScrapedItem.url == item.url)
            existing_item = session.exec(statement).first()
            
            if existing_item:
                logger.info(f'⏭️ 内容已存在，跳过入库: {item.title} ({item.url})')
                # 即使跳过入库，也更新一下源的最后抓取时间
                update_source_last_scraped(source_id)
                return

            # AI 分析
            if os.getenv("DEEPSEEK_API_KEY"):
                try:
                    ai = AIProcessor()
                    analysis = ai.analyze(item.content)
                    item.ai_summary = analysis.get('summary', '分析失败')
                    item.sentiment = analysis.get('sentiment', 'Neutral')
                    item.ai_score = analysis.get('score', 0)
                    item.risk_level = analysis.get('risk_level', 'Unknown')
                except Exception as e:
                    logger.error(f'AI 分析异常: {e}')
                    item.ai_summary = 'AI 服务暂时不可用'
                    item.sentiment = 'Neutral'
            else:
                logger.warning(f'⚠️ 未配置 DEEPSEEK_API_KEY，跳过 AI 分析')
                item.ai_summary = '未配置 AI Key'
            
            session.add(item)
            update_source_last_scraped(source_id)
            session.commit()
            
            logger.info(f'✅ 抓取并入库成功: {item.title}')
            
        except Exception as e:
            # 捕获所有异常，防止 crash 导致调度器挂掉
            logger.error(f'❌ 抓取流程异常 [源ID={source_id}]: {str(e)}')

def scrape_source_async(source_id: int):
    """异步抓取源（供调度器调用）"""
    task_queue.add_task(scrape_source, source_id)

def open_login_browser():
    """打开浏览器进行手动登录"""
    from app.scraper.browser import BrowserManager
    try:
        browser = BrowserManager()
        tab = browser.get_new_tab()
        tab.get('https://www.xiaohongshu.com')
        logger.info("Browser opened for login.")
    except Exception as e:
        logger.error(f"Failed to open login browser: {e}")
