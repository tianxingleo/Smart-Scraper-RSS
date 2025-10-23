"""
RSS内容聚合器 - 主窗口模块

本项目是一个基于AI的内容聚合系统，主要功能包括：
1. 多平台内容爬取（B站、小红书、小黑盒、酷安）
2. 内容价值分析（使用DeepSeek AI）
3. 自动分类打标
4. RSS源生成

作者：[您的名字]
版本：1.0.0
"""

import sys
import os
import asyncio
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QLineEdit,
    QFormLayout, QCheckBox, QStatusBar, QScrollArea, QFrame,
    QSpinBox, QComboBox, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
import webbrowser
import json
from scrapers.bilibili import BilibiliScraper
from analysis.content_analyzer import ContentAnalyzer
import time

logger = logging.getLogger(__name__)

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
    
    def show_qr(self, qr_path):
        """显示二维码
        
        Args:
            qr_path (str): 二维码图片路径
        """
        if os.path.exists(qr_path):
            pixmap = QPixmap(qr_path)
            self.qr_label.setPixmap(pixmap.scaled(
                280, 280,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            self.status_label.setText('请使用B站App扫码登录')
    
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

    def __init__(self, scraper: BilibiliScraper):
        super().__init__()
        self.scraper = scraper
        
    def run(self):
        try:
            def qr_callback(qr_path, qr_data):
                self.qr_ready.emit(qr_path)
                self.log_message.emit(f"二维码已生成: {qr_path}", "info")
            
            success = self.scraper.login(qr_callback)
            self.log_message.emit(f"登录任务完成, 结果: {success}", "success" if success else "error")
            self.finished.emit(success)
        except Exception as e:
            self.log_message.emit(f"登录任务异常: {e}", "error")
            self.finished.emit(False)

class MonitorThread(QThread):
    """监控线程 (qasync-compatible)"""
    video_found = pyqtSignal(dict)
    error = pyqtSignal(str)
    log_message = pyqtSignal(str, str)

    def __init__(self, scraper: BilibiliScraper, interval: int = 300):
        super().__init__()
        self.scraper = scraper
        self.interval = interval
        self._is_running = True

    def run(self):
        self.scraper.init_browser()
        while self._is_running:
            videos = self.scraper.get_recommended_videos()
            self.log_message.emit(f"本轮抓取到 {len(videos)} 个视频", "success")
            
            if not self._is_running: break
            
            for video in videos:
                self.video_found.emit(video)
            
            self.log_message.emit(f"本轮抓取完成，将休眠 {self.interval} 秒...", "info")
            for _ in range(self.interval):
                if not self._is_running: break
                time.sleep(1) # interruptible sleep
        self.scraper.close_browser()
        self.log_message.emit("监控任务结束，正在关闭浏览器...", "info")
        self.log_message.emit("浏览器已关闭，监控任务彻底结束", "success")

    def stop(self):
        self._is_running = False
        self.log_message.emit("收到停止信号，任务将在当前循环或休眠结束后退出", "warning")

class MainWindow(QMainWindow):
    """主窗口类
    
    负责创建和管理主界面，包括：
    - 配置面板（API设置、爬虫设置）
    - 内容监控面板
    - RSS预览面板
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B站内容聚合器")
        self.setMinimumSize(1200, 800)
        
        # 初始化成员变量
        self.analyzer = None
        self.scraper = None
        self.monitor_thread = None
        self.login_thread = None
        self.login_dialog = None
        self.video_data_store = []
        
        # 初始化UI
        self.init_ui()
        
        # 初始化爬虫和分析器
        self.analyzer = ContentAnalyzer()
        self.scraper = BilibiliScraper(analyzer=self.analyzer)
        
        # 检查登录状态
        self.check_login_status()
        
    def init_ui(self):
        """初始化UI"""
        # 创建中心部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建登录状态面板
        login_panel = QWidget()
        login_layout = QHBoxLayout(login_panel)
        
        # 登录状态标签
        self.status_label = QLabel('未登录')
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        login_layout.addWidget(QLabel('当前状态:'))
        login_layout.addWidget(self.status_label)
        login_layout.addSpacing(20)
        
        # 刷新登录状态按钮
        self.refresh_login_btn = QPushButton('刷新登录状态')
        self.refresh_login_btn.clicked.connect(self.check_login_status)
        login_layout.addWidget(self.refresh_login_btn)
        
        # 将登录面板添加到布局中
        layout.addWidget(login_panel)
        
        # 创建选项卡部件
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 添加选项卡
        tab_widget.addTab(self.create_monitor_tab(), "监控")
        tab_widget.addTab(self.create_settings_tab(), "设置")
        tab_widget.addTab(self.create_preview_tab(), "RSS预览")
        
        # 创建状态栏
        self.statusBar()
        
        # 加载配置
        self.load_settings()
        
        # 设置样式
        self.apply_styles()
        
    def create_settings_tab(self):
        """创建配置面板
        
        包含以下设置项：
        - AI API配置（DeepSeek）
        - 平台API配置（B站、小红书等）
        - 内容过滤设置
        - RSS生成设置
        """
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # 创建内容widget
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ===== AI API设置 =====
        ai_group = QFrame()
        ai_group.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        ai_layout = QVBoxLayout(ai_group)
        
        # DeepSeek API设置
        deepseek_layout = QFormLayout()
        self.deepseek_key = QLineEdit()
        self.deepseek_key.setPlaceholderText("输入DeepSeek API密钥")
        self.deepseek_key.textChanged.connect(self.update_deepseek_key)
        deepseek_layout.addRow("DeepSeek API密钥:", self.deepseek_key)
        
        # 添加获取API指南按钮
        deepseek_help = QPushButton("如何获取API密钥？")
        deepseek_help.clicked.connect(lambda: webbrowser.open("https://platform.deepseek.com/"))
        deepseek_layout.addRow("", deepseek_help)
        
        ai_layout.addLayout(deepseek_layout)
        layout.addWidget(QLabel("AI API设置"))
        layout.addWidget(ai_group)
        
        # ===== 平台API设置 =====
        platforms_group = QFrame()
        platforms_group.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        platforms_layout = QVBoxLayout(platforms_group)
        
        # B站设置
        bilibili_layout = QFormLayout()
        self.bilibili_enabled = QCheckBox("启用")
        bilibili_layout.addRow("B站爬虫:", self.bilibili_enabled)
        
        # B站登录按钮
        bilibili_login = QPushButton("扫码登录")
        bilibili_login.clicked.connect(self.start_login)
        bilibili_layout.addRow("", bilibili_login)
        
        platforms_layout.addLayout(bilibili_layout)
        
        # 小红书设置
        xiaohongshu_layout = QFormLayout()
        self.xiaohongshu_enabled = QCheckBox("启用")
        self.xiaohongshu_token = QLineEdit()
        self.xiaohongshu_token.setPlaceholderText("输入小红书Token")
        xiaohongshu_layout.addRow("小红书爬虫:", self.xiaohongshu_enabled)
        xiaohongshu_layout.addRow("Token:", self.xiaohongshu_token)
        xiaohongshu_help = QPushButton("如何获取Token？")
        xiaohongshu_help.clicked.connect(self.show_xiaohongshu_guide)
        xiaohongshu_layout.addRow("", xiaohongshu_help)
        platforms_layout.addLayout(xiaohongshu_layout)
        
        # 酷安设置
        coolapp_layout = QFormLayout()
        self.coolapp_enabled = QCheckBox("启用")
        self.coolapp_token = QLineEdit()
        self.coolapp_token.setPlaceholderText("输入酷安Token")
        coolapp_layout.addRow("酷安爬虫:", self.coolapp_enabled)
        coolapp_layout.addRow("Token:", self.coolapp_token)
        coolapp_help = QPushButton("如何获取Token？")
        coolapp_help.clicked.connect(self.show_coolapp_guide)
        coolapp_layout.addRow("", coolapp_help)
        platforms_layout.addLayout(coolapp_layout)
        
        # 小黑盒设置
        xiaoheihe_layout = QFormLayout()
        self.xiaoheihe_enabled = QCheckBox("启用")
        self.xiaoheihe_token = QLineEdit()
        self.xiaoheihe_token.setPlaceholderText("输入小黑盒Token")
        xiaoheihe_layout.addRow("小黑盒爬虫:", self.xiaoheihe_enabled)
        xiaoheihe_layout.addRow("Token:", self.xiaoheihe_token)
        xiaoheihe_help = QPushButton("如何获取Token？")
        xiaoheihe_help.clicked.connect(self.show_xiaoheihe_guide)
        xiaoheihe_layout.addRow("", xiaoheihe_help)
        platforms_layout.addLayout(xiaoheihe_layout)
        
        layout.addWidget(QLabel("平台设置"))
        layout.addWidget(platforms_group)
        
        # ===== 内容过滤设置 =====
        filter_group = QFrame()
        filter_group.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        filter_layout = QFormLayout(filter_group)
        
        self.min_score = QSpinBox()
        self.min_score.setRange(1, 10)
        self.min_score.setValue(7)
        filter_layout.addRow("最低评分:", self.min_score)
        
        self.categories = QTextEdit()
        self.categories.setPlaceholderText("输入分类标签，每行一个")
        self.categories.setMaximumHeight(100)
        filter_layout.addRow("分类标签:", self.categories)
        
        layout.addWidget(QLabel("内容过滤设置"))
        layout.addWidget(filter_group)
        
        # ===== RSS设置 =====
        rss_group = QFrame()
        rss_group.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        rss_layout = QFormLayout(rss_group)
        
        self.rss_title = QLineEdit("智能内容精选")
        rss_layout.addRow("RSS标题:", self.rss_title)
        
        self.rss_description = QLineEdit("AI筛选的优质内容聚合")
        rss_layout.addRow("RSS描述:", self.rss_description)
        
        layout.addWidget(QLabel("RSS设置"))
        layout.addWidget(rss_group)
        
        # 保存按钮
        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        # 设置滚动区域的widget
        scroll.setWidget(widget)
        return scroll
    
    def start_login(self):
        """开始登录"""
        self.append_log("请求开始登录...", "info")
        try:
            self.login_button.setEnabled(False)
            self.status_label.setText('正在加载二维码...')
            
            self.login_dialog = LoginDialog(self)
            self.login_dialog.show()
            
            self.login_thread = ScraperThread(self.scraper)
            self.login_thread.finished.connect(self.on_login_finished)
            self.login_thread.qr_ready.connect(self.login_dialog.show_qr)
            self.login_thread.log_message.connect(self.append_log)  # 连接日志信号
            self.login_thread.start()
            self.append_log("登录线程已启动", "info")
        except Exception as e:
            logger.error(f"启动登录失败: {str(e)}")
            self.login_button.setEnabled(True)
            self.status_label.setText('登录失败')
            QMessageBox.warning(self, '错误', f'启动登录失败: {str(e)}')
    
    def on_login_finished(self, success):
        """登录完成回调
        
        Args:
            success (bool): 是否登录成功
        """
        try:
            if success or (self.scraper and self.scraper.cookies):
                # 即使scraper.login返回False，但cookie已保存也认为成功
                self.status_label.setText('已登录')
                self.login_button.setEnabled(False)
                self.monitor_button.setEnabled(True)
                if self.login_dialog:
                    self.login_dialog.close()
                    self.login_dialog = None
                if not success:
                    QMessageBox.information(self, '提示', '检测到已保存cookie，自动视为登录成功！')
                else:
                    QMessageBox.information(self, '提示', '登录成功！')
                return
            else:
                self.status_label.setText('登录失败')
                self.login_button.setEnabled(True)
                if self.login_dialog:
                    self.login_dialog.close()
                    self.login_dialog = None
                QMessageBox.warning(self, '错误', '登录失败，请重试')
        except Exception as e:
            logger.error(f"处理登录结果失败: {str(e)}")
            self.status_label.setText('登录状态更新失败')
            self.login_button.setEnabled(True)
    
    def show_xiaohongshu_guide(self):
        """显示小红书Token获取指南"""
        guide = """
如何获取小红书Token：

1. 使用Chrome浏览器访问小红书网页版并登录
2. 按F12打开开发者工具
3. 切换到Network标签页
4. 刷新页面
5. 在请求列表中找到api/sns/v1/...开头的请求
6. 在Headers中找到x-sign字段
7. 复制该值作为Token
"""
        QMessageBox.information(self, "获取小红书Token指南", guide)
    
    def show_coolapp_guide(self):
        """显示酷安Token获取指南"""
        guide = """
如何获取酷安Token：

1. 使用Chrome浏览器访问酷安并登录
2. 按F12打开开发者工具
3. 切换到Network标签页
4. 刷新页面
5. 在请求列表中找到api.coolapk.com
6. 在Headers中找到X-App-Token字段
7. 复制该值
"""
        QMessageBox.information(self, "获取酷安Token指南", guide)
    
    def show_xiaoheihe_guide(self):
        """显示小黑盒Token获取指南"""
        guide = """
如何获取小黑盒Token：

1. 使用Chrome浏览器访问小黑盒并登录
2. 按F12打开开发者工具
3. 切换到Network标签页
4. 刷新页面
5. 在请求列表中找到api.xiaoheihe.cn
6. 在Headers中找到Authorization字段
7. 复制该值
"""
        QMessageBox.information(self, "获取小黑盒Token指南", guide)
    
    def create_monitor_tab(self):
        """创建监控选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 状态面板
        status_panel = QWidget()
        status_layout = QHBoxLayout(status_panel)
        
        # 状态标签和登录按钮
        self.status_label = QLabel('未登录')
        status_layout.addWidget(QLabel('状态:'))
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.login_button = QPushButton('扫码登录')
        self.login_button.clicked.connect(self.start_login)
        status_layout.addWidget(self.login_button)
        
        layout.addWidget(status_panel)
        
        # 控制面板
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        self.monitor_button = QPushButton("开始监控")
        self.monitor_button.clicked.connect(self.toggle_monitor)
        self.monitor_button.setEnabled(False)  # 默认禁用，登录后启用
        control_layout.addWidget(self.monitor_button)
        
        self.clear_log_button = QPushButton("清空日志")
        self.clear_log_button.clicked.connect(self.clear_log)
        control_layout.addWidget(self.clear_log_button)

        self.clear_cache_button = QPushButton("清空视频缓存")
        self.clear_cache_button.clicked.connect(self.clear_video_cache)
        control_layout.addWidget(self.clear_cache_button)
        
        control_layout.addStretch()
        layout.addWidget(control_panel)
        
        # 日志面板
        log_panel = QWidget()
        log_layout = QVBoxLayout(log_panel)
        
        # 日志过滤器
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("日志过滤:"))
        
        self.log_filter = QComboBox()
        self.log_filter.addItems(["全部", "视频信息", "AI分析", "错误"])
        self.log_filter.currentTextChanged.connect(self.filter_log)
        filter_layout.addWidget(self.log_filter)
        
        filter_layout.addStretch()
        log_layout.addLayout(filter_layout)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_panel)
        
        return widget
    
    def create_preview_tab(self):
        """创建RSS预览面板
        
        显示生成的RSS内容预览
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # RSS预览
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        layout.addWidget(self.preview_text)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新预览")
        refresh_btn.clicked.connect(self.refresh_preview)
        button_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("导出RSS")
        export_btn.clicked.connect(self.export_rss)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def apply_styles(self):
        """应用界面样式"""
        # 设置全局字体
        font = QFont("Microsoft YaHei UI", 10)
        QApplication.setFont(font)
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """
        
        # 设置输入框样式
        input_style = """
            QLineEdit, QTextEdit {
                border: 1px solid #BDBDBD;
                border-radius: 4px;
                padding: 4px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #2196F3;
            }
        """
        
        # 设置分组框样式
        frame_style = """
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 8px;
            }
        """
        
        self.setStyleSheet(button_style + input_style + frame_style)
    
    def save_settings(self):
        """保存配置到文件"""
        settings = {
            'deepseek_api_key': self.deepseek_key.text(),
            'bilibili': {
                'enabled': self.bilibili_enabled.isChecked()
            },
            'xiaohongshu': {
                'enabled': self.xiaohongshu_enabled.isChecked(),
                'token': self.xiaohongshu_token.text()
            },
            'coolapp': {
                'enabled': self.coolapp_enabled.isChecked(),
                'token': self.coolapp_token.text()
            },
            'xiaoheihe': {
                'enabled': self.xiaoheihe_enabled.isChecked(),
                'token': self.xiaoheihe_token.text()
            },
            'filter': {
                'min_score': self.min_score.value(),
                'categories': self.categories.toPlainText().split('\n')
            },
            'rss': {
                'title': self.rss_title.text(),
                'description': self.rss_description.text()
            }
        }
        
        try:
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            self.statusBar().showMessage("设置已保存", 3000)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置失败：{str(e)}")
    
    def check_login_status(self):
        """检查并更新登录状态"""
        if self.scraper and self.scraper.check_login():
            self.status_label.setText('已登录')
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.login_button.setEnabled(False)
            self.refresh_login_btn.setEnabled(True)
        else:
            self.status_label.setText('未登录')
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.login_button.setEnabled(True)
            self.refresh_login_btn.setEnabled(True)
            
        # 返回当前登录状态
        return self.scraper.check_login() if self.scraper else False

    def load_settings(self):
        """从文件加载配置"""
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                self.deepseek_key.setText(settings.get('deepseek_api_key', ''))
                
                bilibili = settings.get('bilibili', {})
                self.bilibili_enabled.setChecked(bilibili.get('enabled', False))
                
                xiaohongshu = settings.get('xiaohongshu', {})
                self.xiaohongshu_enabled.setChecked(xiaohongshu.get('enabled', False))
                self.xiaohongshu_token.setText(xiaohongshu.get('token', ''))
                
                coolapp = settings.get('coolapp', {})
                self.coolapp_enabled.setChecked(coolapp.get('enabled', False))
                self.coolapp_token.setText(coolapp.get('token', ''))
                
                xiaoheihe = settings.get('xiaoheihe', {})
                self.xiaoheihe_enabled.setChecked(xiaoheihe.get('enabled', False))
                self.xiaoheihe_token.setText(xiaoheihe.get('token', ''))
                
                filter_settings = settings.get('filter', {})
                self.min_score.setValue(filter_settings.get('min_score', 7))
                self.categories.setPlainText('\n'.join(filter_settings.get('categories', [])))
                
                rss = settings.get('rss', {})
                self.rss_title.setText(rss.get('title', '智能内容精选'))
                self.rss_description.setText(rss.get('description', 'AI筛选的优质内容聚合'))
        except Exception as e:
            QMessageBox.warning(self, "警告", f"加载设置失败：{str(e)}")
    
    def toggle_monitor(self):
        """切换监控状态"""
        if not hasattr(self, 'monitor_thread') or not self.monitor_thread or not self.monitor_thread.isRunning():
            self.start_monitor()
        else:
            self.stop_monitor()
    
    def start_monitor(self):
        """开始监控"""
        self.append_log("请求开始监控...", "info")
        try:
            logger.info("正在启动监控...")
            self.append_log("正在启动监控...", "info")
            
            # 确保之前的监控线程已经停止
            if hasattr(self, 'monitor_thread') and self.monitor_thread:
                if self.monitor_thread.isRunning():
                    self.stop_monitor()
                self.monitor_thread.deleteLater()
                self.monitor_thread = None
            
            # 创建监控线程
            self.monitor_thread = MonitorThread(self.scraper)
            self.monitor_thread.video_found.connect(self.on_video_found)
            self.monitor_thread.error.connect(self.on_monitor_error)
            self.monitor_thread.finished.connect(self.on_monitor_finished)
            self.monitor_thread.log_message.connect(self.append_log) # 连接日志信号
            
            # 启动线程
            self.monitor_thread.start()
            
            # 更新UI状态
            self.monitor_button.setText("停止监控")
            self.monitor_button.setEnabled(True)  # 确保按钮可用
            self.statusBar().showMessage("正在监控中...", 3000)
            
            self.append_log("监控线程已启动", "info")
            
        except Exception as e:
            logger.error(f"启动监控失败: {str(e)}")
            self.append_log(f"启动监控失败: {str(e)}", "error")
            self.monitor_button.setText("开始监控")
            self.monitor_button.setEnabled(True)  # 确保按钮可用
    
    def stop_monitor(self):
        """停止监控"""
        try:
            logger.info("正在请求停止监控...")
            self.append_log("正在停止监控...", "info")
            
            if hasattr(self, 'monitor_thread') and self.monitor_thread and self.monitor_thread.isRunning():
                # 禁用按钮，防止重复点击，等待线程结束后在 on_monitor_finished 中恢复
                self.monitor_button.setEnabled(False)
                self.monitor_button.setText("正在停止...")
                # 非阻塞地发送停止信号
                self.monitor_thread.stop()
            else:
                logger.warning("监控线程未运行或不存在")
                self.monitor_button.setText("开始监控")
                self.monitor_button.setEnabled(True)
            
        except Exception as e:
            logger.error(f"请求停止监控失败: {str(e)}")
            self.append_log(f"请求停止监控失败: {str(e)}", "error")
            self.monitor_button.setText("开始监控")
            self.monitor_button.setEnabled(True)
    
    def on_monitor_finished(self):
        """监控线程结束回调"""
        logger.info("监控线程已结束")
        self.append_log("监控已结束", "info")
        
        # 恢复UI状态
        self.monitor_button.setText("开始监控")
        self.monitor_button.setEnabled(True)
        
        # 清理线程对象
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.deleteLater()
            self.monitor_thread = None
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 请求停止监控线程（非阻塞）
            if hasattr(self, 'monitor_thread') and self.monitor_thread and self.monitor_thread.isRunning():
                logger.info("窗口关闭，发送停止信号到监控线程...")
                self.monitor_thread.stop()
            else:
                logger.info("窗口关闭时，监控线程已不在运行")
            
            # 终止登录线程（如果仍在运行）
            if hasattr(self, 'login_thread') and self.login_thread and self.login_thread.isRunning():
                logger.info("终止登录线程…")
                try:
                    self.login_thread.terminate()
                    self.login_thread.wait(1000) # 短暂等待，避免异常
                except Exception as e:
                    logger.error(f"终止登录线程失败: {str(e)}")

            # 保存设置
            self.save_settings()
        
        except Exception as e:
            logger.error(f"关闭窗口时出错: {e}")
        finally:
            # 直接接受关闭，让操作系统处理剩余的清理工作
            event.accept()
    
    def on_video_found(self, video):
        """处理发现视频的事件
        
        Args:
            video (dict): 视频信息
        """
        try:
            # 将视频数据存入仓库
            self.video_data_store.append(video)

            # 格式化视频信息
            self.append_log("发现新视频:", "success")
            self.append_log(f"标题: {video['title']}")
            self.append_log(f"作者: {video['author']}")
            self.append_log(f"链接: {video['url']}")
            self.append_log(f"简介: {video['description'][:100]}...")
            
            analysis = video.get('analysis')
            if analysis:
                self.append_log("\nAI分析:", "info")
                self.append_log(f"内容摘要: {analysis.get('summary', '无')}")
                self.append_log(f"推荐指数: {analysis.get('score', 'N/A')}/10")
                self.append_log(f"标签: {', '.join(analysis.get('tags', []))}")
                self.append_log(f"质量评估: {analysis.get('quality', 'N/A')}")
                self.append_log(f"受众分析: {analysis.get('audience', 'N/A')}")
                self.append_log(f"创作者评价: {analysis.get('creator', 'N/A')}")
            
            self.append_log("-" * 50)
            
            # 更新RSS预览
            self.refresh_preview()
            
        except Exception as e:
            logger.error(f"处理视频信息失败: {str(e)}")
            self.append_log(f"处理视频信息失败: {str(e)}", "error")
    
    def on_monitor_error(self, error):
        """处理监控错误
        
        Args:
            error (str): 错误信息
        """
        self.append_log(f"监控错误: {error}", "error")
    
    def update_deepseek_key(self, key):
        """更新DeepSeek API密钥
        
        Args:
            key (str): API密钥
        """
        if self.analyzer is not None:
            self.analyzer.set_api_key(key)
        self.statusBar().showMessage("已更新DeepSeek API密钥", 3000)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
    
    def filter_log(self, filter_type):
        """过滤日志
        
        Args:
            filter_type (str): 过滤类型
        """
        # 获取原始日志文本
        text = self.log_text.toPlainText()
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            if filter_type == "全部":
                filtered_lines.append(line)
            elif filter_type == "视频信息" and ("发现新视频" in line or "标题" in line or "作者" in line):
                filtered_lines.append(line)
            elif filter_type == "AI分析" and "AI分析" in line:
                filtered_lines.append(line)
            elif filter_type == "错误" and ("错误" in line or "失败" in line):
                filtered_lines.append(line)
        
        # 更新日志显示
        self.log_text.setText('\n'.join(filtered_lines))
    
    def append_log(self, text, level="info"):
        """添加日志
        
        Args:
            text (str): 日志文本
            level (str): 日志级别
        """
        # 根据日志级别设置颜色
        color = {
            "info": "black",
            "success": "green",
            "warning": "orange",
            "error": "red"
        }.get(level, "black")
        
        # 添加时间戳
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_text = f'<p style="color: {color};">[{timestamp}] {text}</p>'
        
        # 添加到日志文本框
        self.log_text.append(formatted_text)
        
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def refresh_preview(self):
        """刷新RSS预览"""
        try:
            preview = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
    <title>{self.rss_title.text()}</title>
    <description>{self.rss_description.text()}</description>
    <link>https://www.bilibili.com</link>
    <language>zh-cn</language>
    <lastBuildDate>{time.strftime('%a, %d %b %Y %H:%M:%S %z')}</lastBuildDate>
"""
            
            for video in self.video_data_store:
                # 安全地获取数据，如果键不存在则返回空字符串或默认值
                title = video.get('title', '无标题')
                url = video.get('url', '')
                author = video.get('author', '未知作者')
                description = video.get('description', '')
                analysis = video.get('analysis', {})
                
                # 构建描述内容
                cdata_content = f"{description}\n\n"
                
                if analysis:
                    cdata_content += "--- AI分析 ---\n"
                    cdata_content += f"内容摘要: {analysis.get('summary', 'N/A')}\n"
                    cdata_content += f"推荐指数: {analysis.get('score', 'N/A')}/10\n"
                    cdata_content += f"标签: {', '.join(analysis.get('tags', []))}\n"
                    cdata_content += f"质量评估: {analysis.get('quality', 'N/A')}\n"
                    cdata_content += f"受众分析: {analysis.get('audience', 'N/A')}\n"
                    cdata_content += f"创作者评价: {analysis.get('creator', 'N/A')}\n"

                preview += f"""
    <item>
        <title>{title}</title>
        <link>{url}</link>
        <author>{author}</author>
        <description><![CDATA[{cdata_content}]]></description>
    </item>
"""
            
            preview += """
</channel>
</rss>
"""
            
            # 更新预览文本框
            self.preview_text.setPlainText(preview)
            self.append_log("RSS预览已刷新", "success")
            
        except Exception as e:
            logger.error(f"刷新RSS预览失败: {str(e)}", exc_info=True)
            self.preview_text.setPlainText(f"生成RSS预览失败: {e}")
            self.append_log(f"刷新RSS预览失败: {e}", "error")
    
    def export_rss(self):
        """导出RSS文件"""
        try:
            # 获取当前预览内容
            content = self.preview_text.toPlainText()
            if not content:
                QMessageBox.warning(self, "警告", "没有可导出的内容")
                return
                
            # 保存文件
            filename = f"bilibili_rss_{time.strftime('%Y%m%d_%H%M%S')}.xml"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.statusBar().showMessage(f"RSS已导出到 {filename}", 3000)
            QMessageBox.information(self, "成功", f"RSS已导出到 {filename}")
            
        except Exception as e:
            logger.error(f"导出RSS失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"导出RSS失败: {str(e)}")

    def clear_video_cache(self):
        """清空已发现的视频数据"""
        self.video_data_store.clear()
        self.refresh_preview() # 清空后立即刷新预览
        self.append_log("视频缓存已清空", "success")

def run_app():
    """运行应用"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 