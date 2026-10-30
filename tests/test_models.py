import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from src import models

class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()

class ModelsTests(unittest.TestCase):
    def test_checksum_rejects_bad_download(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
                models.install_models(temp, opener=lambda url, timeout: FakeResponse(b"tampered"))
            self.assertEqual(list(Path(temp).glob("*.onnx")), [])

    def test_checksum_accepts_known_bytes(self):
        import hashlib
        blob = b"model-fixture"
        expected = hashlib.sha256(blob).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            with patch.dict(models.MODELS, {"test.onnx": ("fake", expected)}, clear=True):
                models.install_models(temp, opener=lambda url, timeout: FakeResponse(blob))
                self.assertEqual((Path(temp) / "test.onnx").read_bytes(), blob)
                models.install_models(temp, opener=lambda url, timeout: self.fail("unexpected download"))
