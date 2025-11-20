"""应用主布局 - 侧边栏 + 内容区"""
from nicegui import ui
from contextlib import contextmanager

# 1. 定义自定义 CSS
CUSTOM_CSS = """
<style>
    /* 液态流动背景动画 */
    @keyframes gradient-animation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .liquid-background {
        background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #4c1d95);
        background-size: 400% 400%;
        animation: gradient-animation 15s ease infinite;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1; /* 放在最底层 */
    }

    /* 玻璃拟态核心样式 */
    .glass-panel {
        background: rgba(255, 255, 255, 0.05); /* 极低透明度的白色 */
        backdrop-filter: blur(16px);           /* 毛玻璃模糊效果 */
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1); /* 微弱的边框 */
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        color: white;
    }
    
    /* 悬停时的光泽效果 */
    .glass-panel:hover {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }

    /* 滚动条美化 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent; 
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.2); 
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.4); 
    }
    
    /* 字体引入 (Bonus) */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&display=swap');
    body { font-family: 'Rajdhani', sans-serif; }
</style>
"""

def create_header():
    """创建悬浮玻璃顶栏"""
    # 使用 glass-panel 类，去除默认的背景色 bg-blue-600
    with ui.header().classes('bg-transparent p-4'): 
        with ui.row().classes('glass-panel w-full rounded-2xl px-6 py-3 items-center justify-between'):
            with ui.row().classes('items-center gap-4'):
                # 加上一个发光的图标
                ui.icon('rocket').classes('text-3xl text-cyan-400 drop-shadow-lg')
                ui.label('Smart Scraper RSS').classes('text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400')
            
            with ui.row().classes('items-center gap-2'):
                ui.label('AI Enhanced').classes('text-xs font-mono text-cyan-200 border border-cyan-500/30 px-2 py-1 rounded')

def create_sidebar(current_page: str = 'dashboard'):
    """创建悬浮玻璃侧边栏"""
    # 使用 drawer 但设置为透明，内部放一个 glass card
    with ui.left_drawer(value=True).classes('bg-transparent no-shadow border-none p-4'):
        with ui.column().classes('glass-panel h-full w-full rounded-2xl p-4 gap-4'):
            ui.label('MENU').classes('text-xs font-bold text-gray-400 tracking-widest mb-2')
            
            menu_items = [
                ('dashboard', '📊 Dashboard', '/dashboard'),
                ('sources', '🔗 Sources', '/sources'),
                ('settings', '⚙️ Settings', '/settings'),
            ]
            
            for page_id, label, path in menu_items:
                is_active = page_id == current_page
                # 选中态：高亮的渐变背景
                # 未选中态：透明，鼠标悬停微亮
                base_class = 'w-full justify-start rounded-xl transition-all duration-300 '
                if is_active:
                    style_class = base_class + 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-300 border border-cyan-500/50 shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                else:
                    style_class = base_class + 'text-gray-300 hover:bg-white/10 hover:text-white'
                
                ui.button(label, on_click=lambda p=path: ui.navigate.to(p)).classes(style_class).props('flat')

@contextmanager
def create_main_layout(current_page: str = 'dashboard'):
    """应用主布局入口"""
    # 注入 CSS
    ui.add_head_html(CUSTOM_CSS)
    
    # 添加液态背景层 (div)
    ui.element('div').classes('liquid-background')
    
    # 动态光效 (Bonus)
    ui.element('div').classes('fixed top-1/4 left-1/4 w-96 h-96 bg-purple-500/30 rounded-full blur-[100px] animate-pulse z-[-1]')
    ui.element('div').classes('fixed bottom-1/4 right-1/4 w-80 h-80 bg-cyan-500/30 rounded-full blur-[100px] animate-bounce z-[-1]')

    create_header()
    create_sidebar(current_page)
    
    # 主内容区域，也是透明的，内容自己会有玻璃卡片
    with ui.column().classes('w-full p-4 pl-0 overflow-auto text-gray-100'):
        # 这里加一个 max-w 让在大屏上不要太散
        with ui.column().classes('w-full max-w-7xl mx-auto gap-6'):
            yield
    
    # 简单的底部版权，稍微弱化
    with ui.footer().classes('bg-transparent p-2 text-center'):
        ui.label('© 2025 Smart Scraper RSS').classes('text-xs text-gray-500 font-mono')
