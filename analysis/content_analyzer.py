import os
import logging
from openai import OpenAI
import json

class ContentAnalyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1"
            )
        else:
            logging.warning("DeepSeek API Key not found during initialization.")

    def analyze_content(self, title: str, desc: str, subtitle: str) -> dict:
        """
        Analyzes the given content using the DeepSeek API.
        """
        if not self.client:
            # Try to re-initialize if key was set later
            self.api_key = self.api_key or os.getenv("DEEPSEEK_API_KEY")
            if self.api_key:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            else:
                logging.error("DeepSeek API client not initialized.")
                return None

        prompt = (
            "你是一个内容审查员，负责对互联网内容进行价值评估。你的目标是筛选出对用户有益、高质量的内容，并过滤掉低价值、引战、或有害的内容。请遵循以下评分标准和格式要求：\n\n"
            "**评分标准 (0-10分):**\n"
            "- **8-10分 (强烈推荐):** 内容具有很高的信息量、深度、启发性或艺术价值。例如：高质量的科普视频、深入的技术教程、优美的音乐MV、有见地的时事评论。\n"
            "- **5-7分 (值得一看):** 内容健康、有趣、信息准确，但可能深度不足或较为普通。例如：日常Vlog、有趣的游戏集锦、常规新闻资讯。\n"
            "- **2-4分 (价值较低):** 内容质量不高，可能包含营销推广、标题党、少量夸大事实。例如：诱导关注的营销文案、内容空洞的视频。\n"
            "- **0-1分 (坚决过滤):** 内容包含引战、制造对立、虚假信息、人身攻击等明显负面或有害倾向。\n\n"
            "**输出格式:**\n"
            "请严格按照以下JSON格式返回，不要包含任何额外说明：\n"
            "{\"score\": [评分整数], \"tags\": [\"标签列表\"], \"is_negative\": [布尔值 true/false], \"analysis\": \"一句话分析摘要\"}"
        )
        
        full_content = f"标题: {title}\n简介: {desc}\n字幕/内容: {subtitle}\n"

        try:
            logging.info(f"发送视频 '{title}' 到 DeepSeek 进行分析...")
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": full_content}
                ],
                temperature=0.1,
                max_tokens=500,
                stream=False,
                response_format={"type": "json_object"}
            )
            result = response.choices[0].message.content
            usage = response.usage
            logging.info(
                f"DeepSeek 返回，消耗Token: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}"
            )
            
            try:
                analysis_data = json.loads(result)
                analysis_data['prompt_tokens'] = usage.prompt_tokens
                analysis_data['completion_tokens'] = usage.completion_tokens
                return analysis_data
            except json.JSONDecodeError:
                logging.error(f"无法解析来自DeepSeek的JSON响应: {result}")
                return None

        except Exception as e:
            logging.error(f"DeepSeek 分析失败: {e}")
            return None