import unittest
from unittest.mock import patch
import numpy as np
from src.liveness import challenge, direction

class FakeCapture:
    def __init__(self, labels):
        self.labels = iter(labels)
    def read(self):
        try:
            label = next(self.labels)
        except StopIteration:
            return False, None
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        frame[0, 0, 0] = {"center": 1, "left": 2, "right": 3, "none": 4}[label]
        return True, frame

class FakeDetector:
    def detect(self, frame):
        label = int(frame[0, 0, 0])
        if label == 4:
            return []
        x = {1: 40, 2: 5, 3: 80}[label]
        return [np.array([x, 20, 10, 10])]

class LivenessTests(unittest.TestCase):
    def test_direction(self):
        self.assertEqual(direction([5, 20, 10, 10], 100), "left")
        self.assertEqual(direction([80, 20, 10, 10], 100), "right")

    def test_correct_sequence(self):
        labels = ["center"] * 3 + ["left"] * 3 + ["center"] * 3
        passed, frame = challenge(FakeCapture(labels), FakeDetector(), clock=lambda: 0, choose=lambda _: "left")
        self.assertTrue(passed)

    def test_static_photo_fails(self):
        labels = ["center"] * 15
        passed, frame = challenge(FakeCapture(labels), FakeDetector(), clock=lambda: 0, choose=lambda _: "left")
        self.assertFalse(passed)

    def test_wrong_direction_fails(self):
        labels = ["center"] * 3 + ["right"] * 15
        passed, frame = challenge(FakeCapture(labels), FakeDetector(), clock=lambda: 0, choose=lambda _: "left")
        self.assertFalse(passed)

    def test_missing_face_fails(self):
        labels = ["center"] * 3 + ["none"] * 4 + ["left"] * 3 + ["center"] * 3
        passed, frame = challenge(FakeCapture(labels), FakeDetector(), clock=lambda: 0, choose=lambda _: "left")
        self.assertFalse(passed)
