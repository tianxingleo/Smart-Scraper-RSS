import sys
import json
import requests
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineHttpRequest

class BilibiliCrawler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("B站视频爬取工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建浏览器组件
        self.browser = QWebEngineView()
        self.cookie_store = QWebEngineProfile.defaultProfile().cookieStore()
        self.cookie_store.cookieAdded.connect(self.handle_cookie_added)
        self.cookies = {}
        
        # 创建界面组件
        self.create_widgets()
        
        # 加载登录页面
        self.load_login_page()
        
    def create_widgets(self):
        # 主布局
        main_layout = QVBoxLayout()
        
        # 浏览器区域
        browser_frame = QGroupBox("扫码登录")
        browser_layout = QVBoxLayout()
        browser_layout.addWidget(self.browser)
        browser_frame.setLayout(browser_layout)
        
        # 控制区域
        control_frame = QGroupBox("操作")
        control_layout = QHBoxLayout()
        
        self.fetch_btn = QPushButton("获取推荐视频", self)
        self.fetch_btn.clicked.connect(self.fetch_recommended_videos)
        self.fetch_btn.setEnabled(False)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["API直接请求", "浏览器模拟点击"])
        
        self.result_list = QListWidget()
        self.result_list.itemClicked.connect(self.show_video_details)
        
        control_layout.addWidget(self.fetch_btn)
        control_layout.addWidget(QLabel("获取方式:"))
        control_layout.addWidget(self.method_combo)
        control_layout.addStretch()
        control_frame.setLayout(control_layout)
        
        # 详情区域
        detail_frame = QGroupBox("视频详情")
        detail_layout = QVBoxLayout()
        
        self.title_label = QLabel("标题:")
        self.desc_label = QLabel("简介:")
        self.desc_label.setWordWrap(True)
        self.subtitle_text = QTextEdit()
        self.subtitle_text.setReadOnly(True)
        
        detail_layout.addWidget(self.title_label)
        detail_layout.addWidget(self.desc_label)
        detail_layout.addWidget(QLabel("字幕:"))
        detail_layout.addWidget(self.subtitle_text)
        detail_frame.setLayout(detail_layout)
        
        # 添加组件到主布局
        main_layout.addWidget(browser_frame, 2)
        main_layout.addWidget(control_frame, 1)
        main_layout.addWidget(self.result_list, 2)
        main_layout.addWidget(detail_frame, 3)
        
        # 设置中心窗口
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def load_login_page(self):
        """加载B站登录页面"""
        login_url = "https://passport.bilibili.com/login"
        self.browser.load(QUrl(login_url))
        self.browser.urlChanged.connect(self.check_login_status)
    
    def handle_cookie_added(self, cookie):
        """处理cookie添加事件"""
        name = cookie.name().data().decode()
        value = cookie.value().data().decode()
        self.cookies[name] = value
    
    def check_login_status(self, url):
        """检查登录状态"""
        if "bilibili.com" in url.toString() and "SESSDATA" in self.cookies:
            self.fetch_btn.setEnabled(True)
            self.statusBar().showMessage("登录成功！", 3000)
    
    def fetch_recommended_videos(self):
        """获取推荐视频"""
        self.result_list.clear()
        method = self.method_combo.currentIndex()
        
        if method == 0:  # API直接请求
            self.fetch_via_api()
        else:  # 浏览器模拟点击
            self.fetch_via_browser()
    
    def fetch_via_api(self):
        """通过API获取推荐视频"""
        api_url = "https://api.bilibili.com/x/web-interface/index/top/feed/rcmd"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://www.bilibili.com/",
            "Cookie": "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            data = response.json()
            
            if data.get("code") == 0:
                for item in data["data"]["item"]:
                    bvid = item["bvid"]
                    title = item["title"]
                    list_item = QListWidgetItem(f"{title} ({bvid})")
                    list_item.setData(Qt.UserRole, bvid)
                    self.result_list.addItem(list_item)
            else:
                QMessageBox.warning(self, "错误", f"API请求失败: {data.get('message')}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"请求失败: {str(e)}")
    
    def fetch_via_browser(self):
        """通过浏览器模拟点击获取推荐视频"""
        js_code = """
        (function() {
            const items = document.querySelectorAll('.feed-card');
            const results = [];
            items.forEach(item => {
                const titleEl = item.querySelector('.bili-video-card__info--tit');
                const bvid = item.getAttribute('data-aid');
                if (titleEl && bvid) {
                    results.push({
                        title: titleEl.title,
                        bvid: bvid
                    });
                }
            });
            return results;
        })();
        """
        
        self.browser.page().runJavaScript(js_code, self.process_browser_results)
    
    def process_browser_results(self, results):
        """处理浏览器返回的结果"""
        if not results:
            QMessageBox.warning(self, "警告", "未找到视频信息")
            return
        
        for video in results:
            title = video["title"]
            bvid = video["bvid"]
            list_item = QListWidgetItem(f"{title} ({bvid})")
            list_item.setData(Qt.UserRole, bvid)
            self.result_list.addItem(list_item)
    
    def show_video_details(self, item):
        """显示视频详情和字幕"""
        bvid = item.data(Qt.UserRole)
        
        # 获取视频详情
        self.get_video_details(bvid)
        
        # 获取字幕
        self.get_video_subtitle(bvid)
    
    def get_video_details(self, bvid):
        """获取视频详情"""
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            data = response.json()
            
            if data.get("code") == 0:
                info = data["data"]
                self.title_label.setText(f"标题: {info['title']}")
                self.desc_label.setText(f"简介: {info['desc']}")
            else:
                QMessageBox.warning(self, "错误", f"获取详情失败: {data.get('message')}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"请求失败: {str(e)}")
    
    def get_video_subtitle(self, bvid):
        """获取视频字幕"""
        # 先获取cid
        cid = self.get_video_cid(bvid)
        if not cid:
            self.subtitle_text.setText("无法获取字幕: 未找到视频CID")
            return
        
        # 获取字幕信息
        subtitle_url = f"https://api.bilibili.com/x/player/v2?cid={cid}&bvid={bvid}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        }
        
        try:
            response = requests.get(subtitle_url, headers=headers)
            data = response.json()
            
            if data.get("code") == 0:
                subtitles = data["data"].get("subtitle", {}).get("subtitles", [])
                if subtitles:
                    # 获取第一个可用的字幕
                    subtitle_url = "https:" + subtitles[0]["subtitle_url"]
                    subtitle_data = requests.get(subtitle_url).json()
                    self.display_subtitle(subtitle_data)
                else:
                    self.subtitle_text.setText("该视频没有字幕")
            else:
                self.subtitle_text.setText(f"获取字幕失败: {data.get('message')}")
        except Exception as e:
            self.subtitle_text.setText(f"获取字幕失败: {str(e)}")
    
    def get_video_cid(self, bvid):
        """获取视频CID"""
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(api_url, headers=headers)
            data = response.json()
            return data["data"]["cid"] if data.get("code") == 0 else None
        except:
            return None
    
    def display_subtitle(self, subtitle_data):
        """显示字幕内容"""
        text = ""
        for item in subtitle_data["body"]:
            text += f"{item['content']}\n"
        self.subtitle_text.setText(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    crawler = BilibiliCrawler()
    crawler.show()
    sys.exit(app.exec_()) 