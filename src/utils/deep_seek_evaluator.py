import requests
import json
from typing import Dict, Any
from src.utils.persistence import Persistence

class DeepSeekEvaluator:
    def __init__(self):
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        try:
            with open("data/deepseek_config.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载DeepSeek配置失败: {str(e)}")
            return {}
    
    def evaluate_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用DeepSeek API评估内容价值
        """
        if not self.config.get("api_key"):
            raise ValueError("未配置DeepSeek API密钥")
        
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # 构建提示词，根据需要调整
        prompt = self._build_prompt(content)
        
        data = {
            "model": "deepseek-chat",
            "prompt": prompt,
            "max_tokens": 1024,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # 解析返回结果
            evaluation = self._parse_result(result)
            return evaluation
        except Exception as e:
            print(f"调用DeepSeek API失败: {str(e)}")
            return {"error": str(e)}
    
    def _build_prompt(self, content: Dict[str, Any]) -> str:
        # 根据视频标题、描述等构建评估提示词
        prompt = f"""
请评估以下B站视频内容的价值：
标题: {content.get('title', '')}
描述: {content.get('description', '')}
标签: {content.get('tags', [])}
播放量: {content.get('views', 0)}

请以JSON格式返回评估结果，包含以下字段：
- score: 综合评分 (0-10分)
- category: 内容类别
- is_worth_saving: 是否值得保存 (true/false)
- summary: 内容摘要
- keywords: 关键词列表
- quality: 内容质量评价

只返回JSON结果，不要包含其他内容。
"""
        return prompt
    
    def _parse_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        # 解析API返回结果
        try:
            text = result["choices"][0]["text"]
            return json.loads(text)
        except Exception as e:
            print(f"解析DeepSeek返回结果失败: {str(e)}")
            return {"error": "无法解析API返回结果"}