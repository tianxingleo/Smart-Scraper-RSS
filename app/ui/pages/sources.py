"""Sources 源管理页面"""
from nicegui import ui
from app.ui.layout import create_main_layout
from app.database.crud import create_source, get_sources, delete_source
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
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('添加新源').classes('text-xl font-bold mb-4')
        
        name_input = ui.input('源名称', placeholder='例如：我的 B 站收藏').classes('w-full')
        url_input = ui.input('URL', placeholder='https://...').classes('w-full')
        platform_select = ui.select(
            ['bilibili', 'xiaohongshu'],
            label='平台',
            value='bilibili'
        ).classes('w-full')
        frequency_input = ui.number(
            '抓取频率（分钟）',
            value=60,
            min=1,
            max=1440
        ).classes('w-full')
        
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
        
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close, color='grey')
            ui.button('添加', on_click=add, color='primary')
    
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
    
    with ui.dialog() as delete_dialog, ui.card():
        ui.label('确认删除？').classes('text-lg font-bold mb-4')
        ui.label(f'确定要删除源 "{row["name"]}" 吗？').classes('mb-4')
        
        with ui.row().classes('gap-2'):
            ui.button('取消', on_click=delete_dialog.close, color='grey')
            ui.button('确认删除', on_click=confirm_delete, color='negative')
    
    delete_dialog.open()

@ui.page('/sources')
def sources():
    """源管理页面"""
    global sources_table
    
    with create_main_layout('sources'):
        ui.label('🔗 源管理').classes('text-3xl font-bold mb-6')
        
        # 工具栏
        with ui.row().classes('gap-4 mb-4'):
            ui.button('添加源', on_click=show_add_source_dialog, color='primary').props('icon=add')
            ui.button('刷新', on_click=refresh_table, color='secondary').props('icon=refresh')
        
        # 源列表表格
        with ui.card().classes('w-full p-4'):
            sources_list = get_sources()
            
            columns = [
                {'name': 'id', 'label': 'ID', 'field': 'id', 'align': 'left'},
                {'name': 'name', 'label': '名称', 'field': 'name', 'align': 'left'},
                {'name': 'platform', 'label': '平台', 'field': 'platform', 'align': 'center'},
                {'name': 'url', 'label': 'URL', 'field': 'url', 'align': 'left'},
                {'name': 'frequency', 'label': '频率(分)', 'field': 'frequency', 'align': 'center'},
                {'name': 'is_active', 'label': '状态', 'field': 'is_active', 'align': 'center'},
                {'name': 'last_scraped', 'label': '最后抓取', 'field': 'last_scraped', 'align': 'center'},
                {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'},
            ]
            
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
                for s in sources_list
            ]
            
            sources_table = ui.table(columns=columns, rows=rows, row_key='id').classes('w-full')
            
            # 添加操作列
            sources_table.add_slot('body-cell-actions', '''
                <q-td :props="props">
                    <q-btn size="sm" flat dense color="negative" label="删除" 
                           @click="$parent.$emit('delete', props.row)" />
                </q-td>
            ''')
            
            # 监听删除事件
            sources_table.on('delete', handle_delete)
