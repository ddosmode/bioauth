"""Модуль извлечения биометрических признаков и верификации (SFace)."""

import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

DEFAULT_SFACE_PATH = "/etc/bioauth/models/face_recognition_sface_2021dec.onnx"
if not os.path.exists(DEFAULT_SFACE_PATH):
    DEFAULT_SFACE_PATH = os.path.expanduser("~/.config/bioauth/models/face_recognition_sface_2021dec.onnx")

class FaceRecognizer:
    def __init__(self, model_path: str = DEFAULT_SFACE_PATH, cosine_threshold: float = 0.40):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model_path = model_path
        self.cosine_threshold = cosine_threshold
        self._recognizer = cv2.FaceRecognizerSF.create(self.model_path, "")

    def extract_feature(self, image: np.ndarray, face_box: np.ndarray) -> np.ndarray:
        """Выравнивает лицо и извлекает 128-мерный эмбеддинг."""
        aligned = self._recognizer.alignCrop(image, face_box)
        feature = self._recognizer.feature(aligned)
        return feature

    def match(self, feature1: np.ndarray, feature2: np.ndarray) -> tuple[bool, float]:
        """Сравнивает два признака с использованием косинусного сходства."""
        score = self._recognizer.match(feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE)
        is_match = score >= self.cosine_threshold
        return is_match, float(score)
