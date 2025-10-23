# fetch_ids.py
import asyncio
import sys
from bilibili_api import popular

async def main():
    """
    获取B站热门视频的BVID列表并打印到标准输出。
    """
    try:
        popular_videos_data = await popular.get_popular_list()
        bvids = [video_item['bvid'] for video_item in popular_videos_data.get('list', [])[:50]]
        for bvid in bvids:
            print(bvid)
    except Exception as e:
        print(f"Error fetching popular videos: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 