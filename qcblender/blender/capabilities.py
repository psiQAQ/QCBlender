"""Context eligibility shared by controls and operators; never read source files."""
import json

from .source_browser import cached_metadata


def record(obj, key):
    try:
        value = json.loads(obj.get(key, '{}')) if obj is not None else {}
        return value if isinstance(value, dict) else {}
    except (ValueError, TypeError):
        return {}


def capability(context, action):
    """Return (applicable, enabled, reason) from the saved view and cached metadata."""
    obj = context.object
    kind = obj.get('qc_view_kind', '') if obj is not None else ''
    meta = cached_metadata(obj)
    field = record(obj, 'qc_field')
    atoms = kind == 'atoms'
    scalar = kind in ('field', 'slice', 'fog')
    bound = obj is not None and bool(obj.get('qc_dataset'))
    if action == 'generate':
        relevant, ready, reason = bound, 'orbitals' in meta, '源数据缺少轨道系数；如尚未读取来源请刷新'
    elif action == 'charge':
        relevant, ready, reason = atoms, bool(meta.get('charges')), '源数据未记录原子电荷'
        if ready:
            from .graph import view_modifier
            try:
                ready = not view_modifier(obj).node_group.get('qc_color_mapping')
                reason = '此视图已绑定着色场；请使用独立原子显示层'
            except ValueError as error:
                ready, reason = False, str(error)
    elif action == 'dipole':
        relevant, ready, reason = atoms, bool(meta.get('dipole')), '源数据未记录分子偶极矩'
    elif action == 'declare':
        relevant = scalar and field.get('quantity') == 'unknown_scalar'
        ready, reason = bool(field), '场记录缺失'
    elif action in ('slice', 'fog', 'surface'):
        relevant, ready, reason = scalar, bool(field), '缺少标量场记录'
    elif action in ('profile', 'profile_start', 'probe_click'):
        relevant = kind in ('field', 'slice')
        ready, reason = bool(field), '缺少标量场记录'
        if action == 'profile' and relevant and not obj.get('qc_profile_start'):
            ready, reason = False, '请先在此显示层记录剖面起点'
    elif action == 'probe':
        relevant = scalar or (atoms and obj.qc_settings.volume is not None)
        ready, reason = obj is not None and obj.qc_settings.volume is not None, '关联体场缺失'
    elif action == 'clip':
        relevant, ready, reason = atoms or scalar, True, ''
        if relevant:
            from .graph import view_modifier
            try:
                ready = not view_modifier(obj).node_group.get('qc_clipping')
                reason = '已有裁剪；请在对象属性的空间观察中调整'
            except ValueError as error:
                ready, reason = False, str(error)
    elif action == 'esp':
        relevant = field.get('quantity') == 'electrostatic_potential' or record(obj, 'qc_color_source').get('quantity') == 'electrostatic_potential'
        ready = field.get('quantity') == 'electrostatic_potential'
        reason = '请选择实际 ESP 字段视图作为导入参考'
    elif action in ('aim', 'paired', 'nbo', 'nocv_table'):
        relevant, ready, reason = bound, bool(meta.get('source')), '请先刷新来源记录'
    elif action == 'nocv_field':
        relevant = obj is not None and obj.get('qc_analysis_role') == 'ets_nocv'
        ready, reason = bool(meta.get('analysis', {}).get('pairs')), '缺少已计算的 NOCV pair 表'
    elif action == 'atoms':
        relevant, ready, reason = atoms, atoms, '请选择 QC 原子视图'
    elif action == 'result_scatter':
        relevant = kind == 'scatter' or (obj is not None and obj.get('qc_analysis_role') == 'paired')
        ready, reason = len(meta.get('fields', [])) == 2, '配对场来源缺失；请刷新来源'
    elif action == 'result_filter':
        relevant = kind == 'nbo' or (obj is not None and obj.get('qc_analysis_role') in
            ('esp_maximum', 'esp_minimum', 'esp_area', 'aim_C', 'aim_N', 'aim_O', 'aim_F', 'ets_nocv'))
        ready, reason = bool(meta.get('analysis')), '分析记录缺失；请刷新来源'
    else:
        raise ValueError('Unknown QC action: ' + action)
    if relevant and action in ('aim', 'paired', 'nbo', 'nocv_table', 'esp', 'nocv_field'):
        from .static_reference import cached_reference_reason
        static_reason = cached_reference_reason(obj, cached_metadata)
        if static_reason:
            ready, reason = False, static_reason
    if relevant and not bound:
        ready, reason = False, '数据集关联缺失；请恢复数据来源'
    if relevant and bound and 'error' in meta:
        ready, reason = False, meta['error']
    if relevant and obj.mode != 'OBJECT':
        ready, reason = False, '请切换到物体模式'
    if relevant and ready and (action in ('slice', 'fog', 'surface', 'profile', 'profile_start', 'probe_click') or action == 'probe'):
        volume = obj.qc_settings.volume
        if volume is None or not volume.get('qc_field'):
            ready, reason = False, '关联体场缺失；请恢复数据来源'
        elif field and record(volume, 'qc_field') != field:
            ready, reason = False, '显示层与关联体场身份不同'
        elif field and (volume.get('qc_dataset_sha256') != obj.get('qc_dataset_sha256') or
                        volume.get('qc_source_sha256') != obj.get('qc_source_sha256')):
            ready, reason = False, '显示层与体场来源摘要不同'
    return bool(relevant), bool(relevant and ready), reason if relevant and not ready else ''


def poll_action(cls, context, action):
    relevant, enabled, reason = capability(context, action)
    if not enabled:
        cls.poll_message_set(reason or '当前对象不适用此操作')
    return enabled


def action_button(layout, context, action, operator, text, icon='NONE'):
    relevant, enabled, reason = capability(context, action)
    if not relevant:
        return
    row = layout.row()
    row.enabled = enabled
    row.operator(operator, text=text, icon=icon)
    if reason:
        layout.label(text=reason, icon='INFO')
