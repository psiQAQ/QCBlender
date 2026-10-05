"""Eligibility of a Dataset used as an external analysis reference."""
import hashlib
from pathlib import Path


STATIC_REFERENCE_REASON = '外部分析需要静态科学参考；请使用对应步骤的独立文件'


def dynamic_reference(metadata):
    """Identify datasets whose scientific coordinates can be switched."""
    return (metadata.get('optimization', {}).get('status') == 'available'
            or bool(metadata.get('trajectory'))
            or metadata.get('analysis', {}).get('kind') == 'IRC')


def require_static_reference(data):
    if dynamic_reference(data.metadata):
        raise ValueError(STATIC_REFERENCE_REASON)
    return data


def load_static_reference(directory, expected_digest):
    from .data import load_dataset
    directory = Path(directory)
    digest = hashlib.sha256((directory / 'manifest.json').read_bytes()).hexdigest()
    if digest != expected_digest:
        raise ValueError('Reference calculation changed during import')
    return require_static_reference(load_dataset(directory))
