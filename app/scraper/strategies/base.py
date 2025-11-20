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
            gap_position = 200  # 默认值
            
            if bg_ele and slider_ele:
                try:
                    # 改进：直接使用 DrissionPage 的截图功能获取 bytes
                    # 这比 requests.get 更安全，因为它使用的是浏览器已经渲染好的画面
                    # 且自动携带了所有 Cookie 和 Session 信息
                    bg_bytes = bg_ele.screenshot_as_bytes()
                    slider_bytes = slider_ele.screenshot_as_bytes()
                    
                    if bg_bytes and slider_bytes:
                         gap_position = captcha_solver.identify_gap(bg_bytes, slider_bytes)
                         print(f"Calculated gap position: {gap_position}")
                except Exception as e:
                    print(f"Failed to calculate gap (using default): {e}")
            
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
