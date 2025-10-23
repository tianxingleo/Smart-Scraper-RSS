import os
import openai
import logging
from openai import OpenAI
import json

# 全局客户端实例，初始为None，实现懒加载
client = None

def get_deepseek_client():
    """获取DeepSeek客户端，如果不存在则创建。"""
    global client
    if client is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            logging.error("DeepSeek API密钥未设置。请在GUI界面输入或创建.env文件。")
            raise ValueError("DeepSeek API Key not found.")
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com/v1"
        )
    return client

def analyze_content(content: str, api_key: str) -> dict:
    """
    Analyzes the given content using the DeepSeek API to determine its value,
    assign a score, and suggest tags.
    """
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
    except ValueError as e:
        logging.error(e)
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
    
    full_content = f"待分析内容：\n---\n{content}\n---\n"

    try:
        logging.info("发送内容到 DeepSeek 进行分析...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": full_content}
            ],
            temperature=0.1,
            max_tokens=500,
            stream=False,
            # 要求返回JSON格式
            response_format={"type": "json_object"}
        )
        result = response.choices[0].message.content
        usage = response.usage
        logging.info(
            f"DeepSeek 返回，消耗Token: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}"
        )
        logging.info(f"DeepSeek 分析结果: {result}")
        
        # 将JSON结果字符串解析为字典，并合并token使用情况
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