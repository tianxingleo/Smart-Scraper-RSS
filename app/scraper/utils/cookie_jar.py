"""Cookie 持久化管理 - 保存和加载浏览器 Cookie"""
import json
import os
from typing import List, Dict
from pathlib import Path

class CookieJar:
    """Cookie 管理器"""
    
    def __init__(self, storage_dir: str = "./data/cookies"):
        """
        初始化 Cookie 管理器
        
        Args:
            storage_dir: Cookie 存储目录
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_cookies(self, platform: str, cookies: List[Dict]):
        """
        保存 Cookie 到文件
        
        Args:
            platform: 平台名称 (bilibili, xiaohongshu)
            cookies: Cookie 列表
        """
        file_path = self.storage_dir / f"{platform}_cookies.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(cookies, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存 Cookie 失败: {e}")
            return False
    
    def load_cookies(self, platform: str) -> List[Dict]:
        """
        从文件加载 Cookie
        
        Args:
            platform: 平台名称
            
        Returns:
            Cookie 列表，如果文件不存在返回空列表
        """
        file_path = self.storage_dir / f"{platform}_cookies.json"
        
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载 Cookie 失败: {e}")
            return []
    
    def clear_cookies(self, platform: str):
        """
        清除指定平台的 Cookie
        
        Args:
            platform: 平台名称
        """
        file_path = self.storage_dir / f"{platform}_cookies.json"
        
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception as e:
                print(f"清除 Cookie 失败: {e}")
                return False
        return True
    
    def is_cookie_valid(self, platform: str) -> bool:
        """
        检查 Cookie 是否存在且有效
        
        Args:
            platform: 平台名称
            
        Returns:
            Cookie 是否有效
        """
        cookies = self.load_cookies(platform)
        return len(cookies) > 0

# 全局实例
cookie_jar = CookieJar()
