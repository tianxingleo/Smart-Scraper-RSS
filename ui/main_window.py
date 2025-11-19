import logging
import sys
import os
import time
import asyncio
from queue import Queue
from typing import Dict, Any

# Add src to path
src_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
sys.path.insert(0, src_path)

import utils.persistence
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QTextEdit, QLabel, 
                             QLineEdit, QSplitter, QGroupBox, QSpinBox, QDialog, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from dotenv import load_dotenv, set_key
from qasync import QEventLoop, asyncSlot

from analysis.content_analyzer import ContentAnalyzer
from scrapers import bilibili
from feed_generation.feed_generator import generate_rss

# Dynamic proxy for persistence
def load_processed_bvids():
    return utils.persistence.load_processed_bvids()

def add_processed_bvid(bvid):
    return utils.persistence.add_processed_bvid(bvid)

def clear_processed_bvids():
    return utils.persistence.clear_processed_bvids()

logger = logging.getLogger(__name__)

class LoginDialog(QDialog):
    """Login Dialog"""
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
        if not qr_data or 'qrcode' not in qr_data:
            self.status_label.setText('无效的二维码数据')
            return
        try:
            import requests
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

class AnalysisWorker(QThread):
    new_log_message = pyqtSignal(str)
    analysis_complete = pyqtSignal(dict)
    
    def __init__(self, video_queue, api_key):
        super().__init__()
        self.video_queue = video_queue
        self.api_key = api_key
        self.content_analyzer = ContentAnalyzer(api_key)
        self._is_running = True

    def run(self):
        while self._is_running and not self.video_queue.empty():
            try:
                video = self.video_queue.get()
                self.analyze_video(video)
                self.video_queue.task_done()
            except Exception as e:
                self.new_log_message.emit(f"Worker error: {e}")
        # self.finished.emit() is emitted automatically by QThread when run() returns

    def stop(self):
        self._is_running = False

    def analyze_video(self, video: Dict[str, Any]):
        title = video.get('title', '')
        desc = video.get('desc', '')
        subtitle = video.get('subtitle', '') # Subtitle should be fetched before adding to queue or here?
        # Actually, subtitle fetching is async in scraper. 
        # We should probably fetch subtitle BEFORE adding to queue, or make this worker async?
        # QThread is sync. 
        # If subtitle is missing, we might need to fetch it here, but we can't easily call async scraper methods from sync thread.
        # So, we assume subtitle is already in video object.
        
        self.new_log_message.emit(f"正在分析: {title[:20]}...")
        analysis = self.content_analyzer.analyze_content(title, desc, subtitle)
        
        video['deepseek_analysis'] = analysis
        video['score'] = analysis.get('score', 0) if analysis else 0
        video['tags'] = analysis.get('tags', []) if analysis else []
        video['analysis'] = analysis.get('analysis', '') if analysis else ''
        video['is_negative'] = analysis.get('is_negative', False) if analysis else False
        
        self.analysis_complete.emit(video)
        time.sleep(1) # Rate limit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B站内容分析工具")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        
        self.credential = None
        self.loop = asyncio.new_event_loop()
        self.video_queue = Queue()
        self.processed_bvid_set = load_processed_bvids()
        self.analysis_worker = None
        self.high_value_items = []
        self.scraper = bilibili.BilibiliScraper()
        self.content_analyzer = ContentAnalyzer()
        
        self.log_message("正在初始化...")
        self.try_auto_login()

    def init_ui(self):
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Settings
        settings_group = QGroupBox("设置")
        settings_layout = QVBoxLayout()
        api_key_layout = QHBoxLayout()
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.save_api_key_button = QPushButton("保存")
        api_key_layout.addWidget(QLabel("DeepSeek API Key:"))
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.save_api_key_button)
        settings_layout.addLayout(api_key_layout)
        
        score_layout = QHBoxLayout()
        self.score_threshold_input = QSpinBox()
        self.score_threshold_input.setRange(0, 10)
        self.score_threshold_input.setValue(7)
        score_layout.addWidget(QLabel("评分阈值:"))
        score_layout.addWidget(self.score_threshold_input)
        settings_layout.addLayout(score_layout)
        settings_group.setLayout(settings_layout)
        
        # Control
        control_group = QGroupBox("控制")
        control_layout = QVBoxLayout()
        self.start_button = QPushButton("开始分析")
        self.stop_button = QPushButton("停止分析")
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_group.setLayout(control_layout)
        
        # User
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
        
        # Right Panel
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        right_layout.addWidget(QLabel("运行日志:"))
        right_layout.addWidget(self.log_display)
        
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        self.setCentralWidget(main_splitter)
        
        # Signals
        self.save_api_key_button.clicked.connect(self.save_api_key)
        self.start_button.clicked.connect(self.start_analysis)
        self.stop_button.clicked.connect(self.stop_analysis)
        self.login_button.clicked.connect(self.start_login)
        self.logout_button.clicked.connect(self.logout)
        self.clear_history_button.clicked.connect(self.clear_history)
        
        self.fetch_timer = QTimer(self)
        self.fetch_timer.timeout.connect(lambda: asyncio.ensure_future(self.fetch_new_videos()))
        
        self.load_api_key()

    def log_message(self, message):
        logging.info(message)
        self.log_display.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def save_api_key(self):
        api_key = self.api_key_input.text()
        if api_key:
            env_path = ".env"
            if not os.path.exists(env_path):
                with open(env_path, 'w') as f: f.write("")
            set_key(env_path, "DEEPSEEK_API_KEY", api_key)
            self.log_message(f"API密钥已保存到: {os.path.abspath(env_path)}")
            os.environ["DEEPSEEK_API_KEY"] = api_key
        else:
            self.log_message("警告: API密钥不能为空。")

    def load_api_key(self):
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if api_key:
            self.api_key_input.setText(api_key)
            self.log_message("已从 .env 文件加载API密钥。")
        else:
            self.log_message("请在设置中输入DeepSeek API Key并保存。")

    def try_auto_login(self):
        self.log_message("正在尝试自动登录...")
        self.credential = self.scraper.credential
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

    def start_login(self):
        self.login_button.setEnabled(False)
        self.login_dialog = LoginDialog(self)
        self.login_dialog.show()
        asyncio.ensure_future(self.login_with_qrcode_task())

    async def login_with_qrcode_task(self):
        try:
            qr_data = await self.scraper.get_login_qr_code()
            if qr_data:
                self.login_dialog.show_qr(qr_data)
                self.log_message("二维码已生成，请扫码登录")
                while True:
                    if await self.scraper.poll_login_status(qr_data['key']):
                        break
                    if self.scraper.is_logged_in():
                        break
                    if not self.login_dialog.isVisible():
                        return
                    await asyncio.sleep(2)
                self.on_login_finished(True)
            else:
                self.on_login_finished(False)
                self.log_message("二维码生成失败")
        except Exception as e:
            logger.error(f"登录任务异常: {str(e)}")
            self.on_login_finished(False)

    def on_login_finished(self, success):
        self.login_button.setEnabled(True)
        if success:
            self.credential = self.scraper.credential
            self.login_dialog.close()
            self.log_message("登录成功")
            self.update_login_ui()
        else:
            self.log_message("登录失败")
            self.update_login_ui()

    def logout(self):
        # bilibili.logout() # Removed in scraper refactor, need to handle here or add back?
        # The scraper refactor removed the global logout function.
        # We should clear credential file manually or add a method to scraper.
        # For now, just clear memory credential.
        self.credential = None
        self.scraper.credential = None
        # Also remove file if needed?
        if os.path.exists(self.scraper.CREDENTIAL_FILE):
            os.remove(self.scraper.CREDENTIAL_FILE)
        self.update_login_ui()

    def clear_history(self):
        clear_processed_bvids()
        self.processed_bvid_set.clear()
        self.log_message("已清空处理历史记录。")

    def start_analysis(self):
        self.log_message("启动分析流程...")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.fetch_timer.start(10 * 60 * 1000)
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
                videos = await self.scraper.get_personal_recommendations()
                self.log_message(f"已获取 {len(videos)} 条个性化推荐视频。")
            else:
                videos = await self.scraper.get_popular_videos()
                self.log_message(f"已获取 {len(videos)} 条热门视频。")
            
            if not videos:
                self.log_message("未获取到视频。")
                return

            api_key = self.api_key_input.text()
            if not api_key:
                self.log_message("[错误] DEEPSEEK_API_KEY 未设置。")
                self.stop_analysis()
                return

            count = 0
            for video in videos:
                bvid = video.get('bvid')
                if bvid and bvid not in self.processed_bvid_set:
                    # Fetch subtitle here? 
                    # It's async, so we should do it here before passing to sync worker.
                    subtitle = await self.scraper.get_video_subtitle(bvid)
                    video['subtitle'] = subtitle
                    
                    self.video_queue.put(video)
                    self.processed_bvid_set.add(bvid)
                    add_processed_bvid(video) # Persist immediately
                    count += 1
            
            self.log_message(f"添加了 {count} 个新视频到分析队列。")

            if not self.analysis_worker or not self.analysis_worker.isRunning():
                self.analysis_worker = AnalysisWorker(self.video_queue, api_key)
                self.analysis_worker.new_log_message.connect(self.log_message)
                self.analysis_worker.analysis_complete.connect(self.handle_analysis_result)
                self.analysis_worker.finished.connect(self.on_analysis_worker_finished)
                self.analysis_worker.start()

        except Exception as e:
            self.log_message(f"获取视频失败: {e}")

    def handle_analysis_result(self, result):
        score = result.get('score', 0)
        self.log_message(f"视频 '{result.get('title', '')[:20]}...' 分析完成, 得分: {score}")
        if score >= self.score_threshold_input.value() and not result.get('is_negative', False):
            self.high_value_items.append(result)
            self.log_message(f"高价值内容: '{result.get('title', '')[:20]}...' 已加入RSS列表。")
            generate_rss(self.high_value_items)
            # Update persistence with analysis result
            utils.persistence.add_analysis_result(result)

    def on_analysis_worker_finished(self):
        self.log_message("分析线程已结束。")
        # Don't set self.analysis_worker to None if we want to keep it? 
        # Usually we create new one.
        self.analysis_worker = None
        # If stopped manually, buttons are handled in stop_analysis.
        # If finished naturally (queue empty), we keep running state (timer is still on).

    def closeEvent(self, event):
        self.stop_analysis()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = MainWindow()
    window.show()
    with loop:
        sys.exit(loop.run_forever())