"""Scientific context and Markdown for a captured view configuration."""
import json

import numpy as np


def validate_snapshot(snapshot, manifest_sha256):
    if not isinstance(snapshot, dict) or snapshot.get('schema') != 1:
        raise ValueError('View summary requires a schema 1 configuration snapshot')
    if snapshot.get('dataset_manifest_sha256') != manifest_sha256:
        raise ValueError('View summary snapshot belongs to a different Dataset')
    if not isinstance(snapshot.get('view'), dict) or not isinstance(snapshot.get('display'), dict):
        raise ValueError('View summary snapshot is missing view or display records')
    if not isinstance(snapshot.get('captured_at_utc'), str) or not snapshot['captured_at_utc']:
        raise ValueError('View summary snapshot is missing its capture time')
    display = snapshot['display']
    if display.get('status') not in ('captured', 'partial', 'unverified'):
        raise ValueError('Invalid view summary display status')
    for name in ('parameters', 'materials', 'reasons'):
        if not isinstance(display.get(name), list):
            raise ValueError('View summary display is missing ' + name)
    # Freeze JSON values and reject non-finite numbers before the export transaction.
    return json.loads(json.dumps(snapshot, ensure_ascii=False, allow_nan=False))


def scientific_summary(data, snapshot):
    from .geometry import scientific_geometry
    meta = data.metadata
    result = {'source': meta['source'], 'coordinate_unit': meta.get('coordinate_unit'),
              'method': meta.get('method'), 'basis_name': meta.get('basis_name'),
              'calculation_status': meta.get('calculation_status'),
              'selected_job': meta.get('selected_job'), 'fields': [], 'reasons': []}
    for name in ('method', 'basis_name', 'coordinate_unit'):
        if result[name] in (None, '', 'unknown'):
            result['reasons'].append(name + ': source record is not available')
    positions, record = scientific_geometry(data)
    result['source_geometry'] = dict(record, atom_count=len(positions))
    selection = snapshot.get('geometry_selection')
    if selection is not None:
        positions, record = scientific_geometry(data, selection['kind'], selection.get('step'))
        result['current_configuration'] = dict(record, atom_count=len(positions))
    bindings = snapshot.get('fields', {})
    for role in ('geometry', 'color'):
        binding = bindings.get(role)
        if binding is None:
            continue
        field = binding['field']
        if binding['dataset_manifest_sha256'] == snapshot['dataset_manifest_sha256']:
            if field not in meta.get('fields', []):
                raise ValueError('View summary field differs from the saved Dataset')
            source = (meta.get('analysis', {}).get(field['role'] + '_source')
                      if field.get('role') in ('geometry', 'color') else meta['source'])
            if binding.get('source') != source:
                raise ValueError('View summary field source differs from the saved Dataset')
            mask = data.arrays[field['valid_mask']]
            entry = dict(binding, role=role, sample_count=int(mask.size),
                         valid_sample_count=int(np.count_nonzero(mask)))
        else:
            if role != 'color':
                raise ValueError('Geometry field belongs to a different Dataset')
            entry = dict(binding, role=role)
            result['reasons'].append('color: arrays are held in the separately bound Dataset; valid point count is not evaluated')
        result['fields'].append(entry)
        for key in ('quantity', 'unit', 'coordinate_unit'):
            if field.get(key) in (None, '', 'unknown', 'unknown_scalar'):
                result['reasons'].append(role + ' field ' + key + ': source record is not available')
    result['status'] = 'partial' if result['reasons'] else 'captured'
    return result


def _cell(value):
    if value is None:
        return '未记录'
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\\', '\\\\').replace('|', '\\|').replace('\r', '').replace('\n', '<br>')


def render_summary(summary):
    lines = ['# QCBlender 视图参数摘要', '',
             '此摘要记录导出时读取的配置输入。内部节点组和渲染结果未求值；工程复现仍需保留 .blend 与 .qcdata。', '']
    for title, entries in (('视图与快照', summary['view']),
                           ('科学来源与参数', summary['scientific'])):
        lines.extend(['## ' + title, '', '| 项目 | 记录 |', '| --- | --- |'])
        lines.extend('| ' + _cell(key) + ' | ' + _cell(value) + ' |' for key, value in entries.items())
        lines.append('')
    lines.extend(['- 捕获时间 UTC：' + _cell(summary['captured_at_utc']),
                  '- Dataset manifest SHA-256：' + _cell(summary['dataset_manifest_sha256']), '',
                  '## 显示配置输入', '', '- 状态：' + _cell(summary['display']['status']), '',
                  '| 输入 | 类型 | 实时记录 | 读取位置 |', '| --- | --- | --- | --- |'])
    for entry in summary['display']['parameters']:
        lines.append('| ' + ' | '.join(_cell(entry.get(key)) for key in ('label', 'socket_type', 'value', 'location')) + ' |')
    lines.extend(['', '## 材质与色带配置', '', '| 材质 | 记录 |', '| --- | --- |'])
    for entry in summary['display']['materials']:
        lines.append('| ' + _cell(entry['name']) + ' | ' + _cell(entry) + ' |')
    lines.extend(['', '## 未记录或未验证项', ''])
    reasons = summary['display']['reasons'] + summary['scientific']['reasons']
    lines.extend('- ' + _cell(reason) for reason in reasons)
    if not reasons:
        lines.append('本次范围内的配置输入已捕获。内部节点组及完整渲染等效性仍未验证。')
    return '\n'.join(lines) + '\n'
