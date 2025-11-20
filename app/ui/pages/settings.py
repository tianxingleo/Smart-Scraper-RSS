"""Settings 设置页面 - 液态玻璃版"""
from nicegui import ui
from app.ui.layout import create_main_layout
from app.ui.components import LogViewer, glass_card
from app.core import scheduler_manager, task_queue
from app.config import settings
import os

@ui.page('/settings')
def settings_page():
    """设置页面"""
    with create_main_layout('settings'):
        ui.label('Settings').classes('text-4xl font-bold mb-2 tracking-tight text-white drop-shadow-lg')
        ui.label('System Configuration & Logs').classes('text-sm text-gray-400 mb-8 font-light tracking-wider')
        
        # 布局：左侧设置，右侧日志
        with ui.grid().classes('grid-cols-1 lg:grid-cols-3 gap-8 w-full'):
            
            # === 左侧列：配置 ===
            with ui.column().classes('lg:col-span-1 gap-8'):
                
                # 1. RSS 配置
                with glass_card(classes='p-6'):
                    with ui.row().classes('items-center gap-3 mb-4'):
                        ui.icon('rss_feed').classes('text-orange-400 text-xl drop-shadow-[0_0_8px_rgba(251,146,60,0.8)]')
                        ui.label('RSS Feed').classes('text-lg font-bold text-white')
                    
                    feed_url = f'http://localhost:{settings.UI_PORT}/feed.xml'
                    
                    with ui.column().classes('gap-3 w-full'):
                        # 玻璃质感输入框
                        ui.input(value=feed_url).props('readonly borderless dense input-class="text-gray-300 font-mono text-xs"').classes('w-full bg-black/20 rounded-lg px-3 py-1 border border-white/5')
                        
                        with ui.row().classes('w-full gap-2'):
                            ui.button('Copy', icon='content_copy', on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText("{feed_url}")')).props('flat dense no-caps').classes('flex-1 bg-white/10 hover:bg-white/20 text-white border border-white/10 rounded-lg transition-colors text-sm')
                            ui.button('Open', icon='open_in_new', on_click=lambda: ui.run_javascript(f'window.open("{feed_url}", "_blank")')).props('flat dense no-caps').classes('flex-1 bg-orange-500/20 hover:bg-orange-500/30 text-orange-300 border border-orange-500/30 rounded-lg transition-colors text-sm')

                # 2. API 配置
                with glass_card(classes='p-6'):
                    with ui.row().classes('items-center gap-3 mb-4'):
                        ui.icon('vpn_key').classes('text-purple-400 text-xl drop-shadow-[0_0_8px_rgba(192,132,252,0.8)]')
                        ui.label('AI Credentials').classes('text-lg font-bold text-white')
                    
                    with ui.column().classes('gap-4 w-full'):
                        api_key_input = ui.input(
                            placeholder='sk-...',
                            value=settings.DEEPSEEK_API_KEY or '',
                            password=True,
                            password_toggle_button=True
                        ).props('borderless dense input-class="text-white"').classes('w-full bg-black/20 rounded-lg px-3 py-1 border border-white/5 focus-within:border-purple-500/50 transition-colors')
                        
                        def save_api_key():
                            if api_key_input.value:
                                os.environ['DEEPSEEK_API_KEY'] = api_key_input.value
                                ui.notify('API Key saved for session', type='positive', classes='glass-panel')
                        
                        ui.button('Save Key', icon='save_alt', on_click=save_api_key).props('unelevated no-caps').classes('w-full bg-purple-600 hover:bg-purple-500 text-white shadow-[0_0_15px_rgba(147,51,234,0.4)] rounded-lg font-medium transition-all hover:shadow-[0_0_25px_rgba(147,51,234,0.6)]')

                # 3. 浏览器控制
                with glass_card(classes='p-6'):
                    with ui.row().classes('items-center gap-3 mb-4'):
                        ui.icon('public').classes('text-cyan-400 text-xl drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]')
                        ui.label('Browser Control').classes('text-lg font-bold text-white')
                    
                    from app.services.scraper_service import open_login_browser
                    ui.button('Launch Login Browser', on_click=open_login_browser, icon='rocket_launch').props('unelevated no-caps').classes('w-full bg-cyan-600/80 hover:bg-cyan-500 text-white border border-cyan-400/30 rounded-lg shadow-[0_0_15px_rgba(8,145,178,0.4)] transition-all hover:scale-105')
                    ui.label('Use this to manually solve captchas.').classes('text-xs text-gray-500 mt-2')

            # === 右侧列：状态与日志 ===
            with ui.column().classes('lg:col-span-2 gap-8'):
                
                # 1. 系统状态
                with glass_card(classes='p-6'):
                    ui.label('System Status').classes('text-lg font-bold text-white mb-4')
                    
                    with ui.row().classes('w-full gap-4'):
                        # 任务队列状态
                        with ui.column().classes('flex-1 bg-white/5 rounded-xl p-4 border border-white/5'):
                            ui.label('Task Queue').classes('text-xs text-gray-400 uppercase tracking-wider')
                            ui.label(f'{task_queue.get_queue_size()} Pending').classes('text-2xl font-bold text-white')
                            ui.label('2 Workers Active').classes('text-xs text-emerald-400 flex items-center gap-1 before:content-[""] before:w-1.5 before:h-1.5 before:bg-emerald-400 before:rounded-full before:animate-pulse')

                        # 调度器状态
                        jobs = scheduler_manager.get_jobs()
                        with ui.column().classes('flex-1 bg-white/5 rounded-xl p-4 border border-white/5'):
                            ui.label('Scheduler').classes('text-xs text-gray-400 uppercase tracking-wider')
                            ui.label(f'{len(jobs)} Jobs').classes('text-2xl font-bold text-white')
                            ui.label('Running').classes('text-xs text-blue-400')

                # 2. 日志查看器 (已封装为玻璃组件)
                LogViewer(max_lines=50).create()
