from abc import ABC, abstractmethod
from app.database.models import ScrapedItem
from app.scraper.utils.captcha import captcha_solver
from DrissionPage.items import ChromiumElement
import time
import random


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> ScrapedItem:
        pass

    def handle_captcha(self, page, slider_ele: ChromiumElement, bg_ele: ChromiumElement = None):
        """
        处理滑块验证码
        
        Args:
            page: 页面对象
            slider_ele: 滑块元素
            bg_ele: 背景图片元素 (可选，用于计算缺口位置)
        """
        try:
            # 1. 获取缺口位置
            gap_position = 200 # 默认值
            
            if bg_ele:
                try:
                    # 获取背景图和滑块图的字节流
                    bg_bytes = bg_ele.src() # DrissionPage 可以直接获取资源内容，或者需要用 requests 下载
                    # 注意：如果 src 是 URL，需要下载。如果是 base64，需要解码。
                    # DrissionPage 的 .src() 返回的是 URL。
                    # 我们可以尝试截图或者用 page.download 获取
                    
                    # 简单起见，这里假设我们能通过 screenshot 获取元素图片
                    # 或者直接用 src 下载
                    import requests
                    bg_url = bg_ele.attr('src')
                    slider_url = slider_ele.attr('src')
                    
                    if bg_url and slider_url:
                        bg_resp = requests.get(bg_url)
                        slider_resp = requests.get(slider_url)
                        
                        if bg_resp.status_code == 200 and slider_resp.status_code == 200:
                             gap_position = captcha_solver.identify_gap(bg_resp.content, slider_resp.content)
                             print(f"Calculated gap position: {gap_position}")
                except Exception as e:
                    print(f"Failed to calculate gap: {e}")
            
            # 2. 生成轨迹
            track, delays = captcha_solver.solve(gap_position)
            
            # 3. 执行滑动
            # 按住滑块
            page.actions.hold(slider_ele)
            
            # 按照轨迹移动
            for offset, delay in zip(track, delays):
                page.actions.move(offset, 0, duration=delay)
                # 随机微小停顿
                if random.random() < 0.1:
                    time.sleep(random.uniform(0.01, 0.05))
            
            # 松开
            page.actions.release()
            
            # 等待验证结果
            time.sleep(2)
            
        except Exception as e:
            print(f"Captcha handling failed: {e}")

    def simulate_interaction(self, page):
        """
        模拟人类交互行为 (流量池测试)
        包括：随机滚动、鼠标移动、随机停顿
        """
        try:
            print("Simulating human interaction...")
            # 1. 随机滚动
            # 向下滚动一段距离
            scroll_steps = random.randint(3, 6)
            for _ in range(scroll_steps):
                scroll_amount = random.randint(300, 800)
                page.scroll.down(scroll_amount)
                time.sleep(random.uniform(0.5, 1.5))
            
            # 向上回滚一点 (模拟阅读回看)
            if random.random() < 0.5:
                page.scroll.up(random.randint(200, 500))
                time.sleep(random.uniform(0.5, 1.0))
                
            # 2. 鼠标随机移动
            # 移动到屏幕中心附近
            page.actions.move_to((random.randint(300, 800), random.randint(300, 600)), duration=random.uniform(0.5, 1.0))
            
            # 3. 模拟阅读停顿
            time.sleep(random.uniform(1.0, 3.0))
            
            print("Interaction simulation completed.")
        except Exception as e:
            print(f"Interaction simulation failed: {e}")
