import sys
from PyQt5.QtWidgets import QApplication
import logging
from ui.main_window import MainWindow
from dotenv import load_dotenv
import asyncio
from qasync import QEventLoop
import atexit
import bilibili_api.utils.network as bili_network

def setup_logging():
    """配置日志记录，同时输出到控制台和文件。"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

def main():
    setup_logging()
    load_dotenv()

    # 移除bilibili_api的atexit清理钩子，避免退出时事件循环关闭异常
    try:
        atexit.unregister(bili_network.__clean)
    except Exception:
        pass

    app = QApplication(sys.argv)
    
    # 创建事件循环
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 运行事件循环
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    main() 