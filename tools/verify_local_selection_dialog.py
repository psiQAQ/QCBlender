"""Capture the real Local Atom Selection dialog invoked by a native UI click."""
import importlib
import json
import os
from pathlib import Path
import sys

import bpy


_KEY = '_qc_local_selection_dialog_check'


def disarm():
    state = bpy.app.driver_namespace.pop(_KEY, None)
    if state is not None:
        state['cls'].invoke = state['invoke']
        bpy.context.window_manager.operator_properties_last(
            'qcblender.local_selection').mode = state['last_mode']


def arm(output_dir, expected_pid, previous_mode='CLEAR'):
    """Seed the remembered mode, then click 设置局部选择 and cancel its dialog."""
    if os.getpid() != expected_pid:
        raise RuntimeError('Blender process differs from the inspected target')
    if previous_mode not in ('CLEAR', 'RECOMPUTE', 'INVERT'):
        raise ValueError('Choose an immediate-action mode for this regression')
    disarm()
    names = [name for name in sys.modules if name.endswith('.blender.atom_selection')]
    if len(names) != 1:
        raise RuntimeError('Expected exactly one installed atom-selection module')
    cls = importlib.import_module(names[0]).QCBLENDER_OT_local_selection
    if not cls.poll(bpy.context):
        raise ValueError('Select a QC atom view before checking its dialog')
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    last = bpy.context.window_manager.operator_properties_last('qcblender.local_selection')
    state = {'cls': cls, 'invoke': cls.invoke, 'last_mode': last.mode}
    bpy.app.driver_namespace[_KEY] = state
    last.mode = previous_mode

    def capture(self, context, event):
        try:
            result = state['invoke'](self, context, event)
            report = {'status': 'Passed' if result == {'RUNNING_MODAL'} else 'Failed',
                      'pid': os.getpid(), 'blender': bpy.app.version_string,
                      'previous_mode': previous_mode, 'invoked_mode': self.mode,
                      'mode_explicit': self.properties.is_property_set('mode'),
                      'result': sorted(result), 'active_object': context.object.name,
                      'module_file': sys.modules[names[0]].__file__,
                      'method': 'Real registered invoke callback from a native panel click',
                      'independent_human_review': 'Not Run'}
            (output / 'dialog.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
            return result
        finally:
            cls.invoke = state['invoke']

    cls.invoke = capture
    return {'armed': True, 'pid': os.getpid(), 'previous_mode': previous_mode}
