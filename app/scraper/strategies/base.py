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
            # 注意：这里简化处理，如果没有背景图或无法计算，假设一个随机位置或需要额外逻辑
            # 实际项目中需要下载图片并使用 OpenCV 计算 gap_position
            # 这里为了演示，假设我们能获取到 gap (或者通过 js 获取)
            
            # 模拟：如果无法计算，尝试简单的拖拽或者直接报错
            # 在实际反爬中，通常需要下载 bg_ele 的图片，然后用 cv2.matchTemplate 识别缺口
            
            # 临时方案：尝试获取滑块容器宽度作为最大距离的参考
            # 真正的解决方案需要集成 OpenCV 识别逻辑
            gap_position = 200 # 默认值，实际应计算
            
            # 如果有背景图，尝试计算 (伪代码/预留接口)
            # if bg_ele:
            #    bg_img = bg_ele.src()
            #    gap_position = calculate_gap(bg_img)
            
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
