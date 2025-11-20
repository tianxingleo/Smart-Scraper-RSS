"""统计卡片组件 - 适配液态玻璃风格"""
from nicegui import ui
from app.ui.components.glass_card import glass_card

def stats_card(title: str, value: int, icon: str, color: str = '#66ccff'):
    """液态玻璃统计卡片 - 统一主题色 66ccff"""
    # 使用 arbitrary value syntax 适配主题色
    # color 参数保留但默认为主题色，方便微调，但主要逻辑统一
    
    # 主色调 hex: #66ccff (RGB: 102, 204, 255)
    
    with glass_card(classes='p-6 min-w-[220px] cursor-default hover:bg-[#66ccff]/5 transition-colors'):
        with ui.row().classes('items-center gap-5 no-wrap'):
            # 图标容器：使用主题色
            with ui.element('div').classes(f'p-4 rounded-2xl bg-[#66ccff]/10 border border-[#66ccff]/20 shadow-[inset_0_0_20px_rgba(102,204,255,0.1)] backdrop-blur-md group-hover:scale-110 transition-transform duration-300'):
                ui.icon(f'{icon}').classes(f'text-3xl text-[#66ccff] drop-shadow-lg')
            
            with ui.column().classes('gap-1'):
                ui.label(title).classes('text-xs font-bold text-gray-400 uppercase tracking-wider opacity-80')
                # 数字：大号 + 小范围渐变色
                ui.label(str(value)).classes(f'text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-white to-[#66ccff]')