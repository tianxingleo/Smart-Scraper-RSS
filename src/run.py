"""
RSS内容聚合器启动脚本

本项目是一个基于AI的内容聚合系统，主要功能包括：
1. 多平台内容爬取（B站、小红书、小黑盒、酷安）
2. 内容价值分析（使用DeepSeek AI）
3. 自动分类打标
4. RSS源生成

使用方法：
1. 安装依赖：pip install -r requirements.txt
2. 运行程序：python src/run.py
3. 在配置面板中设置各平台API
4. 开始监控内容

作者：[您的名字]
版本：1.0.0
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.app import run_app

if __name__ == "__main__":
    run_app() 