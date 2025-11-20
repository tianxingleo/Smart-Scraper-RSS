"""Sources 源管理页面 - 液态玻璃版 (Fixed)"""
from nicegui import ui
from sqlmodel import Session
from app.ui.layout import create_main_layout
from app.ui.components import glass_card, enhanced_table
from app.database.crud import create_source, get_sources, delete_source, engine
from app.database.models import Source
from app.core import scheduler_manager
from app.services.scraper_service import scrape_source_async

sources_table = None

def refresh_table():
    """刷新表格数据"""
    if sources_table:
        sources = get_sources()
        rows = [
            {
                'id': s.id, 'name': s.name, 'platform': s.platform,
                'url': s.url, 'url_display': s.url[:40] + '...' if len(s.url) > 40 else s.url,
                'frequency': s.frequency, 'is_active': s.is_active,
                'status_label': 'ACTIVE' if s.is_active else 'PAUSED',
                'last_scraped': s.last_scraped.strftime('%H:%M %m/%d') if s.last_scraped else '-'
            }
            for s in sources
        ]
        sources_table.update_rows(rows)

# --- 样式定义 ---
INPUT_STYLE = 'w-full bg-black/20 rounded-lg px-3 py-2 border border-white/10 focus-within:border-cyan-500/50 transition-colors text-gray-200'
INPUT_PROPS = 'borderless dense input-class="text-white"'

def show_add_source_dialog():
    with ui.dialog() as dialog, glass_card(classes='w-96 p-6 border border-cyan-500/30 shadow-[0_0_50px_rgba(6,182,212,0.2)]'):
        with ui.row().classes('items-center gap-3 mb-6'):
            # 增加发光图标
            ui.icon('add_link').classes('text-2xl text-cyan-400 drop-shadow-[0_0_8px_rgba(34,211,238,0.8)]')
            ui.label('Add Source').classes('text-xl font-bold text-white')

        name_input = ui.input(placeholder='Name').props(INPUT_PROPS).classes(INPUT_STYLE)
        url_input = ui.input(placeholder='URL').props(INPUT_PROPS).classes(INPUT_STYLE)
        
        platform_select = ui.select(
            ['bilibili', 'xiaohongshu', 'xiaoheihe', 'coolapk'], value='bilibili'
        ).props(INPUT_PROPS).classes(INPUT_STYLE)
        
        frequency_input = ui.number(value=60, min=1, max=1440).props(INPUT_PROPS).classes(INPUT_STYLE)
        
        def add():
            try:
                new_source = create_source(
                    name=name_input.value, url=url_input.value,
                    platform=platform_select.value, frequency=int(frequency_input.value)
                )
                scheduler_manager.add_job(
                    job_id=f"scrape_source_{new_source.id}", func=scrape_source_async,
                    minutes=new_source.frequency, source_id=new_source.id
                )
                ui.notify(f'Added: {name_input.value}', type='positive', classes='glass-panel')
                refresh_table()
                dialog.close()
            except Exception as e:
                ui.notify(str(e), type='negative', classes='glass-panel')
        
        with ui.row().classes('w-full justify-end gap-3 mt-6'):
            ui.button('Cancel', on_click=dialog.close).props('flat dense no-caps').classes('text-gray-400 hover:text-white')
            ui.button('Confirm', icon='check', on_click=add).props('unelevated dense no-caps').classes('bg-cyan-600 hover:bg-cyan-500 text-white px-6 rounded-lg shadow-[0_0_15px_rgba(8,145,178,0.4)]')
    
    dialog.open()

def show_edit_source_dialog(row):
    with ui.dialog() as dialog, glass_card(classes='w-96 p-6 border border-purple-500/30'):
        with ui.row().classes('items-center gap-3 mb-4'):
            ui.icon('edit_note').classes('text-2xl text-purple-400 drop-shadow-[0_0_8px_rgba(192,132,252,0.8)]')
            ui.label('Edit Source').classes('text-xl font-bold text-white')
        
        name_input = ui.input(value=row['name'], placeholder='Name').props(INPUT_PROPS).classes(INPUT_STYLE)
        # 这里可以添加更多编辑字段
        
        ui.button('Save', icon='save', on_click=dialog.close).props('unelevated no-caps').classes('w-full mt-4 bg-purple-600 rounded-lg shadow-[0_0_15px_rgba(147,51,234,0.4)]')
    dialog.open()

def handle_delete(row):
    with ui.dialog() as dialog, glass_card(classes='p-6 border border-red-500/30 shadow-[0_0_30px_rgba(239,68,68,0.2)]'):
        with ui.row().classes('items-center gap-3 mb-2'):
            ui.icon('warning').classes('text-2xl text-red-400 drop-shadow-[0_0_8px_rgba(248,113,113,0.8)]')
            ui.label('Confirm Delete').classes('text-lg font-bold text-red-400')
        
        ui.label(f'Remove "{row["name"]}"?').classes('text-gray-300 mb-6 ml-9')
        
        with ui.row().classes('justify-end gap-3'):
            ui.button('Cancel', on_click=dialog.close).props('flat dense no-caps text-gray-400')
            def confirm():
                scheduler_manager.remove_job(f"scrape_source_{row['id']}")
                delete_source(row['id'])
                refresh_table()
                dialog.close()
            ui.button('Delete', icon='delete', on_click=confirm).props('unelevated dense no-caps bg-red-500/20 text-red-400 hover:bg-red-500 hover:text-white border border-red-500/30')
    dialog.open()

@ui.page('/sources')
def sources():
    global sources_table
    with create_main_layout('sources'):
        # Header 区域
        with ui.row().classes('items-center justify-between w-full mb-2'):
            # === 关键修复：移除了错误的 .with_content()，改为使用 with 语句 ===
            with ui.column().classes('gap-1'):
                ui.label('Source Manager').classes('text-4xl font-bold text-white drop-shadow-[0_0_10px_rgba(255,255,255,0.3)] tracking-tight')
                ui.label('Manage your content subscriptions').classes('text-sm text-gray-400 font-light tracking-wider')
            
            # 按钮增加发光图标
            with ui.row().classes('gap-3'):
                ui.button('Refresh', icon='refresh', on_click=refresh_table).props('flat dense no-caps color=purple').classes('hover:bg-purple-500/10 rounded-lg px-3')
                ui.button('Add Source', icon='add', on_click=show_add_source_dialog).props('unelevated no-caps').classes('bg-cyan-600/90 hover:bg-cyan-500 text-white border border-cyan-400/30 backdrop-blur-md rounded-xl px-4 py-2 shadow-[0_0_20px_rgba(8,145,178,0.4)] transition-all hover:scale-105')

        # 表格区域
        with glass_card(classes='p-0 overflow-hidden border-t border-white/10'):
            sources_list = get_sources()
            
            columns = [
                {'name': 'name', 'label': 'NAME', 'field': 'name', 'align': 'left'},
                {'name': 'platform', 'label': 'PLATFORM', 'field': 'platform', 'align': 'center'},
                {'name': 'status_label', 'label': 'STATUS', 'field': 'status_label', 'align': 'center'},
                {'name': 'frequency', 'label': 'FREQ (MIN)', 'field': 'frequency', 'align': 'center'},
                {'name': 'last_scraped', 'label': 'LAST RUN', 'field': 'last_scraped', 'align': 'right'},
            ]
            rows = [
                {
                    'id': s.id, 'name': s.name, 'platform': s.platform, 'url': s.url,
                    'frequency': s.frequency, 'is_active': s.is_active,
                    'status_label': 'ACTIVE' if s.is_active else 'PAUSED',
                    'last_scraped': s.last_scraped.strftime('%H:%M %m/%d') if s.last_scraped else '-'
                } for s in sources_list
            ]
            
            sources_table = enhanced_table(
                columns=columns, rows=rows,
                on_edit=show_edit_source_dialog, on_delete=handle_delete
            )
