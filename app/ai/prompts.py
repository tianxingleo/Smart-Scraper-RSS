"""AI Prompt 模板管理 - 集中管理所有 AI 提示词"""

# 系统提示词
SYSTEM_PROMPT = """你是一位专业的社交媒体内容分析师。
你的任务是分析用户提供的内容，并生成结构化的分析结果。
请保持客观、准确，并使用简洁的语言。"""

# 内容分析提示词
CONTENT_ANALYSIS_PROMPT = """请仔细分析以下文本，并生成 JSON 格式的分析结果。

要求：
1. summary: 生成一句话摘要（50字以内）
2. sentiment: 判断情感倾向 (Positive/Neutral/Negative)
3. keywords: 提取3-5个关键词
4. is_ad: 判断是否为广告内容 (true/false)
5. category: 内容分类（科技/生活/娱乐/教育/其他）

请严格按照以下 JSON 格式返回：
{{
    "summary": "一句话摘要",
    "sentiment": "Positive",
    "keywords": ["关键词1", "关键词2", "关键词3"],
    "is_ad": false,
    "category": "科技"
}}

待分析文本：
{content}
"""

# 标题生成提示词
TITLE_GENERATION_PROMPT = """请为以下内容生成一个吸引人的标题。

要求：
- 标题长度：15-30字
- 准确概括内容核心
- 使用吸引眼球的词汇
- 避免标题党

内容：
{content}

请只返回标题文本，不要其他内容。
"""

# 摘要生成提示词
SUMMARY_PROMPT = """请为以下内容生成摘要。

要求：
- 摘要长度：{max_length}字以内
- 保留关键信息
- 语言简洁流畅

内容：
{content}

请只返回摘要文本，不要其他内容。
"""

# 关键词提取提示词
KEYWORDS_PROMPT = """请从以下内容中提取关键词。

要求：
- 提取 {num_keywords} 个最重要的关键词
- 按重要性排序
- 返回 JSON 数组格式

内容：
{content}

请严格按照以下格式返回：
["关键词1", "关键词2", "关键词3"]
"""

def get_content_analysis_prompt(content: str) -> str:
    """获取内容分析提示词"""
    return CONTENT_ANALYSIS_PROMPT.format(content=content)

def get_title_generation_prompt(content: str) -> str:
    """获取标题生成提示词"""
    return TITLE_GENERATION_PROMPT.format(content=content)

def get_summary_prompt(content: str, max_length: int = 100) -> str:
    """获取摘要生成提示词"""
    return SUMMARY_PROMPT.format(content=content, max_length=max_length)

def get_keywords_prompt(content: str, num_keywords: int = 5) -> str:
    """获取关键词提取提示词"""
    return KEYWORDS_PROMPT.format(content=content, num_keywords=num_keywords)
