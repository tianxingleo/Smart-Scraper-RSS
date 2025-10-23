import logging
import sys
import os
import time
import asyncio
from queue import Queue

# 添加src目录到Python路径
src_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
print("Adding to sys.path:", src_path)
sys.path.insert(0, src_path)

import utils.persistence
print("Using persistence module from:", utils.persistence.__file__)
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QLineEdit, QSplitter, QGroupBox, QSpinBox, QDialog, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from dotenv import load_dotenv, set_key
from qasync import QEventLoop, asyncSlot

from analysis.content_analyzer import ContentAnalyzer
from scrapers import bilibili
# 动态代理persistence模块中的函数
def load_processed_bvids():
    return utils.persistence.load_processed_bvids()

def add_processed_bvid(bvid):
    return utils.persistence.add_processed_bvid(bvid)

def clear_processed_bvids():
    return utils.persistence.clear_processed_bvids()
from feed_generation.feed_generator import generate_rss
from typing import Dict, Any

logger = logging.getLogger(__name__)

# --- Helper Classes (Workers, Dialogs) ---

class LoginDialog(QDialog):
    """登录对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('B站登录')
        self.setFixedSize(300, 400)
        
        layout = QVBoxLayout()
        
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(280, 280)
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_label = QLabel('等待扫码...')
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.qr_label)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def show_qr(self, qr_data):
        """显示二维码
        
        Args:
            qr_data (dict): 包含二维码信息的字典，应包含'qrcode'键表示图片URL
        """
        if not qr_data or 'qrcode' not in qr_data:
            self.status_label.setText('无效的二维码数据')
            return
            
        try:
            # 从URL加载二维码图片
            import requests
            from PyQt5.QtGui import QPixmap, QImage
            from PyQt5.QtCore import Qt
            import io
            
            response = requests.get(qr_data['qrcode'])
            response.raise_for_status()
            
            image = QImage.fromData(io.BytesIO(response.content).read())
            pixmap = QPixmap.fromImage(image)
            self.qr_label.setPixmap(pixmap.scaled(
                280, 280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            self.status_label.setText('请使用B站App扫码登录')
            
        except Exception as e:
            logger.error(f"加载二维码失败: {str(e)}")
            self.status_label.setText('无法加载二维码')
    
    def set_status(self, status):
        """设置状态文本
        
        Args:
            status (str): 状态文本
        """
        self.status_label.setText(status)

class ScraperThread(QThread):
    """爬虫登录线程 (qasync-compatible)"""
    finished = pyqtSignal(bool)
    qr_ready = pyqtSignal(str)
    log_message = pyqtSignal(str, str)

    def __init__(self, scraper: bilibili.BilibiliScraper):
        super().__init__()
        self.scraper = scraper
        
    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            def qr_callback(qr_path, qr_data):
                self.qr_ready.emit(qr_path)
                self.log_message.emit(f"二维码已生成: {qr_path}", "info")
            
            success = loop.run_until_complete(self.scraper.login(qr_callback))
            self.log_message.emit(f"登录任务完成, 结果: {success}", "success" if success else "error")
            self.finished.emit(success)
        except Exception as e:
            self.log_message.emit(f"登录任务异常: {e}", "error")
            self.finished.emit(False)
        finally:
            loop.close()

class AnalysisWorker(QThread):
    """Worker to analyze videos in a background thread."""
    new_log_message = pyqtSignal(str)
    analysis_complete = pyqtSignal(dict)
    finished = pyqtSignal()

    def __init__(self, video_queue, api_key, parent=None):
        super().__init__(parent)
        self.video_queue = video_queue
        self.api_key = api_key
        self._is_running = True

    def run(self):
        while self._is_running and not self.video_queue.empty():
            video = self.video_queue.get()
            bvid = video.get('bvid', 'N/A')
            self.new_log_message.emit(f"开始分析: {video.get('title', '')} (BVID: {bvid})")
            
            full_content = f"标题: {video.get('title', '')}\n简介: {video.get('desc', '')}\n字幕: {video.get('subtitle', '无')}"

            try:
                # 使用ContentAnalyzer分析视频
                analysis_result = self.analyze_video(video)
                if analysis_result and analysis_result.get('deepseek_analysis'):
                    analysis_data = analysis_result['deepseek_analysis']
                    analysis_data['bvid'] = bvid
                    analysis_data['title'] = video.get('title', '')
                    analysis_data['url'] = video.get('short_link_v2', video.get('url', ''))
                    self.analysis_complete.emit(analysis_data)
                else:
                    self.new_log_message.emit(f"视频 {bvid} 分析无结果。")
            except Exception as e:
                self.new_log_message.emit(f"分析视频 {bvid} 时出错: {e}")
            
            self.video_queue.task_done()
        
        self.new_log_message.emit("本轮视频分析完成。")
        self.finished.emit()

    def stop(self):
        self._is_running = False
        
    def analyze_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """分析视频内容"""
        # 确保必要的字段存在
        title = video.get('title', '')
        desc = video.get('desc', '')
        subtitle = video.get('subtitle', '')
        
        # 分析内容
        analysis = self.content_analyzer.analyze_content(title, desc, subtitle)
        
        # 添加分析结果
        video['deepseek_analysis'] = analysis
        
        # 添加2秒延迟，避免API请求过快
        time.sleep(2)
        
        return video

# --- Main Application Window ---

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B站内容分析工具")
        self.setGeometry(100, 100, 800, 600)
        
        # 初始化组件
        self.init_ui()
        
        # 初始化变量
        self.credential = None
        self.loop = asyncio.new_event_loop()
        self.video_queue = Queue()
        self.processed_bvid_set = load_processed_bvids()
        self.analysis_worker = None
        self.high_value_items = []
        self.scraper = bilibili.BilibiliScraper()
        
        # 初始化内容分析器
        self.content_analyzer = ContentAnalyzer()
        
        # 加载已处理的视频ID
        self.processed_bvid_set = load_processed_bvids()
        
        # 尝试自动登录
        self.log_message("正在尝试自动登录...")
        self.log_message(f"scraper对象类型: {type(self.scraper)}")
        self.log_message(f"可用属性: {dir(self.scraper)}")
        
        # 检查登录状态
        try:
            if self.scraper.is_logged_in():
                self.log_message("成功加载已保存的登录状态")
                self.update_login_ui()
            else:
                self.log_message("未找到有效的登录状态，请手动登录")
                self.update_login_ui()
        except Exception as e:
            logger.error(f"检查登录状态失败: {str(e)}")
            self.log_message("登录状态检查失败")
            self.update_login_ui()

    def init_ui(self):
        # Main layout
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Settings Group
        settings_group = QGroupBox("设置")
        settings_layout = QVBoxLayout()
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("DeepSeek API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.save_api_key_button = QPushButton("保存")
        api_key_layout.addWidget(api_key_label)
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.save_api_key_button)
        settings_layout.addLayout(api_key_layout)
        score_layout = QHBoxLayout()
        score_label = QLabel("内容价值评分阈值:")
        self.score_threshold_input = QSpinBox()
        self.score_threshold_input.setRange(0, 10)
        self.score_threshold_input.setValue(7)
        score_layout.addWidget(score_label)
        score_layout.addWidget(self.score_threshold_input)
        settings_layout.addLayout(score_layout)
        settings_group.setLayout(settings_layout)
        
        # Control Group
        control_group = QGroupBox("控制")
        control_layout = QVBoxLayout()
        self.start_button = QPushButton("开始分析")
        self.stop_button = QPushButton("停止分析")
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_group.setLayout(control_layout)

        # User Group
        user_group = QGroupBox("用户")
        user_layout = QVBoxLayout()
        self.status_label = QLabel("状态: 未登录")
        self.login_button = QPushButton("登录B站")
        self.logout_button = QPushButton("退出登录")
        self.clear_history_button = QPushButton("清空历史记录")
        user_layout.addWidget(self.status_label)
        user_layout.addWidget(self.login_button)
        user_layout.addWidget(self.logout_button)
        user_layout.addWidget(self.clear_history_button)
        user_group.setLayout(user_layout)

        left_layout.addWidget(settings_group)
        left_layout.addWidget(control_group)
        left_layout.addWidget(user_group)
        left_layout.addStretch(1)

        # Right Panel (Logs)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        log_label = QLabel("运行日志:")
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        right_layout.addWidget(log_label)
        right_layout.addWidget(self.log_display)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)

        self.setCentralWidget(main_splitter)

        # Connect signals
        self.save_api_key_button.clicked.connect(self.save_api_key)
        self.start_button.clicked.connect(self.start_analysis)
        self.stop_button.clicked.connect(self.stop_analysis)
        self.login_button.clicked.connect(self.start_login)
        self.logout_button.clicked.connect(self.logout)
        self.clear_history_button.clicked.connect(self.clear_history)
        
        self.fetch_timer = QTimer(self)
        self.fetch_timer.timeout.connect(lambda: asyncio.ensure_future(self.fetch_new_videos()))

    # --- Core Logic Methods ---

    def start_analysis(self):
        self.log_message("启动分析流程...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.fetch_timer.start(10 * 60 * 1000) # Fetch every 10 minutes
        asyncio.ensure_future(self.fetch_new_videos())

    def stop_analysis(self):
        self.log_message("停止分析流程...")
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.stop()
        self.fetch_timer.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    @asyncSlot()
    async def fetch_new_videos(self):
        self.log_message("正在获取最新视频...")
        try:
            if self.credential:
                videos = await bilibili.get_personal_recommendations(self.credential)
                self.log_message(f"已获取 {len(videos)} 条个性化推荐视频。")
            else:
                videos = bilibili.get_popular_videos()
                self.log_message(f"未登录，已获取 {len(videos)} 条热门视频。")

            new_videos_count = 0
            for video in videos:
                if video.get('bvid', '') not in self.processed_bvid_set:
                    self.video_queue.put(video)
                    self.processed_bvid_set.add(video.get('bvid', ''))
                    add_processed_bvid(video.get('bvid', ''))
                    new_videos_count += 1
            
            self.log_message(f"发现 {new_videos_count} 条新视频，已加入分析队列。")

            if not self.analysis_worker or not self.analysis_worker.isRunning():
                api_key = os.getenv("DEEPSEEK_API_KEY")
                if not api_key:
                    self.log_message("[错误] DEEPSEEK_API_KEY 未设置。")
                    self.stop_analysis()
                    return
                
                self.analysis_worker = AnalysisWorker(self.video_queue, api_key)
                self.analysis_worker.new_log_message.connect(self.log_message)
                self.analysis_worker.analysis_complete.connect(self.handle_analysis_result)
                self.analysis_worker.finished.connect(self.on_analysis_worker_finished)
                self.analysis_worker.start()

        except Exception as e:
            self.log_message(f"获取视频失败: {e}")

    def handle_analysis_result(self, result):
        score = result.get('score', 0)
        self.log_message(f"视频 '{result['title'][:20]}...' 分析完成, 得分: {score}")
        if score >= self.score_threshold_input.value() and not result.get('is_negative', False):
            self.high_value_items.append(result)
            self.log_message(f"高价值内容: '{result['title'][:20]}...' 已加入RSS列表。")
            generate_rss(self.high_value_items)

    def on_analysis_worker_finished(self):
        self.log_message("分析线程已结束。")
        self.analysis_worker = None
        if self.start_button.isEnabled() == False: # Only re-enable if it was running
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    # --- UI and Helper Methods ---

    def log_message(self, message):
        logging.info(message)
        self.log_display.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def save_api_key(self):
        api_key = self.api_key_input.text()
        if api_key:
            env_path = ".env"
            set_key(env_path, "DEEPSEEK_API_KEY", api_key)
            self.log_message(f"API密钥已保存到: {env_path}")
            os.environ["DEEPSEEK_API_KEY"] = api_key
        else:
            self.log_message("警告: API密钥不能为空。")

    def load_api_key(self):
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key:
            self.api_key_input.setText(api_key)
            self.log_message("已从 .env 文件加载API密钥。")
            self.start_button.setEnabled(True)
        else:
            self.log_message("请在设置中输入DeepSeek API Key并保存。")

    def try_auto_login(self):
        self.log_message("正在尝试自动登录...")
        self.credential = bilibili.get_credential()
        self.update_login_ui()

    def update_login_ui(self):
        if self.credential:
            self.status_label.setText(f"状态: 已登录 (UID: {self.credential.dedeuserid})")
            self.login_button.setEnabled(False)
            self.logout_button.setEnabled(True)
        else:
            self.status_label.setText("状态: 未登录")
            self.credential = None
            self.login_button.setEnabled(True)
            self.logout_button.setEnabled(False)
        self.log_message(self.status_label.text())

    def start_login(self):
        """开始登录"""
        self.append_log("请求开始登录...", "info")
        try:
            self.login_button.setEnabled(False)
            self.status_label.setText('正在加载二维码...')
            
            self.login_dialog = LoginDialog(self)
            self.login_dialog.show()
            
            # 启动异步登录任务
            asyncio.ensure_future(self.login_with_qrcode_task())
            
        except Exception as e:
            logger.error(f"登录启动失败: {str(e)}")
            self.status_label.setText('状态: 未登录')
            self.login_button.setEnabled(True)
            self.append_log(f"登录启动失败: {str(e)}", "error")

    async def login_with_qrcode_task(self):
        """异步登录任务，生成二维码并等待登录成功"""
        try:
            # 生成二维码
            qr_data = await self.scraper.login_with_qrcode()
            
            if qr_data:
                # 将二维码数据传递给对话框
                self.login_dialog.show_qr(qr_data)
                self.append_log("二维码已生成，请扫码登录", "info")
                
                # 等待登录完成
                while not self.scraper.is_logged_in():
                    await asyncio.sleep(1)
                
                self.on_login_finished(True)
            else:
                self.on_login_finished(False)
                self.append_log("二维码生成失败", "error")
                
        except Exception as e:
            logger.error(f"登录任务异常: {str(e)}")
            self.on_login_finished(False)

    def on_login_finished(self, success):
        """登录完成回调
        
        Args:
            success (bool): 是否登录成功
        """
        self.login_button.setEnabled(True)
        if success:
            # 登录成功后重新加载本地凭据
            self.credential = bilibili.get_credential()
            self.status_label.setText('已登录')
            self.login_dialog.close()
            self.append_log("登录成功", "success")
            self.update_login_ui()
        else:
            self.status_label.setText('登录失败')
            self.append_log("登录失败", "error")
            self.update_login_ui()
    
    def logout(self):
        bilibili.logout()
        self.credential = None
        self.update_login_ui()
    
    def clear_history(self):
        clear_processed_bvids()
        self.processed_bvid_set.clear()
        self.log_message("已清空处理历史记录。")

    def append_log(self, message, level="info"):
        """添加日志
        
        Args:
            message (str): 日志消息
            level (str): 日志级别
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        self.log_display.append(log_message)
        
        if level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.info(message)

    def closeEvent(self, event):
        self.stop_analysis()
        if self.analysis_worker:
            self.analysis_worker.wait() # Wait for thread to finish
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        sys.exit(loop.run_forever()) 