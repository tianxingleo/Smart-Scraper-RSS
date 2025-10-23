"""
B站爬虫模块

提供B站内容爬取功能，包括：
1. 扫码登录
2. 获取推荐视频
3. 获取视频字幕
4. 内容分析
"""

import json
import time
import logging
import asyncio
from typing import Optional, List, Dict, Any, Callable
import os
from bilibili_api import homepage, video, Credential, sync

logger = logging.getLogger(__name__)

# 从环境变量获取凭据
BILI_SESSDATA = os.environ.get("BILI_SESSDATA", "")
BILI_BILI_JCT = os.environ.get("BILI_BILI_JCT", "")
BILI_DEDEUSERID = os.environ.get("BILI_DEDEUSERID", "")

def get_credential():
    """获取凭据"""
    if BILI_SESSDATA and BILI_BILI_JCT and BILI_DEDEUSERID:
        return Credential(sessdata=BILI_SESSDATA, bili_jct=BILI_BILI_JCT, dedeuserid=BILI_DEDEUSERID)
    return None

async def get_personal_recommendations(credential: Credential) -> List[Dict]:
    """获取个性化推荐视频"""
    try:
        # 使用bilibili-api-python获取推荐视频
        recommendations = await homepage.get_videos(credential=credential)
        return recommendations.get('item', [])
    except Exception as e:
        logger.error(f"获取个性化推荐失败: {str(e)}")
        return []

def get_popular_videos() -> List[Dict]:
    """获取热门视频"""
    try:
        # 使用bilibili-api-python获取热门视频
        popular = sync(homepage.get_popular_videos())
        return popular.get('list', [])
    except Exception as e:
        logger.error(f"获取热门视频失败: {str(e)}")
        return []

def logout():
    """退出登录"""
    cookies_file = os.path.join("data", "bilibili_cookies.json")
    if os.path.exists(cookies_file):
        os.remove(cookies_file)

class BilibiliScraper:
    COOKIES_FILE = os.path.join("data", "bilibili_cookies.json")
    
    def __init__(self):
        """初始化BilibiliScraper"""
        self.cookies = None
        self._login_in_progress = False
        
        # 尝试加载已保存的登录状态
        self._load_cookies()
    
    def _load_cookies(self) -> bool:
        """从文件加载cookies"""
        try:
            if os.path.exists(self.COOKIES_FILE):
                with open(self.COOKIES_FILE, 'r') as f:
                    self.cookies = json.load(f)
                return True
            return False
        except Exception as e:
            logger.error(f"加载cookies失败: {str(e)}")
            return False
    
    async def login_with_qrcode(self) -> dict:
        """
        登录B站（扫码登录），返回二维码信息
        Returns:
            包含二维码图片URL和其他信息的字典，如果已自动跳转则返回None
        """
        # 由于playwright集成问题，暂时返回空值使用bilibili-api-python的登录方式
        logger.info("使用bilibili-api-python进行登录")
        return None
    
    def is_logged_in(self) -> bool:
        """检查是否已登录，如果在登录过程中则返回False"""
        # 简单检查是否有凭据
        credential = get_credential()
        if credential:
            try:
                # 尝试获取用户信息来验证凭据是否有效
                sync(credential.get_user_info())
                return True
            except:
                return False
        return False
    
    def save_cookies(self):
        """保存cookies到文件"""
        pass  # 使用bilibili-api-python不需要手动保存cookies
