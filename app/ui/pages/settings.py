"""Settings 设置页面"""
from nicegui import ui
from app.ui.layout import create_main_layout
from app.ui.components import LogViewer
from app.core import scheduler_manager, task_queue
from app.config import settings
import os

@ui.page('/settings')
def settings_page():
    """设置页面"""
    with create_main_layout('settings'):
        ui.label('⚙️ 设置').classes('text-3xl font-bold mb-6')
        
        # RSS 配置和使用说明
        with ui.card().classes('w-full p-4 mb-4 bg-green-50'):
            ui.label('📡 RSS Feed 配置').classes('text-xl font-bold mb-4')
            
            with ui.column().classes('gap-3'):
                ui.label('RSS Feed 地址').classes('font-bold')
                feed_url = f'http://localhost:{settings.UI_PORT}/feed.xml'
                
                with ui.row().classes('items-center gap-2 w-full'):
                    ui.input('', value=feed_url).classes('flex-1').props('readonly outlined dense')
                    ui.button(
                        '复制地址',
                        on_click=lambda: ui.run_javascript(f'navigator.clipboard.writeText("{feed_url}").then(() => alert("已复制到剪贴板！"))'),
                        color='primary'
                    ).props('dense')
                    ui.button(
                        icon='mdi-open-in-new',
                        on_click=lambda: ui.run_javascript(f'window.open("{feed_url}", "_blank")'),
                        color='secondary'
                    ).props('dense')
                
                ui.separator()
                
                ui.label('使用方法').classes('font-bold mt-2')
                ui.label('1. 复制上面的 RSS 地址').classes('text-sm')
                ui.label('2. 在 RSS 阅读器中添加订阅（推荐：Feedly、Inoreader、NetNewsWire）').classes('text-sm')
                ui.label('3. RSS 将自动包含所有抓取的内容、AI 摘要和情感分析').classes('text-sm')
                
                ui.separator()
                
                ui.label('RSS 设置').classes('font-bold mt-2')
                ui.label(f'• 最大项数: {settings.RSS_MAX_ITEMS} 条').classes('text-sm')
                ui.label(f'• Feed 标题: {settings.RSS_FEED_TITLE}').classes('text-sm')
                ui.label(f'• Feed 描述: {settings.RSS_FEED_DESCRIPTION}').classes('text-sm')
        
        # API 配置
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('🔑 API 配置').classes('text-xl font-bold mb-4')
            
            with ui.column().classes('gap-4 w-full max-w-2xl'):
                api_key_input = ui.input(
                    'DeepSeek API Key',
                    value=settings.DEEPSEEK_API_KEY or '',
                    password=True,
                    password_toggle_button=True
                ).classes('w-full')
                
                def save_api_key():
                    """保存 API Key 到环境变量（仅当前会话）"""
                    new_key = api_key_input.value
                    if new_key:
                        os.environ['DEEPSEEK_API_KEY'] = new_key
                        ui.notify('✅ API Key 已保存（当前会话有效）', type='positive')
                    else:
                        ui.notify('⚠️ 请输入有效的 API Key', type='warning')
                
                ui.button('保存 API Key', on_click=save_api_key, color='primary')
                ui.label('提示：API Key 保存在当前会话的环境变量中，重启后需重新设置').classes('text-sm text-gray-600')
                ui.label('永久保存：请手动添加到系统环境变量 DEEPSEEK_API_KEY').classes('text-sm text-gray-600')
                ui.link('获取 API Key', 'https://platform.deepseek.com/', new_tab=True).classes('text-blue-600')
        
        # 日志查看器
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('📋 系统日志').classes('text-xl font-bold mb-4')
            log_viewer = LogViewer(max_lines=50).create()
            # 添加测试日志
            log_viewer.add_log('系统启动成功', 'INFO')
            log_viewer.add_log('日志查看器已初始化', 'INFO')
        
        # 调度器状态
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('⏰ 调度器状态').classes('text-xl font-bold mb-4')
            
            jobs = scheduler_manager.get_jobs()
            ui.label(f'当前运行中的定时任务: {len(jobs)} 个').classes('text-lg mb-2')
            
            if jobs:
                with ui.column().classes('gap-2'):
                    for job in jobs:
                        with ui.card().classes('p-3 bg-gray-100'):
                            ui.label(f'任务 ID: {job.id}').classes('font-bold')
                            ui.label(f'下次执行: {job.next_run_time}').classes('text-sm text-gray-600')
            else:
                ui.label('暂无定时任务').classes('text-gray-500')
        
        # 任务队列状态
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('📋 任务队列状态').classes('text-xl font-bold mb-4')
            
            queue_size = task_queue.get_queue_size()
            ui.label(f'队列中的任务: {queue_size} 个').classes('text-lg')
            ui.label(f'工作线程数: 2').classes('text-lg')
        
        # 浏览器登录
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('🌐 浏览器登录').classes('text-xl font-bold mb-4')
            ui.label('首次使用建议手动登录以获取 Cookie，提高抓取成功率。').classes('text-sm text-gray-600 mb-2')
            
            from app.services.scraper_service import open_login_browser
            
            def handle_open_browser():
                open_login_browser()
                ui.notify('浏览器已打开，请手动登录目标网站', type='positive')
            
            ui.button('打开浏览器 (手动登录)', on_click=handle_open_browser, icon='login', color='accent')
            ui.label('注意：如果配置了 Headless 模式，请先在 .env 中关闭它，否则看不到窗口。').classes('text-xs text-red-500 mt-1')

        # 系统配置
        with ui.card().classes('w-full p-4'):
            ui.label('🔧 系统配置').classes('text-xl font-bold mb-4')
            
            with ui.column().classes('gap-3'):
                ui.label(f'应用名称: {settings.APP_NAME}')
                ui.label(f'应用版本: {settings.APP_VERSION}')
                ui.label(f'UI 端口: {settings.UI_PORT}')
                ui.label(f'数据库: {settings.DATABASE_URL}')
                ui.label(f'RSS 最大项数: {settings.RSS_MAX_ITEMS}')
