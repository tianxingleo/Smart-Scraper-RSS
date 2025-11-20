import sys
import os
# 添加项目根目录 to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.scraper.strategies import XiaoheiheScraper, CoolAPKScraper

def test_xiaoheihe():
    print("\nTesting Xiaoheihe Scraper...")
    scraper = XiaoheiheScraper()
    # 使用一个示例 URL (实际测试可能需要真实 URL，这里主要测试代码跑通)
    url = "https://api.xiaoheihe.cn/v3/bbs/app/api/web/share?link_id=137229325" 
    try:
        item = scraper.scrape(url)
        print(f"[OK] Scrape Success!")
        print(f"Title: {item.title}")
        print(f"Content Length: {len(item.content)}")
        print(f"Images: {len(item.images.split(',')) if item.images else 0}")
    except Exception as e:
        print(f"[FAIL] Scrape Failed: {e}")

def test_coolapk():
    print("\nTesting CoolAPK Scraper...")
    scraper = CoolAPKScraper()
    # 示例 URL
    url = "https://www.coolapk.com/feed/56789"
    try:
        item = scraper.scrape(url)
        print(f"[OK] Scrape Success!")
        print(f"Title: {item.title}")
        print(f"Content Length: {len(item.content)}")
    except Exception as e:
        print(f"[FAIL] Scrape Failed: {e}")

if __name__ == "__main__":
    # 注意：由于没有真实 URL 和网络环境，这里可能会失败或超时
    # 主要验证类是否能正确实例化和调用
    print("Starting Scraper Tests...")
    try:
        test_xiaoheihe()
    except Exception as e:
        print(f"Xiaoheihe test error: {e}")
        
    try:
        test_coolapk()
    except Exception as e:
        print(f"CoolAPK test error: {e}")
