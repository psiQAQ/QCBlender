"""Copy already downloaded, pinned upstream fixtures with provenance."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'tests/data/chemtools'
SOURCE = ROOT / 'outputs/m0-research/chemtools-references'
FILES = {
    'ch4_uhf_ccpvdz.fchk': '3f93c52df5ef5adda00eff89bc5c9bb0bc10182722193d87e72f3b710d7c2c40',
    'data_cubegen_g09_C01_ch4_uhf_ccpvdz.npz': 'b265e6c121f7b56da9386ed004f8c36decc09b1946fe6a3ce0f28b382cac6eec',
    'data_fortran_ch4_uhf_ccpvdz.npz': '6687ac93fbdcc3fc11fca59c6a7eb68df462c98509680abe8e209065786cebeb',
}
COMMIT = '47c9fe255848b8dbc6f589beb738421f76401885'
TARGET.mkdir(parents=True, exist_ok=True)
records = []
for name, digest in FILES.items():
    path = SOURCE / 'chemtools/data' / name
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
    shutil.copy2(path, TARGET / name)
    records.append({'file': name, 'sha256': digest, 'license': 'GPL-3.0-or-later',
                    'url': f'https://raw.githubusercontent.com/theochem/chemtools/{COMMIT}/chemtools/data/{name}'})
shutil.copy2(SOURCE / 'LICENSE', TARGET / 'LICENSE')
(TARGET / 'sources.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')

iodata_source = ROOT / 'outputs/m0-research/iodata-1.0.1'
iodata_target = ROOT / 'tests/data/iodata'
iodata_target.mkdir(parents=True, exist_ok=True)
records = []
for name in ('water_sto3g_hf_g03.fchk', 'ch3_hf_sto3g.fchk', 'ch3_rohf_sto3g_g03.fchk',
             'o2_cc_pvtz_pure.fchk', 'o2_cc_pvtz_cart.fchk',
             'li_h_3-21G_hf_g09.fchk', 'li2_g09_nbasis_indep.fchk'):
    path = iodata_source / 'iodata/test/data' / name
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    shutil.copy2(path, iodata_target / name)
    records.append({'file': name, 'sha256': digest, 'license': 'GPL-3.0-or-later',
                    'url': 'https://raw.githubusercontent.com/theochem/iodata/'
                           'adab5813713ba64641565eb2a8c11803a4e9bba6/iodata/test/data/' + name})
shutil.copy2(iodata_source / 'LICENSE.txt', iodata_target / 'LICENSE.txt')
(iodata_target / 'sources.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')

gbasis_commit = '071969c900d6d7a9fbbdfe193c65ba3be177fbdf'
gbasis_source = ROOT / 'outputs/m0-research' / ('gbasis-' + gbasis_commit)
gbasis_target = ROOT / 'tests/data/gbasis'
gbasis_target.mkdir(parents=True, exist_ok=True)
records = []
for relative, expected in [
    ('notebooks/tutorial/ch2o_q_0.fchk', '2be8499480834ebf30a921fe12f8696d264a6722916d3ad3e2a1430b651800b3'),
    ('tests/h2o_hf_ccpv5z_sph.fchk', '34f7063d2fdf97e4c7eaae4f2f1fb41b17c4c27a61540c7980af7a79ddf54a99'),
    ('tests/h2o_hf_ccpv5z_cart.fchk', '8ab96a3e64daf359353e19f0cc54fcc84ddbbded341a0b74c3b1a8f6a88b9f60')]:
    path = gbasis_source / relative
    assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    shutil.copy2(path, gbasis_target / path.name)
    records.append({'file': path.name, 'sha256': expected,
                    'license': 'GPL-3.0-or-later metadata; upstream LICENSE is LGPL-3.0 text',
                    'url': f'https://raw.githubusercontent.com/theochem/gbasis/{gbasis_commit}/{relative}'})
shutil.copy2(gbasis_source / 'LICENSE', gbasis_target / 'LICENSE')
(gbasis_target / 'sources.json').write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')
