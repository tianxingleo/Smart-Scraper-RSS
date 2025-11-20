"""Sources 源管理页面 - 液态玻璃版"""
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

# --- 通用样式定义 ---
INPUT_STYLE = 'w-full bg-black/20 rounded-lg px-3 py-2 border border-white/10 focus-within:border-cyan-500/50 transition-colors text-gray-200'
INPUT_PROPS = 'borderless dense input-class="text-white"'

def show_add_source_dialog():
    # 玻璃弹窗
    with ui.dialog() as dialog, glass_card(classes='w-96 p-6 border border-cyan-500/30 shadow-[0_0_50px_rgba(6,182,212,0.2)]'):
        with ui.row().classes('items-center gap-3 mb-6'):
            ui.icon('add_link').classes('text-2xl text-cyan-400')
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
                ui.notify(f'Added: {name_input.value}', type='positive')
                refresh_table()
                dialog.close()
            except Exception as e:
                ui.notify(str(e), type='negative')
        
        with ui.row().classes('w-full justify-end gap-3 mt-6'):
            ui.button('Cancel', on_click=dialog.close).props('flat dense no-caps').classes('text-gray-400 hover:text-white')
            ui.button('Confirm', on_click=add).props('unelevated dense no-caps').classes('bg-cyan-600 hover:bg-cyan-500 text-white px-6 rounded-lg shadow-[0_0_15px_rgba(8,145,178,0.4)]')
    
    dialog.open()

def show_edit_source_dialog(row):
    # 编辑逻辑
    with ui.dialog() as dialog, glass_card(classes='w-96 p-6 border border-purple-500/30'):
        ui.label('Edit Source').classes('text-xl font-bold text-white mb-4')
        
        name_input = ui.input(value=row['name'], placeholder='Name').props(INPUT_PROPS).classes(INPUT_STYLE)
        # 简化展示，实际应包含更多字段编辑
        
        ui.button('Save', on_click=dialog.close).props('unelevated no-caps').classes('w-full mt-4 bg-purple-600 rounded-lg')
    dialog.open()

def handle_delete(row):
    with ui.dialog() as dialog, glass_card(classes='p-6 border border-red-500/30'):
        ui.label('Confirm Delete').classes('text-lg font-bold text-red-400 mb-2')
        ui.label(f'Remove "{row["name"]}"?').classes('text-gray-300 mb-6')
        with ui.row().classes('justify-end gap-3'):
            ui.button('Cancel', on_click=dialog.close).props('flat dense no-caps text-gray-400')
            def confirm():
                scheduler_manager.remove_job(f"scrape_source_{row['id']}")
                delete_source(row['id'])
                refresh_table()
                dialog.close()
            ui.button('Delete', on_click=confirm).props('unelevated dense no-caps bg-red-500/20 text-red-400 hover:bg-red-500 hover:text-white')
    dialog.open()

@ui.page('/sources')
def sources():
    global sources_table
    with create_main_layout('sources'):
        with ui.row().classes('items-center justify-between w-full mb-2'):
            ui.column().classes('gap-0').with_content(
                ui.label('Source Manager').classes('text-4xl font-bold text-white drop-shadow-lg'),
                ui.label('Manage your content subscriptions').classes('text-sm text-gray-400 font-light')
            )
            ui.button('Add Source', icon='add', on_click=show_add_source_dialog).props('unelevated no-caps').classes('bg-white/10 hover:bg-white/20 text-white border border-white/20 backdrop-blur-md rounded-xl px-4 py-2 transition-all hover:scale-105')

        # 表格区域 - 使用 glass_card 包裹 table
        with glass_card(classes='p-0 overflow-hidden'): # p-0 让表格贴边
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
                    'status_label': 'ACTIVE' if s.is_active else 'STOPPED',
                    'last_scraped': s.last_scraped.strftime('%H:%M %b %d') if s.last_scraped else '-'
                } for s in sources_list
            ]
            
            # 调用 enhanced_table (已修改为透明)
            sources_table = enhanced_table(
                columns=columns, rows=rows,
                on_edit=show_edit_source_dialog, on_delete=handle_delete
            )
