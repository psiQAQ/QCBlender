"""Context eligibility shared by controls and operators; never read source files."""
from ..i18n import error_text, ui_layout
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
        relevant, ready, reason = bound, 'orbitals' in meta, 'Source data lacks orbital coefficients; refresh sources if not loaded'
    elif action == 'charge':
        relevant, ready, reason = atoms, bool(meta.get('charges')), 'Source data has no atomic charge records'
        if ready:
            from .graph import view_modifier
            try:
                ready = not view_modifier(obj).node_group.get('qc_color_mapping')
                reason = 'This view has a bound color field; use an independent atom layer'
            except ValueError as error:
                ready, reason = False, str(error)
    elif action == 'dipole':
        relevant, ready, reason = atoms, bool(meta.get('dipole')), 'Source data has no molecular dipole record'
    elif action == 'declare':
        relevant = scalar and field.get('quantity') == 'unknown_scalar'
        ready, reason = bool(field), 'Field record is missing'
    elif action in ('slice', 'fog', 'surface'):
        relevant, ready, reason = scalar, bool(field), 'Scalar field record is missing'
    elif action in ('profile', 'profile_start', 'probe_click'):
        relevant = kind in ('field', 'slice')
        ready, reason = bool(field), 'Scalar field record is missing'
        if action == 'profile' and relevant and not obj.get('qc_profile_start'):
            ready, reason = False, 'Mark the profile start on this display layer first'
    elif action == 'probe':
        relevant = scalar or (atoms and obj.qc_settings.volume is not None)
        ready, reason = obj is not None and obj.qc_settings.volume is not None, 'Linked volume field is missing'
    elif action == 'clip':
        relevant, ready, reason = atoms or scalar, True, ''
        if relevant:
            from .graph import view_modifier
            try:
                ready = not view_modifier(obj).node_group.get('qc_clipping')
                reason = 'Clipping already exists; adjust Spatial View in Object Properties'
            except ValueError as error:
                ready, reason = False, str(error)
    elif action in ('projection', 'aicd'):
        relevant, ready, reason = atoms, bool(meta.get('source')), 'Refresh source records first'
    elif action == 'esp':
        relevant = field.get('quantity') == 'electrostatic_potential' or record(obj, 'qc_color_source').get('quantity') == 'electrostatic_potential'
        ready = field.get('quantity') == 'electrostatic_potential'
        reason = 'Select an actual ESP field view as the import reference'
    elif action in ('aim', 'paired', 'nbo', 'nocv_table'):
        relevant, ready, reason = bound, bool(meta.get('source')), 'Refresh source records first'
    elif action == 'nocv_field':
        relevant = obj is not None and obj.get('qc_analysis_role') == 'ets_nocv'
        ready, reason = bool(meta.get('analysis', {}).get('pairs')), 'The computed NOCV pair table is missing'
    elif action == 'atoms':
        relevant, ready, reason = atoms, atoms, 'Select a QC atom view'
    elif action == 'result_scatter':
        relevant = kind == 'scatter' or (obj is not None and obj.get('qc_analysis_role') == 'paired')
        ready, reason = len(meta.get('fields', [])) == 2, 'Paired field sources are missing; refresh sources'
    elif action == 'result_filter':
        relevant = kind == 'nbo' or (obj is not None and obj.get('qc_analysis_role') in
            ('esp_maximum', 'esp_minimum', 'esp_area', 'aim_C', 'aim_N', 'aim_O', 'aim_F', 'ets_nocv'))
        ready, reason = bool(meta.get('analysis')), 'Analysis records are missing; refresh sources'
    else:
        raise ValueError('Unknown QC action: ' + action)
    if relevant and action in ('aim', 'paired', 'nbo', 'nocv_table', 'esp', 'nocv_field', 'projection', 'aicd'):
        from .static_reference import cached_reference_reason
        static_reason = cached_reference_reason(obj, cached_metadata)
        if static_reason:
            ready, reason = False, static_reason
    if relevant and not bound:
        ready, reason = False, 'Dataset binding is missing; restore the data source'
    if relevant and bound and 'error' in meta:
        ready, reason = False, meta['error']
    if relevant and obj.mode != 'OBJECT':
        ready, reason = False, 'Switch to Object Mode'
    if relevant and ready and (action in ('slice', 'fog', 'surface', 'profile', 'profile_start', 'probe_click') or action == 'probe'):
        volume = obj.qc_settings.volume
        if volume is None or not volume.get('qc_field'):
            ready, reason = False, 'Linked volume field is missing; restore the data source'
        elif field and record(volume, 'qc_field') != field:
            ready, reason = False, 'Display layer and linked volume identities differ'
        elif field and (volume.get('qc_dataset_sha256') != obj.get('qc_dataset_sha256') or
                        volume.get('qc_source_sha256') != obj.get('qc_source_sha256')):
            ready, reason = False, 'Display layer and volume source digests differ'
    return bool(relevant), bool(relevant and ready), reason if relevant and not ready else ''


def poll_action(cls, context, action):
    relevant, enabled, reason = capability(context, action)
    if not enabled:
        cls.poll_message_set(error_text(reason or 'This action is unavailable for the active object'))
    return enabled


def action_button(layout, context, action, operator, text, icon='NONE'):
    layout = ui_layout(layout)
    relevant, enabled, reason = capability(context, action)
    if not relevant:
        return
    row = layout.row()
    row.enabled = enabled
    row.operator(operator, text=text, icon=icon)
    if reason:
        layout.label(text=error_text(reason), icon='INFO')
