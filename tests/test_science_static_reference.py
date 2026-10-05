import hashlib
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = Path(os.environ.get('QCBLENDER_REFERENCE_ROOT', ROOT))
sys.path[:0] = [str(ROOT), str(SAMPLES / 'outputs/science')]
from qcblender.data import save_dataset
from qcblender.gaussian_log import read_log
from qcblender.irc import import_irc
from qcblender.readers import read_source
from qcblender.static_reference import load_static_reference, require_static_reference
from tools.local_inputs import input_path


class StaticReference(unittest.TestCase):
    def test_real_optimization_and_irc_are_rejected_including_initial_geometry(self):
        log = input_path('log-examples/water_neutral_nbo_opt_freq.out', SAMPLES)
        irc = input_path('sop/c10-c13/peroxide-irc-pyscf', SAMPLES) / 'steps.csv'
        for data in (read_log(log, 0), import_irc(irc)):
            with self.subTest(format=data.metadata['source'].get('format')):
                with self.assertRaisesRegex(ValueError, '独立'):
                    require_static_reference(data)
                ROOT.joinpath('outputs').mkdir(exist_ok=True)
                with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as tmp:
                    save_dataset(data, tmp)
                    digest = hashlib.sha256(Path(tmp, 'manifest.json').read_bytes()).hexdigest()
                    with self.assertRaisesRegex(ValueError, '独立'):
                        load_static_reference(tmp, digest)

    def test_static_log_and_step_fchk_remain_eligible(self):
        log = read_log(input_path('log-examples/water_neutral_nbo_opt_freq.out', SAMPLES), 1)
        fchk = read_source(input_path('sop/c10-c13/peroxide-irc-pyscf/step-001.fchk', SAMPLES))
        for data in (log, fchk):
            self.assertIs(require_static_reference(data), data)

    def test_multiframe_xyz_is_rejected_and_single_frame_is_static(self):
        ROOT.joinpath('outputs').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'outputs') as tmp:
            path = Path(tmp, 'frames.xyz')
            frame = '1\nHydrogen\nH 0 0 0\n'
            path.write_text(frame + frame.replace('0 0 0', '0 0 1'), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, '独立'):
                require_static_reference(read_source(path))
            path.write_text(frame, encoding='utf-8')
            require_static_reference(read_source(path))


if __name__ == '__main__':
    unittest.main()
