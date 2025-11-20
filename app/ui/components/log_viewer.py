"""日志查看器组件 - 液态玻璃版"""
from nicegui import ui
from datetime import datetime
from typing import List
from app.ui.components.glass_card import glass_card

class LogViewer:
    def __init__(self, max_lines: int = 100):
        self.max_lines = max_lines
        self.logs: List[tuple] = []
        self.container = None
    
    def create(self):
        # 使用 glass_card，并在顶部增加一个深色 Header 模拟终端
        with glass_card(classes='w-full flex flex-col overflow-hidden p-0 border-t-2 border-t-cyan-500/50'):
            
            # Terminal Header
            with ui.row().classes('w-full bg-black/40 px-4 py-2 items-center justify-between border-b border-white/5 backdrop-blur-md'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('terminal').classes('text-cyan-400 text-xs')
                    ui.label('SYSTEM LOGS').classes('text-[10px] font-mono font-bold text-cyan-400 tracking-widest')
                
                ui.button(icon='delete', on_click=self.clear).props('flat round dense size=xs color=grey').classes('opacity-50 hover:opacity-100')

            # Log Content Area
            self.container = ui.column().classes(
                'w-full h-64 overflow-y-auto p-4 font-mono text-xs gap-1 scroll-smooth bg-black/10'
            )
            with self.container:
                ui.label('> System ready.').classes('text-gray-600 italic')
        
        return self
    
    def add_log(self, message: str, level: str = 'INFO'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # 霓虹配色
        color_map = {
            'INFO': 'text-cyan-300 shadow-[0_0_5px_rgba(103,232,249,0.3)]',
            'WARNING': 'text-yellow-400',
            'ERROR': 'text-red-400 font-bold shadow-[0_0_8px_rgba(248,113,113,0.4)]'
        }
        color = color_map.get(level, 'text-gray-300')
        
        self.logs.append((timestamp, level, message))
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)
        
        if self.container:
            self.container.clear()
            with self.container:
                for time_str, lvl, msg in self.logs:
                    with ui.row().classes('gap-3 items-start no-wrap'):
                        ui.label(time_str).classes('text-gray-600 select-none w-16 shrink-0')
                        ui.label(lvl).classes(f'{color} w-12 shrink-0 font-bold')
                        ui.label(msg).classes('text-gray-300 break-all')
                
                ui.run_javascript(f'var el = document.querySelector(".q-card__section--vert"); if(el) el.scrollTop = el.scrollHeight;')
    
    def clear(self):
        self.logs.clear()
        if self.container: self.container.clear()
