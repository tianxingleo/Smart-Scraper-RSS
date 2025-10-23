"""
应用程序入口模块

提供了启动图形界面的入口函数。
"""

import sys
from PyQt6.QtWidgets import QApplication
from .main_window import MainWindow

def run_app():
    """启动图形界面应用程序"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 