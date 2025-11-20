import logging
from sqlmodel import Session
from app.database import engine
from app.database.models import Source
from app.database.crud import update_source_last_scraped, item_exists
from app.scraper.strategies import BilibiliScraper, XiaohongshuScraper
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
        scraper = BilibiliScraper() if source.platform == 'bilibili' else XiaohongshuScraper()
        
        try:
            item = scraper.scrape(source.url)
            item.source_id = source_id
            
            # AI 分析
            try:
                ai = AIProcessor()
                analysis = ai.analyze(item.content)
                item.ai_summary = analysis.get('summary', '分析失败')
                item.sentiment = analysis.get('sentiment', 'Neutral')
            except Exception as e:
                logger.error(f'AI 分析失败: {e}')
                item.ai_summary = '分析失败'
                item.sentiment = 'Neutral'
            
            session.add(item)
            update_source_last_scraped(source_id)
            session.commit()
            
            logger.info(f'✅ 抓取成功: {item.title}')
        except Exception as e:
            logger.error(f'❌ 抓取失败 [源ID={source_id}]: {str(e)}')

def scrape_source_async(source_id: int):
    """异步抓取源（供调度器调用）"""
    task_queue.add_task(scrape_source, source_id)
