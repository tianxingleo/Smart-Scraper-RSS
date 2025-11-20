"""Dashboard 主控台页面"""
from nicegui import ui
from app.ui.layout import create_main_layout
from app.ui.components import stats_card
from app.database.crud import get_sources, get_scraped_items
from app.core import scheduler_manager

@ui.page('/dashboard')
def dashboard():
    """主控台页面"""
    with create_main_layout('dashboard'):
        ui.label('📊 主控台').classes('text-3xl font-bold mb-6')
        
        # 统计卡片
        with ui.row().classes('gap-4 mb-6'):
            sources = get_sources()
            items = get_scraped_items(limit=1000)
            jobs = scheduler_manager.get_jobs()
            
            # 今日抓取数量
            from datetime import datetime, date
            today = date.today()
            today_items = [i for i in items if i.created_at.date() == today]
            
            stats_card('源数量', len(sources), 'folder-multiple', 'blue')
            stats_card('抓取项', len(items), 'file-document-multiple', 'green')
            stats_card('今日抓取', len(today_items), 'calendar-today', 'orange')
            stats_card('定时任务', len(jobs), 'clock-outline', 'purple')
        
        # RSS Feed 引导卡片
        with ui.card().classes('w-full p-4 mb-6 bg-blue-50'):
            with ui.row().classes('items-center gap-4'):
                ui.icon('mdi-rss').classes('text-4xl text-blue-600')
                with ui.column().classes('flex-1'):
                    ui.label('📡 RSS Feed 订阅').classes('text-lg font-bold mb-2')
                    ui.label('您可以使用 RSS 阅读器订阅本应用生成的 Feed').classes('text-sm text-gray-600')
                    with ui.row().classes('gap-2 mt-2'):
                        feed_url = 'http://localhost:8080/feed.xml'
                        ui.input('RSS 地址', value=feed_url).classes('flex-1').props('readonly')
                        ui.button('复制', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText("{feed_url}")'), color='primary').props('flat dense')
                        ui.button(icon='mdi-open-in-new', on_click=lambda: ui.run_javascript(f'window.open("{feed_url}", "_blank")'), color='secondary').props('flat dense')
        
        # 最近抓取的内容
        with ui.card().classes('w-full p-4'):
            ui.label('📰 最近抓取内容').classes('text-xl font-bold mb-4')
            
            recent_items = get_scraped_items(limit=10)
            
            if recent_items:
                columns = [
                    {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                    {'name': 'title', 'label': '标题', 'field': 'title', 'align': 'left'},
                    {'name': 'sentiment', 'label': '情感', 'field': 'sentiment', 'align': 'center'},
                    {'name': 'created_at', 'label': '创建时间', 'field': 'created_at', 'align': 'center'},
                ]
                
                rows = [
                    {
                        'id': item.id,
                        'title': item.title[:50] + '...' if len(item.title) > 50 else item.title,
                        'sentiment': item.sentiment or 'Unknown',
                        'created_at': item.created_at.strftime('%Y-%m-%d %H:%M')
                    }
                    for item in recent_items
                ]
                
                ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
            else:
                ui.label('暂无抓取内容').classes('text-gray-500')
        
        # 快速操作
        with ui.card().classes('w-full p-4 mt-6'):
            ui.label('⚡ 快速操作').classes('text-xl font-bold mb-4')
            with ui.row().classes('gap-4'):
                ui.button('添加源', on_click=lambda: ui.navigate.to('/sources'), color='primary').props('icon=add')
                ui.button('查看源', on_click=lambda: ui.navigate.to('/sources'), color='secondary').props('icon=list')
                ui.button('设置', on_click=lambda: ui.navigate.to('/settings'), color='grey').props('icon=settings')
