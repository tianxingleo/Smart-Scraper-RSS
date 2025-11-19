"""统计卡片组件"""
from nicegui import ui

def stats_card(title: str, value: int, icon: str, color: str = 'blue'):
    """
    创建统计卡片
    
    Args:
        title: 卡片标题
        value: 显示的数值
        icon: Material Design 图标名称
        color: 主题颜色
    """
    with ui.card().classes('p-4 min-w-[200px] hover:shadow-lg transition-shadow'):
        with ui.row().classes('items-center justify-between w-full'):
            with ui.column().classes('gap-1'):
                ui.label(title).classes('text-sm text-gray-600')
                ui.label(str(value)).classes('text-3xl font-bold')
            ui.icon(icon).classes(f'text-5xl text-{color}-500')
