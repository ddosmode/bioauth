import os
import unittest
import numpy as np
import cv2

from src.detector import FaceDetector
from src.recognizer import FaceRecognizer

class TestBioAuth(unittest.TestCase):
    def setUp(self):
        self.raw_face_path = os.path.expanduser("~/.config/bioauth/enrollment/raw_face.jpg")
        self.vector_path = os.path.expanduser("~/.config/bioauth/enrollment/usernarne.npy")

    def test_detector_on_enrolled_face(self):
        if not os.path.exists(self.raw_face_path):
            self.skipTest("No enrolled face photo found")
        img = cv2.imread(self.raw_face_path)
        detector = FaceDetector()
        faces = detector.detect(img)
        self.assertIsNotNone(faces)
        self.assertGreaterEqual(len(faces), 1)

    def test_recognizer_self_match(self):
        if not os.path.exists(self.vector_path):
            self.skipTest("No enrolled vector found")
        feature = np.load(self.vector_path)
        recognizer = FaceRecognizer()
        is_match, score = recognizer.match(feature, feature)
        self.assertTrue(is_match)
        self.assertAlmostEqual(score, 1.0, places=3)

    def test_recognizer_random_mismatch(self):
        if not os.path.exists(self.vector_path):
            self.skipTest("No enrolled vector found")
        feature = np.load(self.vector_path)
        random_feature = np.random.randn(*feature.shape).astype(np.float32)
        # Normalize
        random_feature = random_feature / np.linalg.norm(random_feature)
        recognizer = FaceRecognizer()
        is_match, score = recognizer.match(feature, random_feature)
        self.assertFalse(is_match)
        self.assertLess(score, 0.40)

if __name__ == "__main__":
    unittest.main()
