"""Local operator credential files must be private and stable across restarts."""
from pathlib import Path
import stat
import tempfile
import unittest
from app.staff import COUNSELORS, local_credentials


class LocalCredentialTests(unittest.TestCase):
    def test_first_run_credentials_persist_without_repository_files(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'private' / 'staff-access.json'
            first = local_credentials(path)
            second = local_credentials(path)
            self.assertTrue(first == second)
            self.assertEqual(len(first), len(COUNSELORS) + 1)
            self.assertEqual(len({entry['key'] for entry in first}), len(first))
            self.assertTrue(all(len(entry['key']) >= 40 for entry in first))
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
