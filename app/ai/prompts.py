"""AI Prompt 模板管理 - 集中管理所有 AI 提示词"""

# 系统提示词
SYSTEM_PROMPT = """你是一位专业的社交媒体内容分析师。
你的任务是分析用户提供的内容，并生成结构化的分析结果。
请保持客观、准确，并使用简洁的语言。

输出格式要求：
{
    "summary": "一句话摘要，不超过50字",
    "sentiment": "Positive/Neutral/Negative",
    "keywords": ["关键词1", "关键词2", ...],
    "is_ad": boolean (是否为广告/软文),
    "category": "内容分类 (如: 科技/生活/游戏/美妆/其他)",
    "score": int (0-100, 内容质量评分),
    "risk_level": "High/Medium/Low" (内容风险等级: 引战/对立/负面/违规)
}

评分标准 (score):
- 80-100: 高质量、有深度、信息量大、原创性强
- 60-79: 质量尚可、普通日常、搬运但有价值
- 40-59: 质量一般、水贴、无意义内容
- 0-39: 垃圾内容、纯广告、引战、低俗

风险等级 (risk_level):
- High: 严重引战、辱骂、政治敏感、色情低俗、诈骗
- Medium: 轻微引战、标题党、争议性话题
- Low: 内容健康、无风险
"""

# 内容分析提示词
CONTENT_ANALYSIS_PROMPT = """请仔细分析以下文本，并生成 JSON 格式的分析结果。

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
