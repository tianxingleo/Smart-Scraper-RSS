"""
设置对话框模块
"""
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDoubleSpinBox, QPushButton,
    QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt

class SettingsDialog(QDialog):
    """设置对话框类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.setModal(True)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # API设置组
        api_group = QGroupBox('API设置')
        api_layout = QFormLayout()
        
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setText(os.getenv('OPENAI_API_KEY', ''))
        api_layout.addRow('OpenAI API密钥:', self.api_key_edit)
        
        self.model_edit = QLineEdit()
        self.model_edit.setText(os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'))
        api_layout.addRow('OpenAI模型:', self.model_edit)
        
        # DeepSeek API密钥输入
        self.deepseek_api_key_edit = QLineEdit()
        self.deepseek_api_key_edit.setText(os.getenv('DEEPSEEK_API_KEY', ''))
        api_layout.addRow('DeepSeek API密钥:', self.deepseek_api_key_edit)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # 爬虫设置组
        crawler_group = QGroupBox('爬虫设置')
        crawler_layout = QFormLayout()
        
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.5, 10.0)
        self.delay_spin.setValue(float(os.getenv('CRAWL_DELAY', 2.0)))
        crawler_layout.addRow('爬取延迟(秒):', self.delay_spin)
        
        self.max_items_spin = QDoubleSpinBox()
        self.max_items_spin.setRange(10, 100)
        self.max_items_spin.setValue(float(os.getenv('MAX_ITEMS_PER_SOURCE', 50)))
        crawler_layout.addRow('每个来源最大条数:', self.max_items_spin)
        
        crawler_group.setLayout(crawler_layout)
        layout.addWidget(crawler_group)
        
        # AI评分设置组
        score_group = QGroupBox('AI评分设置')
        score_layout = QFormLayout()
        
        self.min_score_spin = QDoubleSpinBox()
        self.min_score_spin.setRange(0.0, 5.0)
        self.min_score_spin.setValue(float(os.getenv('MIN_SCORE_THRESHOLD', 3.5)))
        score_layout.addRow('最低合格分数:', self.min_score_spin)
        
        self.max_negative_spin = QDoubleSpinBox()
        self.max_negative_spin.setRange(0.0, 5.0)
        self.max_negative_spin.setValue(float(os.getenv('MAX_NEGATIVE_SCORE', 2.0)))
        score_layout.addRow('最高负面分数:', self.max_negative_spin)
        
        score_group.setLayout(score_layout)
        layout.addWidget(score_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton('保存')
        save_button.clicked.connect(self.save_settings)
        button_layout.addWidget(save_button)
        
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
    def save_settings(self):
        """保存设置"""
        # 更新环境变量
        os.environ['OPENAI_API_KEY'] = self.api_key_edit.text()
        os.environ['OPENAI_MODEL'] = self.model_edit.text()
        os.environ['CRAWL_DELAY'] = str(self.delay_spin.value())
        os.environ['MAX_ITEMS_PER_SOURCE'] = str(int(self.max_items_spin.value()))
        os.environ['MIN_SCORE_THRESHOLD'] = str(self.min_score_spin.value())
        os.environ['MAX_NEGATIVE_SCORE'] = str(self.max_negative_spin.value())
        
        # 添加DeepSeek API密钥到环境变量
        os.environ['DEEPSEEK_API_KEY'] = self.deepseek_api_key_edit.text()
        
        # 保存到.env文件
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(f'OPENAI_API_KEY={os.environ["OPENAI_API_KEY"]}\n')
            f.write(f'OPENAI_MODEL={os.environ["OPENAI_MODEL"]}\n')
            f.write(f'CRAWL_DELAY={os.environ["CRAWL_DELAY"]}\n')
            f.write(f'MAX_ITEMS_PER_SOURCE={os.environ["MAX_ITEMS_PER_SOURCE"]}\n')
            f.write(f'MIN_SCORE_THRESHOLD={os.environ["MIN_SCORE_THRESHOLD"]}\n')
            f.write(f'MAX_NEGATIVE_SCORE={os.environ["MAX_NEGATIVE_SCORE"]}\n')
            
        self.accept() 