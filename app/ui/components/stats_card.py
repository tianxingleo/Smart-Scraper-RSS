"""统计卡片组件 - 适配液态玻璃风格"""
from nicegui import ui
from app.ui.components.glass_card import glass_card

def stats_card(title: str, value: int, icon: str, color: str = 'cyan'):
    """液态玻璃统计卡片"""
    # 使用 glass_card 替代 ui.card
    with glass_card(classes='p-6 min-w-[220px] cursor-default'):
        with ui.row().classes('items-center gap-5 no-wrap'):
            # 图标容器：磨砂玻璃 + 内发光
            with ui.element('div').classes(f'p-4 rounded-2xl bg-{color}-500/10 border border-{color}-500/20 shadow-[inset_0_0_20px_rgba({color},0.1)] backdrop-blur-md'):
                ui.icon(f'mdi-{icon}').classes(f'text-3xl text-{color}-400 drop-shadow-lg')
            
            with ui.column().classes('gap-1'):
                ui.label(title).classes('text-xs font-bold text-gray-400 uppercase tracking-wider opacity-80')
                # 数字：大号 + 渐变色
                ui.label(str(value)).classes(f'text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-{color}-200')
