import os
from openai import OpenAI
from app.ai.prompts import get_content_analysis_prompt, SYSTEM_PROMPT
import json

class AIProcessor:
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable not set")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def analyze(self, text: str) -> dict:
        """
        分析文本内容
        
        Args:
            text: 要分析的文本
            
        Returns:
            分析结果字典，包含 summary, sentiment, keywords, is_ad, category
        """
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": get_content_analysis_prompt(text)}
                ],
                response_format={'type': 'json_object'},
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return {
                "summary": "分析失败",
                "sentiment": "Neutral",
                "keywords": [],
                "is_ad": False,
                "category": "其他",
                "score": 0,
                "risk_level": "Unknown"
            }
