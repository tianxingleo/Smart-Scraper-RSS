import logging
import os
import json
import asyncio

# 核心修改 1: 导入正确的模块。新版 bilibili_api 使用 'hot' 获取热门，而不是 'homepage'
# 如果报错 ImportError，请确保安装的是: pip install bilibili-api-python
try:
    from bilibili_api import login, user, sync, Credential, hot
except ImportError as e:
    logging.error(f"导入库失败: {e}")
    logging.error("请检查是否安装了正确的库: pip install bilibili-api-python")
    # 为了防止 IDE 报错，定义空变量
    login = user = sync = Credential = hot = None

logger = logging.getLogger("BilibiliScraper")

class BilibiliScraper:
    def __init__(self):
        # 核心修改 2: 优先尝试从环境变量读取 Cookies
        # 这样可以绕过 412 风控问题
        self.sessdata = os.getenv("BILIBILI_SESSDATA", "")
        self.bili_jct = os.getenv("BILIBILI_BILI_JCT", "")
        self.buvid3 = os.getenv("BILIBILI_BUVID3", "")
        self.dedeuserid = os.getenv("BILIBILI_DEDEUSERID", "")
        self.credential = None

    async def _authenticate(self):
        """处理认证逻辑：优先 Cookie，失败则尝试二维码"""
        
        # 1. 尝试 Cookie 登录
        if self.sessdata and self.bili_jct:
            logger.info("检测到环境变量 Cookies，尝试直接登录...")
            self.credential = Credential(
                sessdata=self.sessdata,
                bili_jct=self.bili_jct,
                buvid3=self.buvid3,
                dedeuserid=self.dedeuserid
            )
            if await self.credential.check_valid():
                logger.info("Cookies 有效，登录成功。")
                return
            else:
                logger.warning("Cookies 已失效，转为尝试二维码登录。")
        
        # 2. 尝试二维码登录 (可能触发 412 错误)
        logger.info("正在尝试自动登录 (QR码)...")
        try:
            qr_login = login.QRLogin()
            qr_data = await qr_login.get_qrcode()
            print(f"\n【请使用B站App扫描二维码登录】\n或者在浏览器打开此链接: {qr_data.url}\n")
            
            # 可以在这里调用生成二维码图片的逻辑
            # qr_data.image.show() 
            
            user_data = await qr_login.poll()
            logger.info("扫码登录成功！")
            self.credential = user_data['credential']
            
            # 建议：打印出 Cookie 供用户保存到 .env，避免下次再扫码
            logger.info(f"SESSDATA: {self.credential.sessdata}")
            logger.info(f"BILI_JCT: {self.credential.bili_jct}")
            
        except Exception as e:
            logger.error(f"自动登录失败: {e}")
            if "412" in str(e):
                logger.error("【关键错误】B站拒绝了二维码请求 (412)。")
                logger.error("解决方案: 请在浏览器登录B站，按 F12 -> Application -> Cookies，复制 SESSDATA 和 bili_jct 到您的 .env 文件中。")
            raise e

    async def fetch_hot_videos(self, limit=20):
        """获取热门视频"""
        # 确保已登录
        if not self.credential:
            await self._authenticate()

        logger.info("正在获取热门视频...")
        try:
            # 核心修改 3: 使用 hot.get_hot_list() 替代 homepage.get_popular_videos()
            # bilibili_api 的新版本 API 变动
            data = await hot.get_hot_list()
            
            # data 可能是 list 或 dict，取决于具体 API 版本，这里做兼容处理
            video_list = data.get('list', []) if isinstance(data, dict) else data
            
            results = []
            for v in video_list[:limit]:
                # 提取关键信息
                item = {
                    'title': v.get('title', 'No Title'),
                    'bvid': v.get('bvid'),
                    'author': v.get('owner', {}).get('name', 'Unknown'),
                    'play_count': v.get('stat', {}).get('view', 0),
                    'description': v.get('desc', ''),
                    'pic': v.get('pic', ''),
                    'link': f"https://www.bilibili.com/video/{v.get('bvid')}"
                }
                results.append(item)
            
            logger.info(f"已获取 {len(results)} 条热门视频。")
            return results

        except AttributeError:
            logger.error("获取热门视频失败: 模块方法不存在。请检查 bilibili_api 版本。")
            return []
        except Exception as e:
            logger.error(f"获取数据时发生未知错误: {e}")
            return []

# 这是一个同步的入口函数，供外部调用
def get_bilibili_hot():
    scraper = BilibiliScraper()
    return sync(scraper.fetch_hot_videos())

if __name__ == "__main__":
    # 本地测试代码
    logging.basicConfig(level=logging.INFO)
    res = get_bilibili_hot()
    for v in res:
        print(f"{v['title']} - {v['link']}")
