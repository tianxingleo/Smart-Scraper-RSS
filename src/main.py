"""
RSS内容聚合器 - 主程序入口

本程序是一个基于AI的内容聚合系统，支持：
1. 多平台内容爬取（B站、小红书、小黑盒、酷安）
2. 内容价值分析（使用DeepSeek AI）
3. 自动分类打标
4. RSS源生成
"""

import sys
import logging
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

logger = logging.getLogger('main')

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
        logger.info("成功加载qdarkstyle暗色主题")
    except ImportError:
        logger.warning("未找到qdarkstyle，将使用默认样式")

    window = MainWindow()
    logger.info("主窗口已创建")
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main() 