"""统计卡片组件"""
from nicegui import ui

def stats_card(title: str, value: int, icon: str, color: str = 'cyan'):
    """玻璃拟态统计卡片"""
    # 使用 glass-panel 类
    # 使用 hover:scale-105 实现悬停轻微放大
    with ui.card().classes('glass-panel p-6 min-w-[220px] transition-transform duration-300 hover:scale-105 cursor-default'):
        with ui.row().classes('items-center gap-5 no-wrap'):
            # 图标增加光晕效果
            with ui.element('div').classes(f'p-3 rounded-xl bg-{color}-500/20 shadow-[0_0_15px_rgba(0,0,0,0.3)]'):
                ui.icon(f'mdi-{icon}').classes(f'text-4xl text-{color}-300')
            
            with ui.column().classes('gap-1'):
                ui.label(title).classes('text-xs font-bold text-gray-400 uppercase tracking-wider')
                # 数字使用渐变色
                ui.label(str(value)).classes(f'text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-{color}-300 to-white')
