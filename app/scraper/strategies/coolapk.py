from app.scraper.strategies.base import BaseScraper
from app.database.models import ScrapedItem
from app.scraper.browser import BrowserManager
from datetime import datetime
import re

class CoolAPKScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedItem:
        """抓取酷安动态/文章"""
        browser = BrowserManager()
        page = browser.get_new_tab()
        
        try:
            page.get(url)
            
            # 模拟阅读
            self.simulate_interaction(page)
            
            # 酷安网页版结构较为动态，需针对性等待
            try:
                # 尝试等待动态内容加载
                page.wait.ele_displayed('css:.feed-article-title', timeout=10)
            except:
                pass

            # 提取标题 (如果是文章) 或 摘要 (如果是动态)
            title_ele = page.ele('css:.feed-article-title')
            if title_ele:
                title = title_ele.text
            else:
                # 动态没有标题，截取内容前20字
                content_preview = page.ele('css:.feed-article-message')
                title = content_preview.text[:20] + '...' if content_preview else '酷安动态'
            
            # 提取内容
            content_ele = page.ele('css:.feed-article-message') or page.ele('css:.feed-article-content')
            content = content_ele.text if content_ele else '无内容'
            
            # 提取图片
            images = []
            img_eles = page.eles('css:.feed-article-image img')
            for img in img_eles[:3]:
                src = img.attr('src')
                if src:
                    images.append(src)
            
            # 提取发布时间
            publish_date = datetime.now()
            try:
                # 酷安时间通常是 "1小时前" 这种相对时间，或者具体日期
                # 这里简化处理，如果找不到绝对时间，就用当前时间
                # 实际生产中需要解析相对时间
                pass 
            except Exception as e:
                print(f"CoolAPK date parsing failed: {e}")

            return ScrapedItem(
                url=url,
                title=title,
                content=content,
                images=','.join(images),
                publish_date=publish_date,
                source_id=None
            )
            
        finally:
            page.close()
