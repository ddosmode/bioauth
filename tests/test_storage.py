import os
import tempfile
import unittest
from pathlib import Path
import numpy as np
from src.storage import private_dir, save_embedding, load_embedding

class StorageTests(unittest.TestCase):
    def test_permissions_roundtrip(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "profiles" / "primary.npy"
            data = np.ones((1, 128), dtype=np.float32)
            save_embedding(path, data)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
            np.testing.assert_array_equal(load_embedding(path), data)

    def test_bad_shape_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "bad.npy"
            np.save(path, np.ones((2, 2)))
            with self.assertRaises(ValueError):
                load_embedding(path)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            original = Path(root) / "original.npy"
            np.save(original, np.ones((1, 128)))
            link = Path(root) / "link.npy"
            link.symlink_to(original)
            with self.assertRaises(ValueError):
                load_embedding(link)
