import copy
import unittest
from test_portfolio_snapshot_pipeline import PUBLIC_A, snapshot, builder

class RepositoryIdentityCollisionTests(unittest.TestCase):
    def test_case_only_name_collision_is_rejected(self):
        second=copy.deepcopy(PUBLIC_A)
        second["name"]=PUBLIC_A["name"].upper()
        second["head_sha"]="b"*40
        with self.assertRaisesRegex(builder.SnapshotError,"unique"):
            snapshot([PUBLIC_A,second])
