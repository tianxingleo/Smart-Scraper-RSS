from feedgen.feed import FeedGenerator
from app.database.models import ScrapedItem
from typing import List


class RSSGenerator:
    def __init__(self, title: str = "Smart Scraper RSS", link: str = "http://localhost:8080", description: str = "智能内容聚合 RSS"):
        self.fg = FeedGenerator()
        self.fg.title(title)
        self.fg.link(href=link, rel='alternate')
        self.fg.description(description)
        self.fg.language('zh-CN')

    def add_items(self, items: List[ScrapedItem]):
        """添加抓取的条目到 RSS feed"""
        for item in items:
            fe = self.fg.add_entry()
            fe.title(item.title)
            fe.link(href=item.url)
            
            # 构建描述，包含 AI 摘要和原始内容
            description = f"<h3>AI 摘要</h3><p>{item.ai_summary or '暂无摘要'}</p>"
            description += f"<h3>情感</h3><p>{item.sentiment or '未知'}</p>"
            description += f"<h3>原始内容</h3><p>{item.content[:200]}...</p>"
            
            fe.description(description)
            fe.pubDate(item.created_at)
            fe.guid(item.url, permalink=True)

    def generate_rss(self) -> str:
        """生成 RSS XML 字符串"""
        return self.fg.rss_str(pretty=True).decode('utf-8')
