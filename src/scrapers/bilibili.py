"""
B站爬虫模块

提供B站内容爬取功能，包括：
1. 扫码登录
2. 获取推荐视频 (动态)
3. 获取视频字幕
4. 内容分析
"""

import json
import logging
import asyncio
import os
from typing import Optional, List, Dict, Any
# Change import to use login_v2
from bilibili_api import login_v2 as login, user, sync, Credential, homepage

logger = logging.getLogger(__name__)

class BilibiliScraper:
    CREDENTIAL_FILE = os.path.join("data", "credential.json")
    
    def __init__(self):
        """初始化BilibiliScraper"""
        self.credential = None
        self._login_in_progress = False
        self.login_manager = None # Store login manager instance
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # 尝试加载已保存的登录状态
        self._load_credential()
    
    def _load_credential(self) -> bool:
        """从文件加载凭据"""
        try:
            if os.path.exists(self.CREDENTIAL_FILE):
                with open(self.CREDENTIAL_FILE, 'r') as f:
                    data = json.load(f)
                    sessdata = data.get('sessdata')
                    bili_jct = data.get('bili_jct')
                    dedeuserid = data.get('dedeuserid')
                    buvid3 = data.get('buvid3')
                    
                    if sessdata and bili_jct and dedeuserid:
                        self.credential = Credential(
                            sessdata=sessdata, 
                            bili_jct=bili_jct, 
                            dedeuserid=dedeuserid,
                            buvid3=buvid3
                        )
                        return True
            return False
        except Exception as e:
            logger.error(f"加载凭据失败: {str(e)}")
            return False

    def save_credential(self):
        """保存凭据到文件"""
        if not self.credential:
            return
            
        try:
            creds = {
                "sessdata": self.credential.sessdata,
                "bili_jct": self.credential.bili_jct,
                "dedeuserid": self.credential.dedeuserid,
                "buvid3": self.credential.buvid3
            }
            
            with open(self.CREDENTIAL_FILE, "w") as f:
                json.dump(creds, f)
            logger.info("凭据已保存")
        except Exception as e:
            logger.error(f"保存凭据失败: {str(e)}")

    async def get_login_qr_code(self) -> Optional[Dict[str, str]]:
        """
        获取登录二维码
        Returns:
            包含 'url' (二维码内容) and 'key' (用于轮询) 的字典
        """
        try:
            self.login_manager = login.QrCodeLogin()
            await self.login_manager.generate_qrcode()
            
            # Access private member for URL as there is no public getter for raw URL
            # Alternatively we could parse it from terminal string but that's messy
            url = getattr(self.login_manager, '_QrCodeLogin__qr_link', '')
            
            # We don't need key for login_v2 class based approach, but UI expects it
            return {'qrcode': url, 'key': 'internal'}
        except Exception as e:
            logger.error(f"获取二维码失败: {str(e)}")
            return None

    async def poll_login_status(self, key: str) -> bool:
        """
        轮询登录状态
        Args:
            key: ignored in login_v2 class based approach
        Returns:
            True if login success, False otherwise
        """
        if not self.login_manager:
            return False
            
        try:
            status = await self.login_manager.check_state()
            # Check status enum
            if status == login.QrCodeLoginEvents.DONE:
                logger.info("登录成功")
                self.credential = self.login_manager.get_credential()
                self.save_credential()
                return True
            elif status == login.QrCodeLoginEvents.SCAN:
                # Scanned but not confirmed
                pass
            elif status == login.QrCodeLoginEvents.TIMEOUT:
                # Timeout
                pass
                
            return False
        except Exception as e:
            # Don't log every poll error to avoid spam, unless it's critical
            return False

    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        if self.credential and self.credential.sessdata:
            return True
        return False

    async def get_personal_recommendations(self) -> List[Dict]:
        """
        获取个性化推荐视频 (这里使用动态Feed)
        """
        if not self.credential:
            return []
            
        try:
            # 使用 User.get_dynamics 获取关注的UP主视频
            # Need self uid.
            if not self.credential.dedeuserid:
                return []
                
            u = user.User(uid=int(self.credential.dedeuserid), credential=self.credential)
            dynamics = await u.get_dynamics(offset=0)
            
            videos = []
            if 'cards' in dynamics:
                for card in dynamics['cards']:
                    desc = json.loads(card['card'])
                    # 筛选视频类型的动态
                    if 'title' in desc and 'bvid' in desc:
                        videos.append({
                            'title': desc['title'],
                            'bvid': desc['bvid'],
                            'desc': desc.get('desc', ''),
                            'pic': desc.get('pic', ''),
                            'owner': desc.get('owner', {}).get('name', 'Unknown'),
                            'pubdate': desc.get('pubdate', 0)
                        })
            return videos
        except Exception as e:
            logger.error(f"获取动态失败: {str(e)}")
            return []

    async def get_popular_videos(self) -> List[Dict]:
        """获取热门视频"""
        try:
            # 使用bilibili-api-python获取热门视频
            popular = await homepage.get_popular_videos()
            return popular.get('list', [])
        except Exception as e:
            logger.error(f"获取热门视频失败: {str(e)}")
            return []

    async def get_video_subtitle(self, bvid: str) -> str:
        """获取视频字幕"""
        # Placeholder for now, can be implemented later
        return ""
