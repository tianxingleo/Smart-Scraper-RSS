"""增强的数据表格组件"""
from nicegui import ui
from typing import List, Dict, Callable, Optional

def enhanced_table(
    columns: List[Dict],
    rows: List[Dict],
    on_edit: Optional[Callable] = None,
    on_delete: Optional[Callable] = None,
    on_action: Optional[Callable] = None,
    action_label: str = '操作'
):
    """
    创建增强的数据表格
    
    Args:
        columns: 列定义
        rows: 数据行
        on_edit: 编辑回调函数
        on_delete: 删除回调函数
        on_action: 自定义操作回调
        action_label: 操作按钮标签
    
    Returns:
        table 对象
    """
    # 添加操作列
    if on_edit or on_delete or on_action:
        columns_with_actions = columns + [
            {'name': 'actions', 'label': '操作', 'field': 'actions', 'align': 'center'}
        ]
    else:
        columns_with_actions = columns
    
    table = ui.table(
        columns=columns_with_actions,
        rows=rows,
        row_key='id',
        pagination=10
    ).classes('w-full glass-panel rounded-2xl overflow-hidden') # 应用玻璃类
    
    # 关键：使用 props 强制 Quasar 表格透明并使用深色模式
    table.props('flat bordered dark')
    
    # 自定义表头颜色 (Tailwind)
    table.add_slot('header', r'''
        <q-tr :props="props" class="bg-white/5 text-cyan-300 font-bold uppercase text-xs tracking-wider">
            <q-th v-for="col in props.cols" :key="col.name" :props="props">
                {{ col.label }}
            </q-th>
        </q-tr>
    ''')
    
    # 添加操作按钮槽
    if on_edit or on_delete or on_action:
        def create_action_buttons(row):
            with ui.row().classes('gap-2'):
                if on_action:
                    ui.button(action_label, on_click=lambda r=row: on_action(r)).classes('text-xs').props('flat color=primary')
                if on_edit:
                    ui.button('编辑', on_click=lambda r=row: on_edit(r)).classes('text-xs').props('flat color=primary')
                if on_delete:
                    ui.button('删除', on_click=lambda r=row: on_delete(r)).classes('text-xs').props('flat color=negative')
        
        table.add_slot('body-cell-actions', '''
            <q-td key="actions" :props="props">
                <div id="actions-container"></div>
            </q-td>
        ''')
    
    return table
