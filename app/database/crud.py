"""CRUD operations for database models"""
from typing import List, Optional
from sqlmodel import Session, select
from app.database.models import Source, ScrapedItem
from app.database.engine import engine
from datetime import datetime

# Source CRUD

def create_source(name: str, url: str, platform: str, frequency: int = 60) -> Source:
    """创建新的数据源"""
    with Session(engine) as session:
        source = Source(name=name, url=url, platform=platform, frequency=frequency)
        session.add(source)
        session.commit()
        session.refresh(source)
        return source

def get_sources(active_only: bool = False) -> List[Source]:
    """获取所有数据源"""
    with Session(engine) as session:
        statement = select(Source)
        if active_only:
            statement = statement.where(Source.is_active == True)
        return list(session.exec(statement).all())

def update_source_last_scraped(source_id: int):
    """更新源的最后抓取时间"""
    with Session(engine) as session:
        source = session.get(Source, source_id)
        if source:
            source.last_scraped = datetime.now()
            session.add(source)
            session.commit()

def delete_source(source_id: int):
    """删除数据源"""
    with Session(engine) as session:
        source = session.get(Source, source_id)
        if source:
            session.delete(source)
            session.commit()

# ScrapedItem CRUD

def create_scraped_item(item: ScrapedItem) -> ScrapedItem:
    """创建新的抓取项"""
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

def get_scraped_items(limit: int = 100) -> List[ScrapedItem]:
    """获取抓取项列表"""
    with Session(engine) as session:
        statement = select(ScrapedItem).order_by(ScrapedItem.created_at.desc()).limit(limit)
        return list(session.exec(statement).all())

def get_items_by_source(source_id: int) -> List[ScrapedItem]:
    """获取指定源的所有抓取项"""
    with Session(engine) as session:
        statement = select(ScrapedItem).where(ScrapedItem.source_id == source_id)
        return list(session.exec(statement).all())

def item_exists(url: str) -> bool:
    """检查 URL 是否已存在"""
    with Session(engine) as session:
        statement = select(ScrapedItem).where(ScrapedItem.url == url)
        return session.exec(statement).first() is not None
