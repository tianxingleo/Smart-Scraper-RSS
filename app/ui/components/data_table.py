"""增强的数据表格组件"""
from nicegui import ui
from typing import List, Dict, Callable, Optional

def enhanced_table(
    columns: List[Dict],
    rows: List[Dict],
    on_edit: Optional[Callable] = None,
    on_delete: Optional[Callable] = None,
    on_action: Optional[Callable] = None,
    action_label: str = 'ACTIONS'
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
            {'name': 'actions', 'label': action_label, 'field': 'actions', 'align': 'center'}
        ]
    else:
        columns_with_actions = columns
    
    table = ui.table(
        columns=columns_with_actions,
        rows=rows,
        row_key='id',
        pagination=10
    ).classes('w-full glass-panel rounded-2xl overflow-hidden')
    
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
        table.add_slot('body-cell-actions', r'''
            <q-td key="actions" :props="props">
                <div class="flex gap-2 justify-center">
        ''' + 
        (f'''<q-btn flat dense size="sm" color="purple" label="Edit" @click="$parent.$emit('edit', props.row)" />''' if on_edit else '') +
        (f'''<q-btn flat dense size="sm" color="red" label="Delete" @click="$parent.$emit('delete', props.row)" />''' if on_delete else '') +
        (f'''<q-btn flat dense size="sm" color="cyan" label="{action_label}" @click="$parent.$emit('action', props.row)" />''' if on_action else '') +
        '''
                </div>
            </q-td>
        ''')
        
        # 绑定事件
        if on_edit:
            table.on('edit', lambda e: on_edit(e.args))
        if on_delete:
            table.on('delete', lambda e: on_delete(e.args))
        if on_action:
            table.on('action', lambda e: on_action(e.args))
    
    return table
