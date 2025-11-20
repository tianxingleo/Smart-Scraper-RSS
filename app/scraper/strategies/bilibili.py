from app.scraper.strategies.base import BaseScraper
from app.database.models import ScrapedItem
from app.scraper.browser import BrowserManager
import time
from datetime import datetime
from app.scraper.strategies.base import BaseScraper
from app.database.models import ScrapedItem
from app.scraper.browser import BrowserManager
import time
from datetime import datetime
import re

class BilibiliScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedItem:
        """抓取 Bilibili 页面"""
        browser = BrowserManager()
        # 使用新标签页以支持并发
        page = browser.get_new_tab()
        
        try:
            # 开启数据包监听，捕获字幕接口
            # B站字幕接口通常在 player/v2 或类似路径
            page.listen.start('api.bilibili.com/x/player/v2')
            
            page.get(url)
            
            # 1. 检测验证码
            if page.ele('.geetest_window') or page.ele('.bili-mini-mask'):
                print("Detected Bilibili captcha")
                slider = page.ele('.geetest_slider_button')
                if slider:
                    self.handle_captcha(page, slider)
            
            # 2. 模拟人类交互
            self.simulate_interaction(page)

            # 3. 智能等待
            try:
                page.wait.ele_displayed('css:h1.video-title', timeout=10)
            except:
                print("Timeout waiting for video title")
            
            # 提取标题
            title_element = page.ele('css:h1.video-title', timeout=5)
            title = title_element.text if title_element else '无标题'
            
            # 提取内容（简介）
            content_element = page.ele('css:.desc-info', timeout=5)
            content = content_element.text if content_element else '无内容'
            
            # --- 字幕提取逻辑 ---
            subtitle_text = ""
            try:
                # 等待数据包捕获 (最多等待 5 秒)
                res = page.listen.wait(timeout=5)
                if res:
                    json_data = res.response.body
                    # 解析 JSON 寻找 subtitle_url
                    # 结构通常是 data -> subtitle -> subtitles -> [list] -> url
                    if isinstance(json_data, dict) and 'data' in json_data:
                        subtitles = json_data['data'].get('subtitle', {}).get('subtitles', [])
                        if subtitles:
                            # 优先获取中文或第一个字幕
                            sub_url = subtitles[0].get('url')
                            if sub_url:
                                # 补全协议
                                if sub_url.startswith('//'):
                                    sub_url = 'https:' + sub_url
                                
                                print(f"Found subtitle URL: {sub_url}")
                                # 下载字幕
                                import requests
                                sub_resp = requests.get(sub_url)
                                if sub_resp.status_code == 200:
                                    sub_json = sub_resp.json()
                                    # 解析字幕内容
                                    # 格式通常为 body -> [ {from, to, content} ]
                                    body = sub_json.get('body', [])
                                    texts = [item.get('content', '') for item in body]
                                    subtitle_text = "\n".join(texts)
                                    print(f"Extracted {len(texts)} subtitle lines")
            except Exception as e:
                print(f"Subtitle extraction failed: {e}")
            
            # 合并字幕到内容
            if subtitle_text:
                content += f"\n\n=== 视频字幕 ===\n{subtitle_text}"
            
            # 提取图片（封面）
            images = []
            cover_element = page.ele('css:.cover_image', timeout=3)
            if cover_element:
                cover_url = cover_element.attr('src') or ''
                if cover_url:
                    images.append(cover_url)
            
            # 3. 提取发布时间
            publish_date = datetime.now()
            try:
                # B站常见日期选择器
                date_ele = page.ele('css:.pubdate-ip') or page.ele('css:.video-data')
                if date_ele:
                    # 格式通常为 "2023-11-20 12:00:00"
                    date_text = date_ele.text
                    # 提取日期部分
                    match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_text)
                    if match:
                        publish_date = datetime.strptime(match.group(), '%Y-%m-%d %H:%M:%S')
                    else:
                        match_short = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
                        if match_short:
                            publish_date = datetime.strptime(match_short.group(), '%Y-%m-%d')
            except Exception as e:
                print(f"Bilibili date parsing failed: {e}")

            return ScrapedItem(
                url=url,
                title=title,
                content=content,
                images=','.join(images),  # 转换为字符串
                publish_date=publish_date,
                source_id=None
            )
        finally:
            # 停止监听
            page.listen.stop()
            # 务必关闭标签页，防止内存泄漏
            page.close()
