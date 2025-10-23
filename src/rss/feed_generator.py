"""
RSS订阅源生成模块
"""
import os
import logging
from typing import List, Dict, Any
from feedgen.feed import FeedGenerator as FG
from datetime import datetime
import pytz
from src.utils.deep_seek_evaluator import DeepSeekEvaluator

class FeedGenerator:
    def __init__(self, title: str, link: str, description: str):
        """初始化RSS生成器
        
        Args:
            title (str): RSS源标题
            link (str): RSS源链接
            description (str): RSS源描述
        """
        self.fg = FG()
        self.fg.title(title)
        self.fg.link(href=link, rel='alternate')
        self.fg.description(description)
        self.fg.language('zh-CN')
        self.deepseek_evaluator = DeepSeekEvaluator()
        
    def add_item(self, content: Dict[str, Any], analysis: Dict[str, Any]):
        """添加RSS条目
        
        Args:
            content (Dict[str, Any]): 内容信息
            analysis (Dict[str, Any]): 分析结果
        """
        fe = self.fg.add_entry()
        fe.title(content['title'])
        fe.link(href=content.get('url', ''))
        
        # 构建描述，包含AI分析结果
        description = f"""
{content['description']}

---
AI分析评分：{analysis['score']}/10
推荐理由：{analysis['reason']}
        """
        fe.description(description)
        
        # 设置作者
        fe.author({'name': content.get('author', '未知作者')})
        
        # 设置发布时间
        if 'publish_time' in content:
            tz = pytz.timezone('Asia/Shanghai')
            pub_date = datetime.fromtimestamp(content['publish_time'], tz)
            fe.published(pub_date)
        
        # 添加封面图片
        if 'cover_url' in content:
            fe.enclosure(content['cover_url'], 0, 'image/jpeg')
            
    def generate_xml(self) -> str:
        """生成RSS XML
        
        Returns:
            str: RSS XML字符串
        """
        return self.fg.rss_str(pretty=True).decode('utf-8')

class RSSFeedGenerator:
    """RSS订阅源生成类"""
    
    def __init__(self):
        """初始化生成器"""
        self.feed = FeedGenerator(os.getenv('RSS_TITLE', '智能内容精选'), os.getenv('RSS_LINK', 'http://example.com/feed'), os.getenv('RSS_DESCRIPTION', 'AI筛选的优质内容聚合'))
            
    def generate_feed(self, videos: List[Dict[str, Any]], output_file: str = 'feed.xml'):
        """生成RSS订阅源
        
        Args:
            videos: 视频内容列表
            output_file: 输出文件名
        """
        # 清空现有条目
        self.feed.fg.clear()
        
        # 过滤有价值的视频
        valuable_videos = []
        for video in videos:
            try:
                evaluation = self.deepseek_evaluator.evaluate_content(video)
                if evaluation.get("is_worth_saving", False):
                    video["evaluation"] = evaluation
                    valuable_videos.append(video)
            except Exception as e:
                logging.error(f"内容评估失败: {str(e)}")
                continue
        
        # 添加新条目（使用过滤后的有价值视频）
        for video in valuable_videos:
            self.feed.add_item(video, video.get('evaluation', {}))
            
        # 保存文件
        self.feed.generate_xml()
        self.feed.fg.rss_file(output_file)
        
    def get_feed_content(self) -> str:
        """获取RSS内容字符串
        
        Returns:
            RSS内容的字符串形式
        """
        return self.feed.generate_xml() 