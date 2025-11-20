"""Dashboard 主控台页面 - 适配液态玻璃风格"""
from nicegui import ui
from app.ui.layout import create_main_layout
from app.ui.components import stats_card, glass_card, enhanced_table
from app.database.crud import get_sources, get_scraped_items
from app.core import scheduler_manager

@ui.page('/dashboard')
def dashboard():
    """主控台页面"""
    with create_main_layout('dashboard'):
        ui.label('Dashboard').classes('text-4xl font-bold mb-6 tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-400')
        
        # 1. 统计卡片区
        with ui.row().classes('gap-6 mb-8 w-full'):
            sources = get_sources()
            items = get_scraped_items(limit=1000)
            jobs = scheduler_manager.get_jobs()
            
            # 计算今日数据
            from datetime import date
            today = date.today()
            today_items = [i for i in items if i.created_at.date() == today]
            
            stats_card('Active Sources', len(sources), 'folder-multiple', 'blue')
            stats_card('Total Items', len(items), 'file-document-multiple', 'purple')
            stats_card('Today Scraped', len(today_items), 'calendar-today', 'pink')
            stats_card('Scheduled Jobs', len(jobs), 'clock-outline', 'emerald')
        
        # 2. RSS 引导卡片 (大横幅玻璃)
        with glass_card(classes='w-full p-8 mb-8 relative overflow-hidden'):
            # 装饰性背景光斑
            ui.element('div').classes('absolute top-0 right-0 w-64 h-64 bg-cyan-500/20 rounded-full blur-[80px] translate-x-1/3 -translate-y-1/3 pointer-events-none')
            
            with ui.row().classes('items-center gap-6 relative z-10'):
                with ui.element('div').classes('p-4 rounded-full bg-gradient-to-br from-orange-400/20 to-red-400/20 border border-white/10 shadow-[0_0_20px_rgba(251,146,60,0.3)]'):
                    ui.icon('mdi-rss').classes('text-5xl text-orange-400')
                
                with ui.column().classes('flex-1'):
                    ui.label('Your Personal RSS Feed').classes('text-2xl font-bold text-white mb-2')
                    ui.label('Subscribe to this feed in Reeder, Feedly or any RSS reader.').classes('text-base text-gray-400')
                    
                    with ui.row().classes('gap-3 mt-4 w-full max-w-2xl bg-black/20 p-2 rounded-xl border border-white/10'):
                        feed_url = 'http://localhost:8081/feed.xml'
                        ui.input(value=feed_url).classes('flex-1 text-white').props('readonly borderless dense input-class="text-white font-mono"').style('background: transparent;')
                        ui.button('Copy', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText("{feed_url}")'), color='white').props('flat dense class="text-black bg-white rounded-lg px-4 hover:bg-gray-200"')
                        ui.button(icon='mdi-open-in-new', on_click=lambda: ui.run_javascript(f'window.open("{feed_url}", "_blank")'), color='white').props('flat dense round')
        
        # 3. 最近内容列表
        with glass_card(classes='w-full p-6'):
            with ui.row().classes('justify-between items-center mb-6'):
                ui.label('Recent Activities').classes('text-xl font-bold text-white')
                ui.button('View All', on_click=lambda: ui.navigate.to('/sources'), color='white').props('flat dense size=sm icon-right=arrow_forward')

            recent_items = get_scraped_items(limit=10)
            
            if recent_items:
                columns = [
                    {'name': 'title', 'label': 'Title', 'field': 'title', 'align': 'left', 'classes': 'font-bold text-gray-100'},
                    {'name': 'sentiment', 'label': 'Sentiment', 'field': 'sentiment', 'align': 'center', 'classes': 'text-gray-300'},
                    {'name': 'created_at', 'label': 'Time', 'field': 'created_at', 'align': 'right', 'classes': 'text-gray-400 font-mono'},
                ]
                
                rows = [
                    {
                        'id': item.id,
                        'title': item.title[:60] + '...' if len(item.title) > 60 else item.title,
                        'sentiment': item.sentiment or 'Neutral',
                        'created_at': item.created_at.strftime('%H:%M')
                    }
                    for item in recent_items
                ]
                
                # 移除 enhanced_table 自带的样式，完全融入玻璃背景
                table = enhanced_table(columns=columns, rows=rows)
                table.classes('bg-transparent shadow-none border-none')
            else:
                ui.label('No content scraped yet.').classes('text-gray-500 italic w-full text-center py-8')

        # 4. 底部快速操作栏 (使用玻璃卡片作为按钮容器)
        with ui.row().classes('w-full gap-4 mt-8'):
            def action_btn(label, icon, path, color):
                # 这里的 glass_card 充当了一个大按钮
                with glass_card(classes='flex-1 p-4 hover:bg-white/5 cursor-pointer transition-colors items-center justify-center gap-3 group relative'):
                    # 点击覆盖层
                    ui.element('div').classes('absolute inset-0 z-20').on('click', lambda: ui.navigate.to(path))
                    
                    ui.icon(icon).classes(f'text-2xl text-{color}-400 group-hover:scale-110 transition-transform duration-300 drop-shadow-md')
                    ui.label(label).classes('font-bold text-gray-300 group-hover:text-white transition-colors')

            action_btn('Add Source', 'add_circle', '/sources', 'cyan')
            action_btn('Manage Sources', 'list', '/sources', 'purple')
            action_btn('System Settings', 'settings', '/settings', 'gray')
