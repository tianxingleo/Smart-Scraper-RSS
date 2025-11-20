from feedgen.feed import FeedGenerator
from app.database.models import ScrapedItem
from typing import List
from datetime import timezone, timedelta

class RSSGenerator:
    def __init__(self, title: str = "Smart Scraper RSS", link: str = "http://localhost:8080", description: str = "智能内容聚合 RSS"):
        self.fg = FeedGenerator()
        self.fg.title(title)
        self.fg.link(href=link, rel='alternate')
        self.fg.description(description)
        self.fg.language('zh-CN')

    def add_items(self, items: List[ScrapedItem]):
        """添加抓取的条目到 RSS feed"""
        # 定义时区 (假设为 UTC+8)
        tz_cn = timezone(timedelta(hours=8))
        
        for item in items:
            fe = self.fg.add_entry()
            fe.title(item.title)
            fe.link(href=item.url)
            
            # 处理发布时间，确保带有时区
            pub_date = item.publish_date
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=tz_cn)
            fe.pubDate(pub_date)
            fe.guid(item.url, permalink=True)
            
            # 构建描述，包含 AI 摘要和原始内容
            description = ""
            if item.ai_summary:
                description += f"<h3>🤖 AI 摘要</h3><p>{item.ai_summary}</p><hr>"
            
            description += f"<h3>情感</h3><p>{item.sentiment or '未知'}</p>"
            description += f"<h3>原始内容</h3><p>{item.content[:200]}...</p>"
            
            fe.description(description)

    def generate_rss(self) -> str:
        """生成 RSS XML 字符串"""
        return self.fg.rss_str(pretty=True).decode('utf-8')
