"""Critical boundaries of the approved output cleanup categories."""
import unittest
from tools.prune_outputs import OUTPUTS, classify


class CleanupBoundaries(unittest.TestCase):
    def test_environment_and_user_project_precede_generated_file_rules(self):
        keep = ('recovery/pid3144-preserved/evidence.blend',
                'batch/profile/config/userpref.blend',
                'batch/profile/extensions/user_default/qcblender/assets/nodes.blend',
                'committed-build/source/outputs/science/package/reference.npy',
                'v1-acceptance/sources/raw-calculation.log', 'branch-archive/manifest.json',
                'unknown-user-folder/user.blend', 'process-temp/quit.blend')
        remove = ('vmd-parameters/evidence.qcdata/datasets/id/manifest.json', 'vmd-parameters/dist/qcblender.zip',
                  'batch/profile/extensions/.user/qcblender/jobs/id/dataset/arrays/a.npy',
                  'batch/profile/datafiles/qcblender/analyses/id/arrays/a.npy')
        for path in keep:
            self.assertEqual(classify(OUTPUTS / path, {})[0], 'keep', path)
        for path in remove:
            self.assertEqual(classify(OUTPUTS / path, {})[0], 'delete', path)
        self.assertEqual(classify(OUTPUTS / 'batch/profile/extensions/.user/qcblender/jobs/id/worker.log', {})[0], 'keep')


if __name__ == '__main__':
    unittest.main()
