"""增强的数据表格组件 - 透明版"""
from nicegui import ui
from typing import List, Dict, Callable, Optional

def enhanced_table(
    columns: List[Dict],
    rows: List[Dict],
    on_edit: Optional[Callable] = None,
    on_delete: Optional[Callable] = None,
    on_action: Optional[Callable] = None,
    action_label: str = 'ACTION'
):
    """
    透明数据表格 (需放置在 glass_card 中)
    """
    # 添加操作列
    if on_edit or on_delete or on_action:
        columns_with_actions = columns + [
            {'name': 'actions', 'label': '', 'field': 'actions', 'align': 'right'}
        ]
    else:
        columns_with_actions = columns
    
    table = ui.table(
        columns=columns_with_actions,
        rows=rows,
        row_key='id',
        pagination=10
    ).classes('w-full bg-transparent border-none') # 关键：全透明
    
    # 深度定制 Quasar 表格样式
    table.props('flat dark :rows-per-page-options="[10, 20]"')
    
    # 自定义表头：半透明白色背景条 + 发光文字
    table.add_slot('header', r'''
        <q-tr :props="props" class="bg-white/5 border-b border-white/10 text-cyan-400 font-bold text-[10px] tracking-[0.1em]">
            <q-th v-for="col in props.cols" :key="col.name" :props="props" class="opacity-80">
                {{ col.label }}
            </q-th>
        </q-tr>
    ''')
    
    # 自定义单元格：Hover 高亮
    table.add_slot('body', r'''
        <q-tr :props="props" class="hover:bg-white/5 transition-colors border-b border-white/5 text-gray-300 font-light text-sm">
            <q-td v-for="col in props.cols" :key="col.name" :props="props">
                <div v-if="col.name !== 'actions'">{{ col.value }}</div>
                <div v-else class="flex gap-2 justify-end">
                    ''' + 
                    (f'''<q-btn flat round dense size="sm" icon="edit" color="purple-300" class="opacity-60 hover:opacity-100" @click="$parent.$emit('edit', props.row)" />''' if on_edit else '') +
                    (f'''<q-btn flat round dense size="sm" icon="delete" color="red-400" class="opacity-60 hover:opacity-100" @click="$parent.$emit('delete', props.row)" />''' if on_delete else '') +
                    '''
                </div>
            </q-td>
        </q-tr>
    ''')

    # 绑定事件
    if on_edit: table.on('edit', lambda e: on_edit(e.args))
    if on_delete: table.on('delete', lambda e: on_delete(e.args))
    if on_action: table.on('action', lambda e: on_action(e.args))
    
    return table
