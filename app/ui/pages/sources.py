"""Sources 源管理页面"""
from nicegui import ui
from sqlmodel import Session
from app.ui.layout import create_main_layout
from app.database.crud import create_source, get_sources, delete_source, engine
from app.database.models import Source
from app.core import scheduler_manager
from app.services.scraper_service import scrape_source_async

# 全局状态
sources_table = None

def refresh_table():
    """刷新源列表表格"""
    global sources_table
    if sources_table:
        sources = get_sources()
        rows = [
            {
                'id': s.id,
                'name': s.name,
                'platform': s.platform,
                'url': s.url[:40] + '...' if len(s.url) > 40 else s.url,
                'frequency': s.frequency,
                'is_active': '启用' if s.is_active else '禁用',
                'last_scraped': s.last_scraped.strftime('%Y-%m-%d %H:%M') if s.last_scraped else '从未'
            }
            for s in sources
        ]
        sources_table.update_rows(rows)

def show_add_source_dialog():
    """显示添加源对话框"""
    # 弹窗背景也用 glass-panel，加深一点背景色以遮挡下层内容
    with ui.dialog() as dialog, ui.card().classes('w-96 glass-panel bg-[#0f172a]/80 border border-cyan-500/30 backdrop-blur-xl'):
        with ui.row().classes('w-full items-center justify-between mb-6'):
            ui.label('添加数据源').classes('text-lg font-mono font-bold text-cyan-300 tracking-wider')
            ui.icon('add_link').classes('text-cyan-500')
        
        # 统一样式 Props
        input_props = 'dark outlined dense'
        input_class = 'w-full'

        name_input = ui.input('源名称').props(input_props).classes(input_class)
        url_input = ui.input('目标 URL').props(input_props).classes(input_class)
        
        platform_select = ui.select(
            ['bilibili', 'xiaohongshu', 'xiaoheihe', 'coolapk'],
            label='平台',
            value='bilibili'
        ).props(input_props).classes(input_class)
        
        frequency_input = ui.number(
            '抓取频率 (分钟)',
            value=60, min=1, max=1440
        ).props(input_props).classes(input_class)
        
        def add():
            try:
                new_source = create_source(
                    name=name_input.value,
                    url=url_input.value,
                    platform=platform_select.value,
                    frequency=int(frequency_input.value)
                )
                
                # 添加到调度器（使用真实的抓取函数）
                scheduler_manager.add_job(
                    job_id=f"scrape_source_{new_source.id}",
                    func=scrape_source_async,
                    minutes=new_source.frequency,
                    source_id=new_source.id
                )
                
                ui.notify(f'已添加源: {name_input.value}', type='positive')
                refresh_table()
                dialog.close()
            except Exception as e:
                ui.notify(f'添加失败: {str(e)}', type='negative')
        
        # 按钮样式
        with ui.row().classes('w-full justify-end gap-3 mt-6'):
            ui.button('取消', on_click=dialog.close).props('flat color=grey').classes('font-mono')
            # 发光按钮
            ui.button('确认添加', on_click=add).props('unelevated').classes('bg-cyan-600 hover:bg-cyan-500 text-white font-bold font-mono shadow-[0_0_15px_rgba(8,145,178,0.4)] transition-all')
    
    dialog.open()

def show_edit_source_dialog(row):
    """显示编辑源对话框"""
    source_id = row['id']
    
    with ui.dialog() as dialog, ui.card().classes('w-96 glass-panel bg-[#0f172a]/90 border border-purple-500/30'):
        with ui.row().classes('w-full items-center justify-between mb-4'):
            ui.label('编辑数据源').classes('text-lg font-mono font-bold text-purple-300 tracking-wider')
            ui.icon('edit_note').classes('text-purple-500')
            
        # 统一样式
        input_props = 'dark outlined dense'
        
        name_input = ui.input('源名称', value=row['name']).props(input_props).classes('w-full')
        url_input = ui.input('URL', value=row['url_full'] if 'url_full' in row else row['url']).props(input_props).classes('w-full') 
        
        frequency_input = ui.number(
            '抓取频率 (分钟)', 
            value=row['frequency'], min=1, max=1440
        ).props(input_props).classes('w-full')
        
        is_active_switch = ui.switch('启用自动抓取', value=row['is_active']).props('color=cyan')

        def save():
            try:
                with Session(engine) as session:
                    source = session.get(Source, source_id)
                    if source:
                        source.name = name_input.value
                        source.url = url_input.value
                        source.frequency = int(frequency_input.value)
                        source.is_active = is_active_switch.value
                        session.add(source)
                        session.commit()
                        
                        # 更新调度器
                        job_id = f"scrape_source_{source.id}"
                        if source.is_active:
                            scheduler_manager.add_job(
                                job_id=job_id,
                                func=scrape_source_async,
                                minutes=source.frequency,
                                source_id=source.id
                            )
                        else:
                            scheduler_manager.remove_job(job_id)
                            
                        ui.notify(f'Source updated: {source.name}', type='positive')
                        refresh_table()
                        dialog.close()
            except Exception as e:
                ui.notify(f'Update failed: {str(e)}', type='negative')

        with ui.row().classes('w-full justify-end gap-3 mt-6'):
            ui.button('取消', on_click=dialog.close).props('flat color=grey')
            ui.button('保存修改', on_click=save).props('unelevated').classes('bg-purple-600 hover:bg-purple-500 text-white font-bold font-mono')
    
    dialog.open()

def handle_delete(row):
    """处理删除源"""
    source_id = row['id']
    
    def confirm_delete():
        try:
            # 从调度器移除
            scheduler_manager.remove_job(f"scrape_source_{source_id}")
            
            # 从数据库删除
            delete_source(source_id)
            
            ui.notify('已删除源', type='positive')
            refresh_table()
            delete_dialog.close()
        except Exception as e:
            ui.notify(f'删除失败: {str(e)}', type='negative')
    
    with ui.dialog() as delete_dialog, ui.card().classes('glass-panel border border-red-500/30'):
        ui.label('确认删除？').classes('text-lg font-bold mb-4 text-red-200')
        ui.label(f'确定要删除数据源 "{row["name"]}" 吗？').classes('mb-4 text-gray-300')
        
        with ui.row().classes('gap-2'):
            ui.button('取消', on_click=delete_dialog.close, color='grey').props('flat')
            ui.button('确认删除', on_click=confirm_delete, color='red').props('unelevated')
    
    delete_dialog.open()

@ui.page('/sources')
def sources():
    """源管理页面"""
    global sources_table
    
    with create_main_layout('sources'):
        with ui.row().classes('items-center justify-between w-full mb-6'):
            ui.label('数据源管理').classes('text-3xl font-mono font-bold text-white')
            
            with ui.row().classes('gap-4'):
                ui.button('刷新', on_click=refresh_table,color='purple').props('icon=refresh outline flat')
                ui.button('添加数据源', on_click=show_add_source_dialog).props('icon=add unelevated').classes('bg-cyan-600 hover:bg-cyan-500 text-white font-bold shadow-[0_0_15px_rgba(8,145,178,0.4)]')
        
        # 源列表表格
        sources_list = get_sources()
        
        columns = [
            {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True, 'align': 'left'},
            {'name': 'name', 'label': '名称', 'field': 'name', 'sortable': True, 'align': 'left'},
            {'name': 'platform', 'label': '平台', 'field': 'platform', 'sortable': True, 'align': 'center'},
            {'name': 'frequency', 'label': '频率(分)', 'field': 'frequency', 'sortable': True, 'align': 'center'},
            {'name': 'status_label', 'label': '状态', 'field': 'status_label', 'sortable': True, 'align': 'center'},
            {'name': 'last_scraped', 'label': '最后运行', 'field': 'last_scraped', 'sortable': True, 'align': 'right'},
        ]
        
        rows = [
            {
                'id': s.id,
                'name': s.name,
                'platform': s.platform,
                'url': s.url[:40] + '...' if len(s.url) > 40 else s.url,
                'url_full': s.url,  # 保留完整URL用于编辑
                'frequency': s.frequency,
                'is_active': s.is_active,  # Keep boolean for logic
                'status_label': '✅ 运行中' if s.is_active else '❌ 已禁用',
                'last_scraped': s.last_scraped.strftime('%Y-%m-%d %H:%M') if s.last_scraped else '从未运行'
            }
            for s in sources_list
        ]
        
        from app.ui.components.data_table import enhanced_table
        sources_table = enhanced_table(
            columns=columns, 
            rows=rows,
            on_edit=show_edit_source_dialog,  # 绑定编辑事件
            on_delete=handle_delete,
        )
