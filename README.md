🎯 Smart-Scraper-RSS (AI 增强版)

下一代智能内容聚合系统

一个基于 Windows/Linux 的现代化桌面应用，支持爬取 哔哩哔哩、小红书、小黑盒、酷安 等平台内容，通过 DeepSeek AI 进行深度分析、评分与清洗，最终生成高质量的 RSS 订阅源。

English Version Below

🚀 项目核心目标

本项目旨在解决信息过载与“垃圾内容”问题，通过本地化的智能代理实现：

多源内容采集：支持 B站视频、小红书笔记、小黑盒游戏资讯、酷安应用评论的自动化抓取。

深度内容处理：

B站增强：自动提取视频 CC 字幕，将其与标题、简介合并，让您不看视频也能读懂核心内容。

去噪清洗：自动去除广告、推广软文。

AI 价值评估：

调用 DeepSeek/ChatGPT 模型对内容进行 “引战、对立、负面” 检测。

智能打分：根据内容质量打分（0-100），低于阈值的内容自动过滤，不进入 RSS。

私有化 RSS 中心：生成标准的 RSS 2.0 订阅源，可接入 Feedly、Reeder 等任意阅读器。

现代化 GUI：基于 NiceGUI 的原生级桌面体验，无需敲命令行即可管理所有任务。

🧩 技术架构 (Modular Monolith)

本项目并未采用传统的 requests + tkinter 方案，而是采用了更适应 2025 年反爬环境的现代技术栈：

模块

技术选型

核心优势

GUI 界面

NiceGUI (FastAPI)

现代化 Material Design 风格，浏览器/桌面双模式，开发效率极高。

爬虫内核

DrissionPage

融合了 Requests 的速度与 Selenium 的抗指纹能力，能通过滑块验证与特征检测。

AI 引擎

DeepSeek API

高性价比的 Token 成本，优秀的中文语义理解与 JSON 结构化输出能力。

数据持久化

SQLModel (SQLite)

类型安全的 ORM，单文件数据库，易于迁移与备份。

任务调度

APScheduler

稳定强大的后台定时任务管理，支持多线程并发抓取。

🛠️ 功能实现进度 (Roadmap)

✅ 已实现功能

[x] 核心架构：NiceGUI 界面框架、SQLModel 数据库设计、任务调度器。

[x] 基础爬虫：

[x] 小红书 (基础图文抓取)

[x] 哔哩哔哩 (基础视频信息抓取)

[x] AI 分析：接入 DeepSeek 进行摘要生成、情感分析(Pos/Neg)、关键词提取。

[x] RSS 生成：支持生成标准 RSS XML 链接。

[x] 反爬对抗：

[x] DrissionPage 浏览器指纹伪装。

[x] Cookie 持久化与复用。

🚧 开发中 / 待实现 (TODO)

[ ] 平台扩展：

[ ] 小黑盒 爬虫策略实现。

[ ] 酷安 (CoolAPK) 爬虫策略实现。

[ ] 内容深度处理：

[ ] B站字幕提取：通过监听数据包获取 CC 字幕并合并文本。

[ ] 高级 AI 逻辑：

[ ] 评分系统：让 AI 输出 0-100 分值。

[ ] 风控过滤：识别“引战/挂人”内容并在 RSS 生成阶段过滤。

[ ] 验证码攻防：

[ ] 集成 OpenCV 实现真实的滑块缺口识别（目前为模拟逻辑）。

[ ] 完善动态代理池支持。

💻 快速开始

1. 环境准备

需要 Python 3.10 或更高版本。

# 克隆项目
git clone [https://github.com/your-repo/Smart-Scraper-RSS.git](https://github.com/your-repo/Smart-Scraper-RSS.git)
cd Smart-Scraper-RSS

# 安装依赖
pip install -r requirements.txt


2. 配置 AI

本项目强依赖 AI 能力，请设置 DeepSeek API Key (或兼容 OpenAI 格式的其他 Key)。

# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-your-api-key"

# Linux/Mac
export DEEPSEEK_API_KEY="sk-your-api-key"


3. 启动应用

python -m app.main


启动后会自动打开系统默认浏览器访问控制台。

📂 目录结构

Smart-Scraper-RSS/
├── app/
│   ├── ai/              # AI 客户端与 Prompt 模板 (需修改此处增加评分逻辑)
│   ├── core/            # 调度器与任务队列
│   ├── database/        # SQLModel 模型定义
│   ├── rss/             # RSS 生成逻辑 (需修改此处增加过滤逻辑)
│   ├── scraper/         # 核心爬虫引擎
│   │   ├── strategies/  # 平台策略 (在此添加 Xiaoheihe/Coolapk)
│   │   └── utils/       # 验证码与 Cookie 工具
│   └── ui/              # NiceGUI 界面代码
└── data/                # 存储数据库与浏览器配置


🤝 贡献指南

如果你想添加新的平台支持（如知乎、微博）：

在 app/scraper/strategies/ 下创建一个新文件（如 zhihu.py）。

继承 BaseScraper 类并实现 scrape 方法。

在界面中注册新的 Source 类型即可。

🎯 Smart-Scraper-RSS (AI Enhanced Edition)

Next-Gen Intelligent Content Aggregation System

A modern desktop application based on Windows/Linux, supporting content scraping from Bilibili, Xiaohongshu, Xiaoheihe, CoolAPK, utilizing DeepSeek AI for deep analysis, scoring, and cleaning, to generate high-quality RSS feeds.

🚀 Core Goals

This project aims to solve the problem of information overload and "spam content" through a localized intelligent agent:

Multi-Source Collection: Automated scraping of Bilibili videos, Xiaohongshu notes, Xiaoheihe game news, and CoolAPK app reviews.

Deep Content Processing:

Bilibili Enhancement: Automatically extract video CC subtitles and merge them with titles and descriptions, allowing you to understand core content without watching the video.

De-noising: Automatically remove ads and promotional soft articles.

AI Value Evaluation:

Call DeepSeek/ChatGPT models to detect "provocative, polarizing, negative" content.

Smart Scoring: Score content based on quality (0-100); content below the threshold is automatically filtered out of the RSS.

Private RSS Hub: Generate standard RSS 2.0 feeds compatible with any reader like Feedly or Reeder.

Modern GUI: Native-grade desktop experience based on NiceGUI, managing tasks without command-line operations.

🧩 Technical Architecture (Modular Monolith)

Instead of the traditional requests + tkinter approach, this project adopts a modern tech stack better suited for the 2025 anti-scraping environment:

Module

Technology

Core Advantage

GUI

NiceGUI (FastAPI)

Modern Material Design style, browser/desktop dual mode, high development efficiency.

Scraper Kernel

DrissionPage

Combines the speed of Requests with the anti-fingerprinting capability of Selenium; passes slider captchas and feature detection.

AI Engine

DeepSeek API

Cost-effective token usage, excellent Chinese semantic understanding, and JSON structured output capabilities.

Persistence

SQLModel (SQLite)

Type-safe ORM, single-file database, easy to migrate and back up.

Scheduler

APScheduler

Stable and robust background task management supporting multi-threaded concurrent scraping.

🛠️ Roadmap

✅ Implemented

[x] Core Architecture: NiceGUI framework, SQLModel database design, Task scheduler.

[x] Basic Scrapers:

[x] Xiaohongshu (Basic text/image scraping)

[x] Bilibili (Basic video info scraping)

[x] AI Analysis: DeepSeek integration for summary generation, sentiment analysis (Pos/Neg), keyword extraction.

[x] RSS Generation: Support for generating standard RSS XML links.

[x] Anti-Scraping:

[x] DrissionPage browser fingerprint masking.

[x] Cookie persistence and reuse.

🚧 In Development / TODO

[ ] Platform Expansion:

[ ] Xiaoheihe scraping strategy.

[ ] CoolAPK scraping strategy.

[ ] Deep Content Processing:

[ ] Bilibili Subtitle Extraction: Listen to data packets to acquire CC subtitles and merge text.

[ ] Advanced AI Logic:

[ ] Scoring System: Let AI output a 0-100 score.

[ ] Risk Filtering: Identify "provocative/doxing" content and filter it during RSS generation.

[ ] Captcha Defense:

[ ] Integrate OpenCV for real slider gap recognition (currently simulated).

[ ] Perfect dynamic proxy pool support.

💻 Quick Start

1. Prerequisites

Python 3.10 or higher is required.

# Clone project
git clone [https://github.com/your-repo/Smart-Scraper-RSS.git](https://github.com/your-repo/Smart-Scraper-RSS.git)
cd Smart-Scraper-RSS

# Install dependencies
pip install -r requirements.txt


2. Configure AI

This project relies heavily on AI capabilities. Please set the DeepSeek API Key (or other OpenAI-compatible keys).

# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-your-api-key"

# Linux/Mac
export DEEPSEEK_API_KEY="sk-your-api-key"


3. Start Application

python -m app.main


The application will automatically open the default system browser to access the dashboard.

📂 Directory Structure

Smart-Scraper-RSS/
├── app/
│   ├── ai/              # AI client and Prompt templates (Modify here to add scoring logic)
│   ├── core/            # Scheduler and task queue
│   ├── database/        # SQLModel definitions
│   ├── rss/             # RSS generation logic (Modify here to add filtering logic)
│   ├── scraper/         # Core scraper engine
│   │   ├── strategies/  # Platform strategies (Add Xiaoheihe/Coolapk here)
│   │   └── utils/       # Captcha and Cookie utilities
│   └── ui/              # NiceGUI interface code
└── data/                # Database and browser configuration storage


🤝 Contribution Guide

If you want to add support for a new platform (e.g., Zhihu, Weibo):

Create a new file in app/scraper/strategies/ (e.g., zhihu.py).

Inherit from the BaseScraper class and implement the scrape method.

Register the new Source type in the interface.

© 2025 Smart Scraper RSS