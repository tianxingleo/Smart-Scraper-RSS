from nicegui import ui
from contextlib import contextmanager

@contextmanager
def glass_card(classes: str = '', style: str = ''):
    """
    iOS 26 风格液态玻璃卡片容器
    自动包含：
    1. 噪点纹理 (Noise Overlay) - 增加真实质感
    2. 交互式高光 (Glare Layer) - 跟随鼠标移动的光泽
    3. 3D 视差内容容器 (Content Layer) - 内容悬浮感
    """
    # 基础容器：liquid-glass-card 类定义了核心玻璃属性
    with ui.element('div').classes(f'liquid-glass-card group {classes}').style(style):
        # 1. 噪点层 (SVG Filter)
        ui.element('div').classes('noise-overlay')
        
        # 2. 高光层 (JS 控制位置)
        ui.element('div').classes('glare-layer')
        
        # 3. 内容层 (Z轴突起)
        with ui.element('div').classes('card-content w-full h-full'):
            yield
