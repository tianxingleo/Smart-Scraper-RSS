from feedgen.feed import FeedGenerator
from datetime import datetime

def generate_rss(items, filename="output.xml", feed_metadata=None):
    if feed_metadata is None:
        feed_metadata = {}
        
    fg = FeedGenerator()
    fg.title(feed_metadata.get('title', "Bilibili 高价值内容精选"))
    fg.link(href=feed_metadata.get('link', 'https://www.bilibili.com'), rel='alternate')
    fg.description(feed_metadata.get('description', "由AI筛选的Bilibili高价值内容RSS源"))

    for item in items:
        fe = fg.add_entry()
        fe.id(item['bvid'])
        fe.title(item['title'])
        fe.link(href=item['url'])
        
        # 直接从item的顶层获取分析结果
        content_html = f"""
            <p><b>AI 评分:</b> {item.get('score', 'N/A')}</p>
            <p><b>AI 标签:</b> {', '.join(item.get('tags', []))}</p>
            <p><b>AI 分析:</b> {item.get('analysis', 'No analysis available.')}</p>
            <hr>
            <p><b>原始简介:</b></p>
            <p>{item.get('desc', '无简介')}</p>
        """
        fe.content(content_html, type='html')
        
        pubdate = item.get('pubdate') or item.get('ctime')
        if pubdate:
            try:
                # Assuming pubdate is a unix timestamp
                fe.pubDate(datetime.fromtimestamp(pubdate, tz=datetime.now().astimezone().tzinfo))
            except Exception:
                pass

    try:
        fg.rss_file(filename)
        return True, f"RSS feed generated successfully at {filename}"
    except Exception as e:
        return False, f"Failed to generate RSS feed: {str(e)}"