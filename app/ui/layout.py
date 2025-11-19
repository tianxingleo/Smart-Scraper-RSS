"""应用主布局 - 侧边栏 + 内容区"""
from nicegui import ui
from contextlib import contextmanager

def create_header():
    """创建顶部栏"""
    with ui.header().classes('bg-blue-600 text-white items-center justify-between px-6'):
        with ui.row().classes('items-center gap-4'):
            ui.label('🚀 Smart Scraper RSS').classes('text-2xl font-bold')
        with ui.row().classes('items-center gap-2'):
            ui.label('Powered by DeepSeek & NiceGUI').classes('text-sm')

def create_sidebar(current_page: str = 'dashboard'):
    """
    创建侧边栏导航
    
    Args:
        current_page: 当前页面名称，用于高亮
    """
    with ui.column().classes('bg-gray-800 w-64 p-4 gap-2'):
        # 导航菜单
        menu_items = [
            ('dashboard', '📊 主控台', '/dashboard'),
            ('sources', '🔗 源管理', '/sources'),
            ('settings', '⚙️ 设置', '/settings'),
        ]
        
        for page_id, label, path in menu_items:
            is_active = page_id == current_page
            btn_class = 'w-full justify-start ' + (
                'bg-blue-600 text-white' if is_active else 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            )
            ui.button(
                label,
                on_click=lambda p=path: ui.navigate.to(p)
            ).classes(btn_class).props('flat')

@contextmanager
def create_main_layout(current_page: str = 'dashboard'):
    """
    创建完整布局（Header + Sidebar + Content + Footer）
    
    Args:
        current_page: 当前页面名称
        
    Yields:
        内容区域
    """
    create_header()
    
    with ui.row().classes('w-full flex-1 no-wrap'):
        # 侧边栏
        create_sidebar(current_page)
        
        # 主内容区
        with ui.column().classes('flex-1 p-6 overflow-auto bg-gray-100'):
            yield
    
    # 底部栏
    with ui.footer().classes('bg-gray-800 text-white text-center p-3'):
        ui.label('© 2025 Smart Scraper RSS').classes('text-sm')
