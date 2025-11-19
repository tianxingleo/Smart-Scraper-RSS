"""日志查看器组件"""
from nicegui import ui
from datetime import datetime
from typing import List

class LogViewer:
    """日志查看器"""
    
    def __init__(self, max_lines: int = 100):
        self.max_lines = max_lines
        self.logs: List[str] = []
        self.container = None
    
    def create(self):
        """创建日志查看器 UI"""
        with ui.card().classes('w-full'):
            ui.label('📋 系统日志').classes('text-lg font-bold mb-2')
            self.container = ui.column().classes(
                'bg-gray-900 text-green-400 font-mono text-xs p-4 h-64 overflow-auto rounded'
            )
            
            # 添加清除按钮
            with ui.row().classes('mt-2'):
                ui.button('清除日志', on_click=self.clear, color='red').classes('text-xs')
        
        return self
    
    def add_log(self, message: str, level: str = 'INFO'):
        """
        添加日志消息
        
        Args:
            message: 日志内容
            level: 日志级别 (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 颜色映射
        color_map = {
            'INFO': 'text-green-400',
            'WARNING': 'text-yellow-400',
            'ERROR': 'text-red-400'
        }
        color = color_map.get(level, 'text-green-400')
        
        log_entry = f'[{timestamp}] [{level}] {message}'
        self.logs.append(log_entry)
        
        # 限制日志数量
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)
        
        # 更新 UI
        if self.container:
            self.container.clear()
            with self.container:
                for log in self.logs:
                    ui.label(log).classes(color)
    
    def clear(self):
        """清除所有日志"""
        self.logs.clear()
        if self.container:
            self.container.clear()
