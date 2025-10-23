"""
图形界面模块

本模块提供了RSS内容聚合器的图形界面实现，包括：
1. 主窗口（MainWindow）：程序的主界面
2. 应用程序入口（run_app）：启动图形界面
"""

from .app import run_app
from .main_window import MainWindow

__all__ = ['run_app', 'MainWindow'] 