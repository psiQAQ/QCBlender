"""Workflow actions in the sidebar; persistent controls in native Properties."""
import json
import textwrap

import bpy
from bpy.props import EnumProperty

from .capabilities import action_button, record
from .source_browser import cached_metadata


def is_qc(context):
    obj = context.object
    return obj is not None and bool(obj.get('qc_view_kind') or obj.get('qc_dataset'))


def summary(layout, obj):
    layout.label(text=obj.name, icon='OBJECT_DATA')
    layout.label(text='来源: ' + obj.get('qc_source_filename', '未记录'))
    if obj.get('qc_source_job', -1) >= 0:
        layout.label(text=f"计算段 {obj['qc_source_job'] + 1}")
    field = record(obj, 'qc_field')
    if field:
        layout.label(text=f"{field.get('quantity', '未记录')} [{field.get('unit', '未记录')}]")
        layout.label(text='网格: ' + ' × '.join(map(str, field.get('shape', []))))
    color = record(obj, 'qc_color_source')
    if color:
        layout.label(text=f"着色: {color.get('quantity', '未记录')} [{color.get('unit', '未记录')}]")
    if obj.get('qc_optimization_record'):
        step = record(obj, 'qc_optimization_record')
        layout.label(text=f"优化步 {obj.get('qc_optimization_step')} / {obj.get('qc_optimization_count')}")
        if step.get('energy'):
            layout.label(text=f"{step['energy']['value_hartree']:.10f} Hartree")
    if obj.get('qc_irc'):
        step = record(obj, 'qc_irc_record')
        layout.label(text=f"IRC 步 {obj.get('qc_irc_step')} / {step.get('count', '未记录')}")
    if obj.get('qc_mode_frequency_cm-1') is not None:
        layout.label(text=f"振动 {obj.get('qc_mode_source_number')}: {obj['qc_mode_frequency_cm-1']:.4f} cm⁻¹")
    probe = record(obj, 'qc_probe')
    if probe.get('value') is not None:
        layout.label(text=f"最近采样: {probe['value']:.8g} {probe.get('unit', '')}")


class QCBLENDER_OT_open_properties(bpy.types.Operator):
    bl_idname = 'qcblender.open_properties'
    bl_label = 'Open QC Properties'
    editor: EnumProperty(items=[('OBJECT', '对象', ''), ('MATERIAL', '材质', ''),
                               ('RENDER', '渲染', ''), ('OUTPUT', '输出', '')])

    def execute(self, context):
        areas = [a for a in context.screen.areas if a.type == 'PROPERTIES']
        if not areas:
            self.report({'ERROR'}, '请先将一个编辑器切换为属性编辑器')
            return {'CANCELLED'}
        area = areas[0]
        if self.editor in ('OBJECT', 'MATERIAL'):
            area.spaces.active.pin_id = context.object
            area.spaces.active.use_pin_id = True
        area.spaces.active.context = self.editor
        area.tag_redraw()
        return {'FINISHED'}


class QCBLENDER_PT_main(bpy.types.Panel):
    bl_label = '工作流'
    bl_idname = 'QCBLENDER_PT_main'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_order = 0

    def draw(self, context):
        layout = self.layout
        layout.operator('qcblender.import_calculation', text='导入 Gaussian / Cube', icon='IMPORT')
        layout.operator('qcblender.import_irc_path', text='导入 IRC 路径')
        action_button(layout, context, 'generate', 'qcblender.generate_field', '生成量子化学场', 'VOLUME_DATA')
        if is_qc(context):
            layout.operator('qcblender.open_properties', text='对象属性与显示参数', icon='PROPERTIES').editor = 'OBJECT'


class QCBLENDER_PT_dataset(bpy.types.Panel):
    bl_label = '数据集与数值摘要'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return is_qc(context)

    def draw(self, context):
        layout = self.layout
        summary(layout, context.object)
        layout.operator('qcblender.source_details', text='查看完整来源', icon='INFO')
        layout.operator('qcblender.refresh_sources', text='刷新来源', icon='FILE_REFRESH')


class QCBLENDER_PT_create(bpy.types.Panel):
    bl_label = '创建视图与检查工具'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return is_qc(context)

    def draw(self, context):
        layout, obj = self.layout, context.object
        for action, operator, text in [
            ('surface', 'qcblender.add_surface_layer', '创建等值面层'),
            ('slice', 'qcblender.create_slice', '创建切片'),
            ('fog', 'qcblender.create_fog', '创建体积雾'),
            ('clip', 'qcblender.add_clipping', '添加裁剪控件'),
            ('probe', 'qcblender.probe_field', '读取游标处场值'),
            ('profile_start', 'qcblender.mark_profile_start', '记录剖面起点'),
            ('profile', 'qcblender.create_line_profile', '创建线剖面'),
            ('dipole', 'qcblender.show_dipole', '创建偶极矢量')]:
            action_button(layout, context, action, operator, text)
        if obj.get('qc_view_kind') == 'atoms':
            layout.operator('qcblender.local_selection_layer', text='创建局部显示层')
            for kind, title in [('ATOM', '编号标注'), ('DISTANCE', '距离标注'),
                                ('ANGLE', '角度标注'), ('DIHEDRAL', '二面角标注')]:
                layout.operator('qcblender.add_annotation', text='创建' + title).kind = kind
            if obj.get('qc_optimization_available') and not obj.get('qc_optimization_step'):
                layout.operator('qcblender.optimization_view', text='创建优化轨迹视图')
        if obj.get('qc_view_kind') == 'profile':
            layout.operator('qcblender.export_line_profile', text='导出剖面 CSV', icon='EXPORT')
        layout.operator('qcblender.new_current_view', text='创建当前版本视图')
        layout.operator('qcblender.create_framed_camera', text='创建取景相机', icon='CAMERA_DATA')


class QCBLENDER_PT_external_import(bpy.types.Panel):
    bl_label = '导入外部结果'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return context.object is not None and bool(context.object.get('qc_dataset'))

    def draw(self, context):
        for action, operator, text in [
            ('paired', 'qcblender.import_paired_field', 'IGMH / IRI 成对场'),
            ('nbo', 'qcblender.import_nbo', 'NBO 记录'),
            ('esp', 'qcblender.import_esp_analysis', 'ESP 表面分析'),
            ('aim', 'qcblender.import_aim_analysis', 'AIM 拓扑'),
            ('nocv_table', 'qcblender.import_ets_nocv', 'ETS-NOCV 表'),
            ('nocv_field', 'qcblender.import_nocv_field', 'NOCV pair Cube')]:
            action_button(self.layout, context, action, operator, text)


class QCBLENDER_PT_project(bpy.types.Panel):
    bl_label = '工程与诊断'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'QCBlender'
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 5

    def draw(self, context):
        layout = self.layout
        for operator, text in [('save_project', '保存自包含工程'), ('archive_project', '归档工程'),
                               ('rebuild_cache', '重建显示缓存'), ('relocate_dataset', '重新定位数据'),
                               ('cleanup_legacy_node_assets', '预览并整理旧 QC 节点资产'),
                               ('check_runtime', '检查科学运行环境')]:
            layout.operator('qcblender.' + operator, text=text)
        obj = context.object
        if obj is not None:
            for diagnostic in json.loads(obj.get('qc_diagnostics', '[]')):
                for line in textwrap.wrap(diagnostic, width=40):
                    layout.label(text=line)


class QCBLENDER_PT_object(bpy.types.Panel):
    bl_label = 'QCBlender · 对象与量子化学'
    bl_idname = 'QCBLENDER_PT_object'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'

    @classmethod
    def poll(cls, context):
        return is_qc(context)

    def draw(self, context):
        summary(self.layout, context.object)
        self.layout.operator('qcblender.source_details', text='来源详情', icon='INFO')
        self.layout.operator('qcblender.refresh_sources', text='刷新来源')
        self.layout.operator('qcblender.associate_sources', text='关联选中数据源')
        action_button(self.layout, context, 'declare', 'qcblender.declare_field', '声明 Cube 物理量与单位')


class QCBLENDER_PT_scientific(bpy.types.Panel):
    bl_label = '科学记录与振动模式'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        obj, layout = context.object, self.layout
        settings = obj.qc_settings
        meta = cached_metadata(obj)
        if not meta or 'error' in meta:
            layout.label(text=meta.get('error', '请刷新来源记录'), icon='INFO')
            return
        layout.label(text='计算状态: ' + meta.get('calculation_status', '未记录'))
        field = record(obj, 'qc_field')
        if field.get('steps'):
            layout.label(text='源网格步矢 [Å]，只读')
            for axis, step in zip('ijk', field['steps']):
                layout.label(text=axis + ': ' + ', '.join(f'{v:.6g}' for v in step))
        orbital = field.get('orbital')
        if isinstance(orbital, dict):
            for key in ('spin', 'source_number', 'occupation', 'energy_hartree'):
                layout.label(text=f"{key}: {orbital.get(key, '未记录')}")
        if settings.energies:
            layout.template_list('QCBLENDER_UL_energies', '', settings, 'energies', settings, 'active_energy', rows=3)
            if 0 <= settings.active_energy < len(settings.energies):
                energy = json.loads(settings.energies[settings.active_energy].record)
                layout.label(text=f"{energy['value_hartree']:.10f} Hartree")
                layout.label(text=f"{energy['method']} / {energy['kind']}")
        if settings.modes:
            layout.template_list('QCBLENDER_UL_modes', '', settings, 'modes', settings, 'active_mode', rows=4)
        if obj.get('qc_view_kind') == 'atoms':
            action_button(layout, context, 'charge', 'qcblender.color_charge', '设置原子电荷着色')


class _ObjectSection:
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not is_qc(context):
            return False
        from .ui import parameter_section_available
        return parameter_section_available(context.object, cls.bl_label)

    def draw(self, context):
        from .ui import draw_view_parameters
        draw_view_parameters(self.layout, context.object, self.bl_label)


class QCBLENDER_PT_geometry(_ObjectSection, bpy.types.Panel):
    bl_label = '几何表示'


class QCBLENDER_PT_mapping(_ObjectSection, bpy.types.Panel):
    bl_label = '颜色映射'


class QCBLENDER_PT_legend(_ObjectSection, bpy.types.Panel):
    bl_label = '图例排版'


class QCBLENDER_PT_spatial(_ObjectSection, bpy.types.Panel):
    bl_label = '空间观察'


class QCBLENDER_PT_advanced(_ObjectSection, bpy.types.Panel):
    bl_label = '高级参数'


class QCBLENDER_PT_selection(bpy.types.Panel):
    bl_label = '局部选择与标注'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'object'
    bl_parent_id = 'QCBLENDER_PT_object'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.get('qc_view_kind') == 'atoms'

    def draw(self, context):
        layout, obj = self.layout, context.object
        layout.operator('qcblender.local_selection', text='设置局部选择')
        selected = record(obj, 'qc_local_selection_record')
        if selected:
            layout.label(text='固定源编号: ' + ','.join(map(str, selected.get('fixed_numbers', []))))
            layout.operator('qcblender.local_selection', text='按当前步重新计算').mode = 'RECOMPUTE'
            layout.operator('qcblender.local_selection', text='清除局部限制').mode = 'CLEAR'
        row = layout.row(align=True)
        for mode, label in [('HIDE', '隐藏氢'), ('KEEP', '保留指定氢'), ('RESTORE', '显示全部氢')]:
            row.operator('qcblender.hydrogen_visibility', text=label).mode = mode
        from .annotations import draw_annotations
        draw_annotations(layout, context)


class QCBLENDER_PT_material(bpy.types.Panel):
    bl_label = 'QCBlender · 节点材质'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'material'
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        from .ui import parameter_section_available
        return is_qc(context) and parameter_section_available(context.object, '材质')

    def draw(self, context):
        from .ui import draw_view_parameters
        self.layout.label(text='材质节点可在着色器编辑器中独立修改')
        draw_view_parameters(self.layout, context.object, '材质')


class QCBLENDER_MT_object(bpy.types.Menu):
    bl_label = 'QCBlender'

    def draw(self, context):
        layout = self.layout
        layout.operator('qcblender.source_details', text='来源详情')
        layout.operator('qcblender.open_properties', text='对象属性').editor = 'OBJECT'
        action_button(layout, context, 'slice', 'qcblender.create_slice', '创建切片')
        action_button(layout, context, 'probe', 'qcblender.probe_field', '读取游标处场值')
        layout.operator('qcblender.create_framed_camera', text='创建取景相机')
        if context.object.get('qc_view_kind') in ('atoms', 'field', 'slice', 'fog'):
            layout.operator('qcblender.copy_display_parameters', text='复制显示参数到选中视图')


def object_context_menu(self, context):
    if is_qc(context):
        self.layout.menu('QCBLENDER_MT_object')
