from app.scraper.strategies.base import BaseScraper
from app.database.models import ScrapedItem
from app.scraper.browser import BrowserManager
from datetime import datetime
import re

class XiaoheiheScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedItem:
        """抓取小黑盒文章"""
        browser = BrowserManager()
        page = browser.get_new_tab()
        
        try:
            page.get(url)
            
            # 模拟阅读
            self.simulate_interaction(page)
            
            # 等待标题加载
            try:
                page.wait.ele_displayed('css:h1.title', timeout=10)
            except:
                print("Timeout waiting for Xiaoheihe title")

            # 提取标题
            title_ele = page.ele('css:h1.title')
            title = title_ele.text if title_ele else '无标题'
            
            # 提取正文
            # 小黑盒文章内容通常在 .article-content 或类似容器中
            content_ele = page.ele('css:.article-content') or page.ele('css:#article_content')
            content = content_ele.text if content_ele else '无内容'
            
            # 提取图片
            images = []
            img_eles = page.eles('css:.article-content img')
            for img in img_eles[:3]:  # 取前3张
                src = img.attr('data-original') or img.attr('src')
                if src:
                    images.append(src)
            
            # 提取发布时间
            publish_date = datetime.now()
            try:
                # 尝试寻找时间元素
                time_ele = page.ele('css:.time') or page.ele('css:.article-time')
                if time_ele:
                    # 格式处理需根据实际页面调整，这里做通用尝试
                    date_text = time_ele.text
                    # 简单匹配 YYYY-MM-DD
                    match = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
                    if match:
                        publish_date = datetime.strptime(match.group(), '%Y-%m-%d')
            except Exception as e:
                print(f"Xiaoheihe date parsing failed: {e}")

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
