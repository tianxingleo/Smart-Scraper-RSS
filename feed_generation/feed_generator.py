from feedgen.feed import FeedGenerator
from datetime import datetime

def generate_rss(items, filename="output.xml"):
    fg = FeedGenerator()
    fg.title("Bilibili 高价值内容精选")
    fg.link(href='https://www.bilibili.com', rel='alternate')
    fg.description("由AI筛选的Bilibili高价值内容RSS源")

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
            <p>{item['content']}</p>
        """
        fe.content(content_html, type='html')
        
        if 'pubdate' in item:
            # Assuming pubdate is a unix timestamp
            fe.pubDate(datetime.fromtimestamp(item['pubdate']).strftime('%Y-%m-%d %H:%M:%S'))

    fg.rss_file(filename) 