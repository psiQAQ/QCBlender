import importlib
from importlib.metadata import version
import platform
import sys


def check_runtime():
    modules = []
    for name, distribution, required in (
        ('numpy', 'numpy', '2.3.4'), ('openvdb', None, None),
        ('scipy', 'scipy', '1.16.3'), ('cclib', 'cclib', '1.8.1'),
        ('iodata', 'qc-iodata', '1.0.1'), ('gbasis', 'qc-gbasis', '0.1.0+qcblender.071969c.pure1'),
        ('gbasis.evals.electrostatic_potential', None, None),
    ):
        entry = {'module': name}
        try:
            module = importlib.import_module(name)
            actual = version(distribution) if distribution else None
            entry.update(origin=module.__file__, version=actual,
                         status='Passed' if required is None or actual == required else 'Failed')
            if entry['status'] == 'Failed':
                entry['error'] = f'Requires {required}; loaded {actual}'
        except (ImportError, OSError, RuntimeError) as error:
            entry.update(status='Failed', error=f'{type(error).__name__}: {error}')
        modules.append(entry)
    return {'ok': all(m['status'] == 'Passed' for m in modules),
            'python': sys.version, 'platform': platform.platform(), 'modules': modules}
