"""Explicit public tests; the complete local scientific suite remains separate."""

PUBLIC_SCIENCE = tuple('test_science_' + name for name in (
    'adapter', 'reference', 'cube', 'xyz', 'project', 'current_association',
    'geometry', 'measurements', 'planes', 'profile', 'framing', 'field_ranges',
    'resources', 'view_summary_export', 'probe_metadata')) + ('test_annotation_geometry', 'test_annotations_core')

STDLIB = tuple('test_' + name for name in (
    'i18n_core', 'node_localization', 'ui_localization', 'operator_tooltips',
    'cancel_finalization', 'copy_display', 'fog_materials', 'legend_layout',
    'local_inputs', 'multi_field_accept', 'native_volume', 'native_volume_project',
    'static_reference_capabilities', 'storage_cleanup', 'candidate_artifacts',
    'generate_qualification', 'view_summary', 'release_candidate', 'validation_data',
    'empty_button_guards', 'record_ranges', 'color_presets', 'atom_benchmark',
    'annotation_inputs', 'object_summary', 'source_summary_cache', 'sidebar_layout', 'property_viewport_context',
    'workspace_paths', 'tutorial_dataset', 'tutorial_workspace', 'preview_release'))
