"""日志查看器组件"""
from nicegui import ui
from datetime import datetime
from typing import List

class LogViewer:
    """全息风格日志查看器"""
    
    def __init__(self, max_lines: int = 100):
        self.max_lines = max_lines
        self.logs: List[str] = []
        self.container = None
    
    def create(self):
        """创建日志查看器 UI"""
        # 使用更深色的半透明背景，模拟终端
        with ui.card().classes('w-full glass-panel p-0 overflow-hidden border-t-2 border-t-cyan-500/50'):
            # 终端顶栏
            with ui.row().classes('w-full bg-black/40 px-4 py-2 items-center justify-between border-b border-white/5'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('terminal').classes('text-cyan-500 text-sm')
                    ui.label('SYSTEM LOGS').classes('text-xs font-mono font-bold text-cyan-500 tracking-widest')
                
                # 清除按钮改为图标
                ui.button(icon='delete_sweep', on_click=self.clear).props('flat dense size=sm color=grey').classes('hover:text-red-400 transition-colors')

            # 日志内容区域
            self.container = ui.column().classes(
                'bg-black/20 p-4 h-64 overflow-y-auto font-mono text-xs gap-1 scroll-smooth'
            )
            # 初始提示
            with self.container:
                ui.label('> System ready. Waiting for tasks...').classes('text-gray-500 italic')
        
        return self
    
    def add_log(self, message: str, level: str = 'INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 赛博风格配色
        color_map = {
            'INFO': 'text-cyan-300',
            'WARNING': 'text-yellow-400 font-bold',
            'ERROR': 'text-red-400 font-bold drop-shadow-[0_0_5px_rgba(248,113,113,0.5)]' # 错误带发光
        }
        color = color_map.get(level, 'text-gray-300')
        
        log_entry = f'[{timestamp}]'
        
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)
        self.logs.append((log_entry, level, message)) # Store structured data
        
        if self.container:
            self.container.clear()
            with self.container:
                for time_str, lvl, msg in self.logs:
                    with ui.row().classes('gap-2 items-start no-wrap'):
                        ui.label(time_str).classes('text-gray-600 select-none')
                        ui.label(f'[{lvl}]').classes(f'{color} w-16 shrink-0')
                        ui.label(msg).classes('text-gray-300 break-all')
                
                # 自动滚动到底部 (NiceGUI trick)
                ui.run_javascript(f'document.querySelector(".q-card__section--vert").scrollTop = document.querySelector(".q-card__section--vert").scrollHeight')
    
    def clear(self):
        self.logs.clear()
        if self.container:
            self.container.clear()
