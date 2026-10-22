"""Properties-to-viewport boundaries with real operator methods and fake bpy I/O."""
import ast
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


class Object(dict):
    def __init__(self, name, **values):
        super().__init__(values)
        self.name = name
        self.modifiers = []
        self.matrix_world = ((1., 0.), (0., 1.))
        self.hidden = False

    def hide_get(self):
        return self.hidden

    def update_tag(self):
        pass


class Operator:
    messages = []

    @classmethod
    def poll_message_set(cls, message):
        cls.messages.append(message)

    def report(self, levels, message):
        self.messages.append(message)


class Area:
    def __init__(self, name, kind='VIEW_3D', width=600, height=400, x=0):
        self.name, self.type, self.width, self.height = name, kind, width, height
        self.region = SimpleNamespace(type='WINDOW', x=x, y=0, width=width, height=height)
        rotation = SimpleNamespace(copy=lambda: rotation,
                                   to_matrix=lambda: SimpleNamespace(col=((1, 0, 0), (0, 1, 0), (0, 0, 1))))
        self.view = SimpleNamespace(view_rotation=rotation)
        self.spaces = SimpleNamespace(active=SimpleNamespace(region_3d=self.view,
                                      use_pin_id=False, pin_id=None))
        self.regions = [self.region]
        self.redraws = 0

    def tag_redraw(self):
        self.redraws += 1


def load_helper(bpy):
    name = 'qcblender.blender._property_viewport_test'
    spec = importlib.util.spec_from_file_location(name, ROOT / 'qcblender/blender/viewport_context.py')
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'bpy': bpy, name: module}):
        spec.loader.exec_module(module)
    return module


def operator_class(filename, name, namespace):
    tree = ast.parse((ROOT / 'qcblender/blender' / filename).read_text(encoding='utf-8'))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name)
    exec(compile(ast.Module(body=[cls], type_ignores=[]), filename, 'exec'), namespace)
    return namespace[name]


class PropertyViewportContext(unittest.TestCase):
    def setUp(self):
        self.small = Area('small', width=300, height=200)
        self.large = Area('large', width=700, height=500, x=310)
        self.properties = Area('properties', 'PROPERTIES', width=200, height=500, x=1020)
        self.screen = SimpleNamespace(areas=[self.small, self.large, self.properties])
        self.window = SimpleNamespace(screen=self.screen)
        self.active = Object('active', qc_view_kind='atoms')
        self.pinned = Object('pinned', qc_view_kind='field', qc_dataset='dataset',
                             qc_dataset_sha256='dataset-sha', qc_source_sha256='source-sha')
        self.properties.spaces.active.use_pin_id = True
        self.properties.spaces.active.pin_id = self.pinned
        self.handlers = []
        self.bpy = ModuleType('bpy')
        self.bpy.types = SimpleNamespace(Object=Object, Operator=Operator,
            SpaceView3D=SimpleNamespace(draw_handler_add=lambda *args: 'handle',
                                       draw_handler_remove=lambda *args: self.handlers.append(args)))
        self.bpy.data = SimpleNamespace(objects={self.active.name: self.active, self.pinned.name: self.pinned})
        self.context = SimpleNamespace(window=self.window, screen=self.screen, area=self.properties,
            region=self.properties.region, region_data=None, object=self.active,
            selected_objects=[self.active, self.pinned], evaluated_depsgraph_get=lambda: 'depsgraph',
            window_manager=SimpleNamespace(modal_handler_add=lambda operator: None))

        @contextmanager
        def override(**values):
            saved = {key: getattr(self.context, key, None) for key in values}
            saved['region_data'] = self.context.region_data
            for key, value in values.items():
                setattr(self.context, key, value)
            self.context.region_data = self.context.area.view
            try:
                yield
            finally:
                for key, value in saved.items():
                    setattr(self.context, key, value)

        self.context.temp_override = override
        self.bpy.context = self.context
        self.helper = load_helper(self.bpy)
        self.namespace = {'__package__': 'qcblender.blender', 'bpy': self.bpy,
                          'FloatProperty': lambda **kwargs: None,
                          'EnumProperty': lambda **kwargs: None, 'error_text': str,
                          'target_object': self.helper.target_object,
                          'target_context': self.helper.target_context,
                          'viewport_context': self.helper.viewport_context}
        Operator.messages.clear()

    def test_properties_uses_largest_same_window_view_and_pinned_object(self):
        selected = self.helper.viewport_context(self.context)
        self.assertIs(selected.area, self.large)
        self.assertIs(selected.region, self.large.region)
        self.assertIs(selected.view, self.large.view)
        self.assertIs(self.helper.target_object(self.context), self.pinned)
        self.assertIs(self.helper.target_context(self.context).object, self.pinned)
        self.assertIs(self.context.object, self.active)
        self.assertIs(self.context.area, self.properties)

    def test_tied_areas_keep_screen_order_and_other_windows_are_not_considered(self):
        self.large.width, self.large.height = self.small.width, self.small.height
        self.assertIs(self.helper.viewport_context(self.context).area, self.small)
        self.screen.areas = [self.properties]
        with self.assertRaisesRegex(ValueError, 'same window'):
            self.helper.viewport_context(self.context)

    def test_invoking_view_and_region_data_are_preserved(self):
        self.context.area = self.small
        self.context.region = self.small.region
        pane = SimpleNamespace(view_rotation='quad-view-pane')
        self.context.region_data = pane
        selected = self.helper.viewport_context(self.context)
        self.assertIs(selected.area, self.small)
        self.assertIs(selected.view, pane)

    def test_pinned_non_object_does_not_fall_back_to_active_object(self):
        self.properties.spaces.active.pin_id = SimpleNamespace(name='material')
        self.assertIsNone(self.helper.target_object(self.context))
        self.properties.spaces.active.use_pin_id = False
        self.assertIs(self.helper.target_object(self.context), self.active)

    def test_missing_region_and_changed_selected_editor_are_rejected(self):
        self.large.regions = []
        with self.assertRaisesRegex(ValueError, 'viewport window'):
            self.helper.viewport_context(self.context)
        self.large.regions = [self.large.region]
        selected = self.helper.viewport_context(self.context)
        self.large.type = 'OUTLINER'
        with self.assertRaisesRegex(ValueError, 'changed during probing'):
            selected.validate()

    def camera(self):
        fitted, linked = [], []
        def fit(points, basis, aspect, margin):
            fitted.append(points)
            return SimpleNamespace(tolist=lambda: [0, 0, 10]), 3., 100.
        self.context.scene = SimpleNamespace(render=SimpleNamespace(
            resolution_x=100, resolution_y=100, pixel_aspect_x=1, pixel_aspect_y=1),
            collection=SimpleNamespace(objects=SimpleNamespace(link=linked.append)))
        self.context.view_layer = SimpleNamespace(objects=SimpleNamespace(active=self.active))
        self.bpy.data.cameras = SimpleNamespace(new=lambda name: SimpleNamespace())
        self.bpy.data.objects = SimpleNamespace(new=lambda name, data: Object(name))
        self.namespace.update(np=SimpleNamespace(array=lambda values: values), fit_orthographic=fit,
            _view_points=lambda obj, depsgraph: [obj.name], _renderable=lambda obj, context: True,
            _DISPLAY_KINDS={'atoms', 'field', 'slice', 'fog'})
        cls = operator_class('camera.py', 'QCBLENDER_OT_create_framed_camera', self.namespace)
        operator = cls()
        operator.margin = .05
        return cls, operator, fitted, linked

    def test_properties_camera_frames_only_pinned_target(self):
        cls, operator, fitted, linked = self.camera()
        self.assertTrue(cls.poll(self.context))
        self.assertEqual(operator.execute(self.context), {'FINISHED'})
        self.assertEqual(fitted, [['pinned']])
        self.assertEqual(len(linked), 1)
        self.assertIs(linked[0].rotation_quaternion, self.large.view.view_rotation)

    def test_render_output_uses_viewport_selection_while_object_properties_keeps_pin(self):
        path = ROOT / 'qcblender/blender/output_ui.py'
        function = next(node for node in ast.parse(path.read_text(encoding='utf-8')).body
                        if isinstance(node, ast.FunctionDef) and node.name == 'output_context')
        self.namespace['contextmanager'] = contextmanager
        exec(compile(ast.Module(body=[function], type_ignores=[]), str(path), 'exec'), self.namespace)
        self.properties.spaces.active.context = 'RENDER'
        with self.namespace['output_context'](self.context) as context:
            self.assertIs(context.area, self.large)
            self.assertIs(self.helper.target_object(context), self.active)
            self.assertEqual(context.selected_objects, [self.active, self.pinned])
        self.properties.spaces.active.context = 'OBJECT'
        with self.namespace['output_context'](self.context) as context:
            self.assertIs(context.area, self.properties)
            self.assertIs(self.helper.target_object(context), self.pinned)

    def test_viewport_camera_retains_multiple_selected_views(self):
        cls, operator, fitted, _ = self.camera()
        self.context.area, self.context.region = self.small, self.small.region
        self.context.region_data = self.small.view
        self.assertEqual(operator.execute(self.context), {'FINISHED'})
        self.assertEqual(fitted, [['active', 'pinned']])

    def test_properties_camera_never_falls_back_when_pin_is_invalid(self):
        cls, operator, fitted, linked = self.camera()
        self.properties.spaces.active.pin_id = SimpleNamespace(name='material')
        self.assertFalse(cls.poll(self.context))
        self.assertEqual(operator.execute(self.context), {'CANCELLED'})
        self.assertEqual(fitted, [])
        self.assertEqual(linked, [])

    def test_camera_no_viewport_is_disabled_with_an_explanation(self):
        cls, operator, fitted, linked = self.camera()
        self.screen.areas = [self.properties]
        self.assertFalse(cls.poll(self.context))
        self.assertIn('same window', cls.messages[-1])
        self.assertEqual(operator.execute(self.context), {'CANCELLED'})
        self.assertEqual(fitted, [])

    def probe(self):
        field = {'array': 'values', 'valid_mask': 'valid', 'unit': 'e', 'quantity': 'test'}
        source = Object('volume', qc_dataset='dataset', qc_dataset_sha256='dataset-sha',
                        qc_source_sha256='source-sha')
        meta = {'source': {'sha256': 'source-sha'}}
        def bound(obj):
            self.assertIs(obj, self.pinned)
            return source, field, meta, meta['source']
        self.namespace.update(bound_field=bound, mapped_field=lambda obj: (source, field, meta),
            profile_source=lambda obj, role: (source, field), field_source=lambda metadata, field: metadata['source'],
            binding_key=lambda obj: (obj['qc_dataset'], obj['qc_dataset_sha256']),
            load_dataset=lambda path: SimpleNamespace(metadata=meta), _probe_draw=lambda operator: None,
            np=SimpleNamespace(asarray=lambda value: value, array_equal=lambda a, b: a == b,
                               linalg=SimpleNamespace(LinAlgError=RuntimeError)), json=__import__('json'))
        self.bpy.path = SimpleNamespace(abspath=lambda value: value)
        cls = operator_class('interaction.py', 'QCBLENDER_OT_click_probe', self.namespace)
        operator = cls()
        operator.role = 'GEOMETRY'
        return cls, operator

    @staticmethod
    def event(kind='LEFTMOUSE', value='PRESS', x=1100, y=100):
        return SimpleNamespace(type=kind, value=value, mouse_x=x, mouse_y=y)

    def test_probe_invocation_captures_pin_and_selected_viewport(self):
        cls, operator = self.probe()
        self.pinned['qc_probe'] = 'old'
        self.assertEqual(operator.invoke(self.context, self.event()), {'RUNNING_MODAL'})
        self.assertIs(operator._target, self.pinned)
        self.assertIs(operator._area, self.large)
        self.assertIs(operator._region, self.large.region)
        self.assertIs(operator._view, self.large.view)
        self.assertEqual(operator._old_probe, 'old')

    def test_probe_poll_uses_pin_for_eligibility(self):
        cls, operator = self.probe()
        capabilities = ModuleType('qcblender.blender.capabilities')
        seen = []
        capabilities.poll_action = lambda cls, context, action: seen.append(context.object) or True
        with patch.dict(sys.modules, {capabilities.__name__: capabilities}):
            self.assertTrue(cls.poll(self.context))
        self.assertEqual(seen, [self.pinned])

    def test_probe_accepts_context_object_drift_but_rejects_real_binding_change(self):
        cls, operator = self.probe()
        operator.invoke(self.context, self.event())
        operator._check_binding(self.context)
        self.pinned['qc_source_job'] = 3
        with self.assertRaisesRegex(ValueError, 'binding changed'):
            operator._check_binding(self.context)

    def test_outside_click_retains_pending_sample_and_enter_saves_captured_target(self):
        cls, operator = self.probe()
        operator.invoke(self.context, self.event())
        operator._pending = {'quantity': 'test', 'value': 2., 'unit': 'e'}
        operator._pending_transforms = tuple(obj.matrix_world for obj in
                                            (operator._target, operator._geometry, operator._source))
        pending = operator._pending
        self.assertEqual(operator.modal(self.context, self.event()), {'RUNNING_MODAL'})
        self.assertIs(operator._pending, pending)
        self.assertEqual(operator.modal(self.context, self.event('RET')), {'FINISHED'})
        self.assertIn('qc_probe', self.pinned)
        self.assertNotIn('qc_probe', self.active)
        self.assertEqual(len(self.handlers), 1)

    def test_escape_from_properties_restores_target_probe(self):
        cls, operator = self.probe()
        self.pinned['qc_probe'] = 'previous-record'
        operator.invoke(self.context, self.event())
        self.assertEqual(operator.modal(self.context, self.event('ESC')), {'CANCELLED'})
        self.assertEqual(self.pinned['qc_probe'], 'previous-record')
        self.assertNotIn('qc_probe', self.active)

    def test_probe_ignores_other_window_and_keeps_viewport_bounds_half_open(self):
        cls, operator = self.probe()
        operator.invoke(self.context, self.event())
        operator._pending = {'value': 'retained'}
        self.assertTrue(operator._viewport.contains(self.event(x=310, y=0)))
        self.assertFalse(operator._viewport.contains(self.event(x=1010, y=0)))
        self.assertFalse(operator._viewport.contains(self.event(x=310, y=500)))
        self.context.window = SimpleNamespace(screen=SimpleNamespace(areas=[]))
        self.assertEqual(operator.modal(self.context, self.event('RET')), {'PASS_THROUGH'})
        self.assertEqual(operator._pending, {'value': 'retained'})

    def test_probe_hud_is_drawn_only_in_captured_window_and_region(self):
        cls, operator = self.probe()
        operator.invoke(self.context, self.event())
        tree = ast.parse((ROOT / 'qcblender/blender/interaction.py').read_text(encoding='utf-8'))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == '_probe_draw')
        namespace = dict(self.namespace)
        exec(compile(ast.Module(body=[function], type_ignores=[]), 'interaction.py', 'exec'), namespace)
        font = ModuleType('blf')
        drawn = []
        font.size = lambda *args: None
        font.position = lambda *args: None
        font.draw = lambda font_id, text: drawn.append(text)
        with patch.dict(sys.modules, {'blf': font}):
            namespace['_probe_draw'](operator)
            self.assertEqual(drawn, [])
            self.context.area, self.context.region = self.large, self.large.region
            namespace['_probe_draw'](operator)
            self.assertEqual(drawn, [operator._hud])
            self.context.area, self.context.region = self.small, self.small.region
            namespace['_probe_draw'](operator)
            self.assertEqual(drawn, [operator._hud])


if __name__ == '__main__':
    unittest.main()
