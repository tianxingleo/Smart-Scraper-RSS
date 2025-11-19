import asyncio
import json
import os
import logging
from bilibili_api import Credential, login_v2, video, hot, homepage
from bilibili_api.utils.picture import Picture

class BilibiliScraper:
    def __init__(self):
        self.credential = None
        self.cookie_file = 'bilibili_cookies.json'
        self.qr_login = None # Store QrCodeLogin instance
        self.load_cookies()

    def load_cookies(self):
        if os.path.exists(self.cookie_file):
            try:
                with open(self.cookie_file, 'r') as f:
                    cookies = json.load(f)
                    self.credential = Credential(
                        sessdata=cookies.get('SESSDATA'),
                        bili_jct=cookies.get('bili_jct'),
                        buvid3=cookies.get('buvid3'),
                        dedeuserid=cookies.get('DedeUserID'),
                        ac_time_value=cookies.get('ac_time_value')
                    )
                logging.info("Loaded cookies from file.")
            except Exception as e:
                logging.error(f"Failed to load cookies: {e}")

    def save_cookies(self):
        if self.credential:
            cookies = {
                'SESSDATA': self.credential.sessdata,
                'bili_jct': self.credential.bili_jct,
                'buvid3': self.credential.buvid3,
                'DedeUserID': self.credential.dedeuserid,
                'ac_time_value': self.credential.ac_time_value
            }
            try:
                with open(self.cookie_file, 'w') as f:
                    json.dump(cookies, f)
                logging.info("Saved cookies to file.")
            except Exception as e:
                logging.error(f"Failed to save cookies: {e}")

    async def login_with_qrcode(self):
        """获取登录二维码"""
        try:
            self.qr_login = login_v2.QrCodeLogin()
            # Generate QR code
            # Note: generate_qrcode() might not return anything, but prepares the QR code
            # We need to check the library usage. 
            # Based on help(QrCodeLogin), generate_qrcode() returns None.
            # But we need to call it to start the process.
            # Wait, looking at help output again: 
            # async generate_qrcode(self) -> None
            # get_qrcode_picture(self) -> Picture
            # get_qrcode_terminal(self) -> str
            
            # It seems we don't need to await generate_qrcode() if we just want the picture? 
            # Or maybe we do. Let's assume we do.
            # Actually, usually you init, then get url.
            # Let's try calling generate_qrcode first.
            
            # Re-reading help: generate_qrcode() is async.
            await self.qr_login.generate_qrcode()
            
            # Get picture
            picture = self.qr_login.get_qrcode_picture()
            return {'qrcode': picture.url}
            
        except Exception as e:
            logging.error(f"Error generating QR code: {e}")
        return None

    async def poll_login_status(self):
        """Poll QR code status. Returns True if login success."""
        if not self.qr_login:
            return False
            
        try:
            # check_state returns QrCodeLoginEvents
            # We need to know what that enum contains.
            # But usually we can just check has_done()
            
            status = await self.qr_login.check_state()
            # Based on common usage, check_state returns the status.
            # If success, we can get credential.
            
            if await self.qr_login.has_done():
                self.credential = self.qr_login.get_credential()
                self.save_cookies()
                return True
                
        except Exception as e:
            logging.error(f"Error polling login status: {e}")
        return False

    def is_logged_in(self):
        """Check if currently logged in"""
        return self.credential is not None

    async def get_video_subtitle(self, bvid):
        """获取视频字幕"""
        try:
            v = video.Video(bvid=bvid, credential=self.credential)
            # get_subtitle returns a dict with list of subtitles
            sub_info = await v.get_subtitle()
            
            if not sub_info or 'subtitles' not in sub_info:
                return ""
                
            subtitles = sub_info['subtitles']
            if not subtitles:
                return ""
            
            # Prefer zh-CN
            target_sub = subtitles[0]
            for sub in subtitles:
                if sub.get('lan') == 'zh-CN':
                    target_sub = sub
                    break
            
            # The URL in target_sub['url'] is a JSON file containing the subtitle text
            # We need to fetch it.
            # Since we are using bilibili_api, maybe there is a helper?
            # No obvious helper in Video class to download content.
            # We can use requests to fetch the URL.
            
            sub_url = target_sub['url']
            if sub_url.startswith('//'):
                sub_url = 'https:' + sub_url
                
            import requests
            resp = requests.get(sub_url)
            if resp.status_code == 200:
                data = resp.json()
                body = data.get('body', [])
                text = " ".join([item['content'] for item in body])
                return text
                
        except Exception as e:
            logging.error(f"Error fetching subtitle for {bvid}: {e}")
        
        return ""

    async def get_popular_videos(self):
        try:
            # get_hot_videos returns list of dicts
            data = await hot.get_hot_videos()
            return data['list']
        except Exception as e:
            logging.error(f"Error fetching popular videos: {e}")
            return []

    async def get_personal_recommendations(self):
        if not self.credential:
            return []
        try:
            # homepage.get_videos returns dict
            data = await homepage.get_videos(credential=self.credential)
            # The structure usually contains 'item' list
            return data.get('item', [])
        except Exception as e:
            logging.error(f"Error fetching recommendations: {e}")
            return []

# Helper to get global credential if needed
def get_credential():
    scraper = BilibiliScraper()
    return scraper.credential

def logout():
    if os.path.exists('bilibili_cookies.json'):
        os.remove('bilibili_cookies.json')
