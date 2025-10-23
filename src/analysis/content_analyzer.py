"""
内容分析模块

使用DeepSeek API分析内容的价值和倾向性
"""

import openai
import logging
import time
import json
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self):
        """初始化内容分析器"""
        self.api_key = None
        self.client = None
    
    def set_api_key(self, api_key: str):
        """设置API密钥
        
        Args:
            api_key (str): API密钥
        """
        self.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    async def analyze_content(self, title: str, content: str, author: str) -> Dict[str, Any]:
        """分析内容
        
        Args:
            title (str): 标题
            content (str): 内容
            author (str): 作者
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        if not self.api_key or not self.client:
            logger.warning("未设置API密钥，跳过内容分析")
            return None
        
        try:
            # 构建提示词
            prompt = f"""请分析以下B站视频内容：

标题：{title}
作者：{author}
简介：{content}

请从以下几个方面进行分析：
1. 内容摘要（100字以内）
2. 推荐指数（1-10分）
3. 内容标签（3-5个关键词）
4. 内容质量评估
5. 受众分析
6. 创作者评价

请用JSON格式返回分析结果，包含以下字段：
- summary: 内容摘要
- score: 推荐指数
- tags: 内容标签数组
- quality: 内容质量评估
- audience: 受众分析
- creator: 创作者评价
"""
            
            # 调用API
            logger.info(f"正在分析内容: {title}")
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的视频内容分析师，擅长分析B站视频内容的质量和价值。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # 解析响应
            result = json.loads(response.choices[0].message.content)
            logger.info(f"内容分析完成: {title}")
            
            return result
            
        except Exception as e:
            logger.error(f"内容分析失败: {str(e)}")
            return None
    
    def analyze_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """分析视频内容
        
        Args:
            video: 视频信息字典
            
        Returns:
            添加了分析结果的视频信息字典
        """
        # 确保必要的字段存在
        title = video.get('title', '')
        desc = video.get('desc', '')
        subtitle = video.get('subtitle', '')
        
        # 分析内容
        analysis = self.analyze_content(title, desc, '')
        
        # 添加分析结果
        video['deepseek_analysis'] = analysis
        
        # 添加2秒延迟，避免API请求过快
        time.sleep(2)
        
        return video 