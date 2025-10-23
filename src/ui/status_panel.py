"""
状态面板模块
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt

class StatusPanel(QWidget):
    """状态面板类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 状态组
        status_group = QGroupBox('运行状态')
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel('就绪')
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # 统计组
        stats_group = QGroupBox('统计信息')
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel('已处理: 0\n合格内容: 0')
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Token统计组
        token_group = QGroupBox('Token使用')
        token_layout = QVBoxLayout()
        
        self.token_label = QLabel('输入Token: 0\n输出Token: 0')
        token_layout.addWidget(self.token_label)
        
        token_group.setLayout(token_layout)
        layout.addWidget(token_group)
        
        layout.addStretch()
        
    def clear(self):
        """清空状态"""
        self.status_label.setText('就绪')
        self.stats_label.setText('已处理: 0\n合格内容: 0')
        self.token_label.setText('输入Token: 0\n输出Token: 0')
        
    def update_status(self, text):
        """更新状态文本"""
        self.status_label.setText(text)
        
    def update_stats(self, total, qualified):
        """更新统计信息"""
        self.stats_label.setText(
            f'已处理: {total}\n'
            f'合格内容: {qualified}'
        )
        
    def update_tokens(self, input_tokens, output_tokens):
        """更新Token统计"""
        self.token_label.setText(
            f'输入Token: {input_tokens}\n'
            f'输出Token: {output_tokens}'
        ) 