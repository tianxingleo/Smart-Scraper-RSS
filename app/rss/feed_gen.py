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

    def add_items(self, items: List[ScrapedItem], min_score: int = 60, filter_high_risk: bool = True):
        """
        添加抓取的条目到 RSS feed
        
        Args:
            items: 抓取的条目列表
            min_score: 最低 AI 评分要求 (默认 60)
            filter_high_risk: 是否过滤高风险内容 (默认 True)
        """
        # 定义时区 (假设为 UTC+8)
        tz_cn = timezone(timedelta(hours=8))
        
        for item in items:
            # --- 智能过滤逻辑 ---
            # 1. 评分过滤
            if item.ai_score < min_score:
                continue
            
            # 2. 风险过滤
            if filter_high_risk and item.risk_level == "High":
                continue
            
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
                description += f"<h3>🤖 AI 摘要</h3><p>{item.ai_summary}</p>"
            
            # 添加评分和风险展示
            description += f"""
            <div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <p><strong>📊 AI 评分:</strong> {item.ai_score}</p>
                <p><strong>⚠️ 风险等级:</strong> {item.risk_level}</p>
                <p><strong>😊 情感倾向:</strong> {item.sentiment or '未知'}</p>
            </div>
            <hr>
            """
            
            description += f"<h3>原始内容</h3><p>{item.content[:500]}...</p>"
            
            fe.description(description)

    def generate_rss(self) -> str:
        """生成 RSS XML 字符串"""
        return self.fg.rss_str(pretty=True).decode('utf-8')
