"""滑块验证码求解工具 - 使用 Bezier 曲线模拟人类滑动行为"""
import time
import random
import numpy as np
from typing import List, Tuple

class CaptchaSolver:
    """滑块验证码求解器"""
    
    @staticmethod
    def generate_track(distance: int) -> List[int]:
        """
        生成滑动轨迹 - 使用物理加速模型
        
        Args:
            distance: 需要滑动的距离（像素）
            
        Returns:
            轨迹列表，每个元素表示每次移动的距离
        """
        track = []  # 轨迹列表
        current = 0  # 当前位移
        mid = distance * 4 / 5  # 减速阈值
        t = 0.2  # 计算间隔
        v = 0  # 初速度
        
        while current < distance:
            if current < mid:
                # 加速阶段 - 加速度为正
                a = random.uniform(2, 5)
            else:
                # 减速阶段 - 加速度为负
                a = -random.uniform(3, 5)
            
            # 计算位移 s = v*t + 0.5*a*t^2
            move = v * t + 0.5 * a * t * t
            # 更新速度 v = v0 + a*t
            v = v + a * t
            
            # 防止过冲
            if current + move > distance:
                move = distance - current
            
            track.append(round(move))
            current += move
        
        return track
    
    @staticmethod
    def generate_bezier_track(distance: int) -> List[Tuple[int, int]]:
        """
        使用 Bezier 曲线生成更自然的滑动轨迹
        
        Args:
            distance: 需要滑动的距离
            
        Returns:
            (x, y) 坐标点列表
        """
        # 三阶 Bezier 曲线的四个控制点
        p0 = np.array([0, 0])
        p1 = np.array([distance * 0.3, random.randint(-10, 10)])
        p2 = np.array([distance * 0.7, random.randint(-15, 15)])
        p3 = np.array([distance, random.randint(-5, 5)])
        
        track = []
        steps = random.randint(30, 50)  # 随机步数
        
        for i in range(steps + 1):
            t = i / steps
            # Bezier 曲线公式
            point = (1-t)**3 * p0 + 3*(1-t)**2*t * p1 + 3*(1-t)*t**2 * p2 + t**3 * p3
            track.append((int(point[0]), int(point[1])))
        
        return track
    
    @staticmethod
    def add_human_behavior(track: List[int]) -> List[int]:
        """
        添加人类行为特征 - 随机抖动
        
        Args:
            track: 原始轨迹
            
        Returns:
            添加抖动后的轨迹
        """
        human_track = []
        for move in track:
            # 添加随机抖动
            jitter = random.randint(-2, 2)
            human_track.append(move + jitter)
        
        # 末尾添加小幅回退（模拟人类修正）
        if len(human_track) > 5:
            human_track.append(random.randint(-3, -1))
            human_track.append(random.randint(1, 3))
        
        return human_track
    
    @staticmethod
    def get_slide_delay(track: List[int]) -> List[float]:
        """
        生成每步的延迟时间 - 模拟人类反应时间
        
        Args:
            track: 滑动轨迹
            
        Returns:
            延迟时间列表（秒）
        """
        delays = []
        for _ in track:
            # 随机延迟 0.01-0.03 秒
            delay = random.uniform(0.01, 0.03)
            delays.append(delay)
        return delays
    
    def solve(self, gap_position: int) -> Tuple[List[int], List[float]]:
        """
        求解滑块验证码
        
        Args:
            gap_position: 缺口位置（像素）
            
        Returns:
            (轨迹, 延迟时间列表)
        """
        # 生成基础轨迹
        track = self.generate_track(gap_position)
        
        # 添加人类行为
        track = self.add_human_behavior(track)
        
        # 生成延迟
        delays = self.get_slide_delay(track)
        
        return track, delays

    def identify_gap(self, bg_bytes: bytes, slider_bytes: bytes) -> int:
        """
        识别缺口位置
        
        Args:
            bg_bytes: 背景图片字节流
            slider_bytes: 滑块图片字节流
            
        Returns:
            缺口 X 坐标
        """
        try:
            import cv2
            
            # 字节流转 numpy 数组
            bg_arr = np.frombuffer(bg_bytes, np.uint8)
            slider_arr = np.frombuffer(slider_bytes, np.uint8)
            
            # 解码为图像
            bg_img = cv2.imdecode(bg_arr, cv2.IMREAD_COLOR)
            slider_img = cv2.imdecode(slider_arr, cv2.IMREAD_COLOR)
            
            # 边缘检测 (Canny)
            bg_edge = cv2.Canny(bg_img, 100, 200)
            slider_edge = cv2.Canny(slider_img, 100, 200)
            
            # 转换图片格式
            bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
            slider_pic = cv2.cvtColor(slider_edge, cv2.COLOR_GRAY2RGB)
            
            # 模板匹配
            res = cv2.matchTemplate(bg_pic, slider_pic, cv2.TM_CCOEFF_NORMED)
            
            # 获取最佳匹配位置
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            # max_loc 是最佳匹配的左上角坐标 (x, y)
            # 通常滑块验证码只需要 X 坐标
            return max_loc[0]
            
        except ImportError:
            print("OpenCV not installed. Please install opencv-python.")
            return 200 # Fallback
        except Exception as e:
            print(f"Gap identification failed: {e}")
            return 200 # Fallback

# 全局实例
captcha_solver = CaptchaSolver()
