"""Settings 设置页面"""
from nicegui import ui
from app.ui.layout import create_main_layout
from app.core import scheduler_manager, task_queue
from app.config import settings

@ui.page('/settings')
def settings_page():
    """设置页面"""
    with create_main_layout('settings'):
        ui.label('⚙️ 设置').classes('text-3xl font-bold mb-6')
        
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
                
                ui.label('提示：API Key 保存在环境变量中').classes('text-sm text-gray-600')
        
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
        
        # 系统配置
        with ui.card().classes('w-full p-4'):
            ui.label('🔧 系统配置').classes('text-xl font-bold mb-4')
            
            with ui.column().classes('gap-3'):
                ui.label(f'应用名称: {settings.APP_NAME}')
                ui.label(f'应用版本: {settings.APP_VERSION}')
                ui.label(f'UI 端口: {settings.UI_PORT}')
                ui.label(f'数据库: {settings.DATABASE_URL}')
                ui.label(f'RSS 最大项数: {settings.RSS_MAX_ITEMS}')
