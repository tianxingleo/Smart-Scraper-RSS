"""小红书爬虫策略"""
from app.scraper.strategies.base import BaseScraper
from app.database.models import ScrapedItem
from app.scraper.browser import BrowserManager
import time
from datetime import datetime
import re

class XiaohongshuScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedItem:
        """抓取小红书页面"""
        browser = BrowserManager()
        # 使用新标签页以支持并发
        page = browser.get_new_tab()
        
        try:
            page.get(url)
            
            # 1. 检测并处理验证码
            # 假设验证码容器类名为 .validate-main (需根据实际情况调整)
            if page.ele('.validate-main'):
                print("Detected captcha, attempting to solve...")
                slider = page.ele('.drag-button') # 假设滑块类名
                bg = page.ele('.validate-bg')     # 假设背景类名
                if slider:
                    self.handle_captcha(page, slider, bg)
            
            # 2. 模拟人类交互 (流量池测试)
            self.simulate_interaction(page)

            # 3. 智能等待内容加载
            # 替换硬编码 sleep
            try:
                page.wait.ele_displayed('css:.title', timeout=10)
            except:
                print("Timeout waiting for content")
            
            # 提取标题
            title_element = page.ele('css:.title', timeout=5)
            title = title_element.text if title_element else '无标题'
            
            # 提取内容
            content_element = page.ele('css:.content', timeout=5)
            content = content_element.text if content_element else '无内容'
            
            # 提取图片
            images = []
            img_elements = page.eles('css:.note-image img', timeout=3)
            for img in img_elements[:5]:  # 最多5张图片
                img_url = img.attr('src') or ''
                if img_url:
                    images.append(img_url)
            
            # 3. 提取发布时间
            publish_date = datetime.now()
            try:
                # 尝试多种常见的日期选择器
                date_ele = page.ele('css:.date') or page.ele('css:.publish-date') or page.ele('css:.bottom-container .time')
                if date_ele:
                    date_text = date_ele.text.replace('发布于', '').strip()
                    # 尝试解析日期格式，如 "2023-11-20" 或 "11-20"
                    if re.match(r'\d{4}-\d{2}-\d{2}', date_text):
                        publish_date = datetime.strptime(date_text, '%Y-%m-%d')
                    elif re.match(r'\d{2}-\d{2}', date_text):
                        # 补全年份
                        current_year = datetime.now().year
                        publish_date = datetime.strptime(f"{current_year}-{date_text}", '%Y-%m-%d')
            except Exception as e:
                print(f"Date parsing failed: {e}")

            return ScrapedItem(
                url=url,
                title=title,
                content=content,
                images=','.join(images),  # 转换为字符串
                publish_date=publish_date,
                source_id=None
            )
        finally:
            # 务必关闭标签页，防止内存泄漏
            page.close()
