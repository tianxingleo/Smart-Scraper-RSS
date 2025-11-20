from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Source(SQLModel, table=True):
    """数据源模型 - 存储爬虫任务配置"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str  # 源的友好名称
    url: str
    platform: str  # 'bilibili' or 'xiaohongshu'
    frequency: int = 60  # 抓取频率(分钟)
    is_active: bool = True  # 是否启用
    last_scraped: Optional[datetime] = None  # 最后抓取时间
    
    # 关系
    items: List["ScrapedItem"] = Relationship(back_populates="source")

class ScrapedItem(SQLModel, table=True):
    """抓取内容模型 - 存储爬取结果"""
    id: Optional[int] = Field(default=None, primary_key=True)
    source_id: int = Field(foreign_key="source.id")
    title: str
    url: str = Field(unique=True)
    content: str
    images: str = ""  # JSON string: 图片 URL 列表
    publish_date: datetime = Field(default_factory=datetime.now)  # 发布时间 (RSS 必需)
    created_at: datetime = Field(default_factory=datetime.now)  # 创建时间
    
    # AI 增强字段
    ai_summary: Optional[str] = None
    sentiment: Optional[str] = None
    ai_score: int = Field(default=0)  # 内容评分 (0-100)
    risk_level: str = Field(default="Unknown")  # 风险等级 (High/Medium/Low)
    
    # 关系
    source: Source = Relationship(back_populates="items")
