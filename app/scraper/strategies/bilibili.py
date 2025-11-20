from app.scraper.strategies.base import BaseScraper
from app.database.models import ScrapedItem
from app.scraper.browser import BrowserManager
import time
from datetime import datetime
import re

class BilibiliScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedItem:
        """抓取 Bilibili 页面 (支持视频详情页和列表页自动跳转)"""
        browser = BrowserManager()
        page = browser.get_new_tab()
        
        try:
            # 开启数据包监听 (为了获取字幕)
            page.listen.start('api.bilibili.com/x/player/v2')
            
            print(f"Navigating to: {url}")
            page.get(url)
            
            # === 新增：列表页自动跳转逻辑 ===
            # 如果是热门、排行榜、频道页，通常包含视频卡片
            # 尝试寻找常见的视频列表容器
            video_card = page.ele('.video-card') or \
                         page.ele('.bili-video-card') or \
                         page.ele('.rank-item') or \
                         page.ele('.small-item')
                         
            # 如果找到了视频卡片，且当前页面没有视频标题（说明不是详情页）
            if video_card and not page.ele('h1.video-title'):
                print("检测到列表页，尝试获取第一个视频...")
                # 获取视频链接
                # 通常链接在卡片本身或其内部的 a 标签
                video_link = video_card.ele('tag:a').link
                if not video_link:
                    video_link = video_card.link
                
                if video_link:
                    # 必须是视频链接 (av/BV)
                    if 'video/BV' in video_link or 'video/av' in video_link:
                        print(f"Redirecting to video: {video_link}")
                        # 跳转到具体视频页，覆盖之前的 URL 变量以便入库时使用具体的视频 URL
                        url = video_link 
                        page.get(url)
                        time.sleep(2) # 等待跳转加载
            # ================================

            # 1. 检测验证码
            if page.ele('.geetest_window') or page.ele('.bili-mini-mask'):
                print("Detected Bilibili captcha")
                slider = page.ele('.geetest_slider_button')
                if slider:
                    self.handle_captcha(page, slider)
            
            # 2. 模拟人类交互
            self.simulate_interaction(page)

            # 3. 智能等待标题
            try:
                page.wait.ele_displayed('css:h1.video-title', timeout=8)
            except:
                pass # 超时继续尝试提取
            
            # 提取标题
            title_element = page.ele('css:h1.video-title')
            title = title_element.text if title_element else '无标题'
            
            # 提取内容（简介）
            content_element = page.ele('css:.desc-info') or page.ele('css:#v_desc')
            content = content_element.text if content_element else ''
            
            # --- 字幕提取逻辑 (保持不变) ---
            subtitle_text = ""
            try:
                res = page.listen.wait(timeout=3)
                if res:
                    json_data = res.response.body
                    if isinstance(json_data, dict) and 'data' in json_data:
                        subtitles = json_data['data'].get('subtitle', {}).get('subtitles', [])
                        if subtitles:
                            sub_url = subtitles[0].get('url')
                            if sub_url:
                                if sub_url.startswith('//'): sub_url = 'https:' + sub_url
                                import requests
                                sub_resp = requests.get(sub_url)
                                if sub_resp.status_code == 200:
                                    body = sub_resp.json().get('body', [])
                                    subtitle_text = "\n".join([i.get('content', '') for i in body])
            except Exception as e:
                print(f"Subtitle extraction warning: {e}")
            
            if subtitle_text:
                content += f"\n\n=== 视频字幕 ===\n{subtitle_text}"
            
            # 提取封面
            images = []
            # B站封面通常在 meta 标签或 window.__INITIAL_STATE__ 中，这里尝试简单的 DOM 获取
            # 很多时候封面是背景图，较难获取，这里尝试获取 og:image
            try:
                meta_img = page.ele('xpath://meta[@property="og:image"]')
                if meta_img:
                    images.append(meta_img.attr('content'))
            except:
                pass
            
            # 提取时间
            publish_date = datetime.now()
            try:
                date_ele = page.ele('css:.pubdate-ip') or page.ele('css:.video-data')
                if date_ele:
                    date_text = date_ele.text
                    match = re.search(r'\d{4}-\d{2}-\d{2}', date_text)
                    if match:
                        publish_date = datetime.strptime(match.group(), '%Y-%m-%d')
            except:
                pass

            return ScrapedItem(
                url=url, # 这里返回的是最终跳转后的视频 URL，而不是列表 URL
                title=title,
                content=content,
                images=','.join(images),
                publish_date=publish_date,
                source_id=None
            )
        finally:
            page.listen.stop()
            page.close()
