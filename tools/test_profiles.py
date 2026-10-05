"""Explicit public tests; the complete local scientific suite remains separate."""

PUBLIC_SCIENCE = tuple('test_science_' + name for name in (
    'adapter', 'reference', 'cube', 'xyz', 'project', 'current_association',
    'geometry', 'measurements', 'planes', 'profile', 'framing', 'field_ranges',
    'resources', 'view_summary_export'))

STDLIB = tuple('test_' + name for name in (
    'cancel_finalization', 'copy_display', 'fog_materials', 'legend_layout',
    'local_inputs', 'multi_field_accept', 'native_volume', 'native_volume_project',
    'static_reference_capabilities', 'storage_cleanup', 'candidate_artifacts',
    'generate_qualification', 'view_summary', 'release_candidate'))
