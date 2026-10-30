"""Модуль детекции лиц с использованием YuNet (OpenCV FaceDetectorYN)."""

import os
import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)

DEFAULT_YUNET_PATH = "/etc/bioauth/models/face_detection_yunet_2023mar.onnx"
if not os.path.exists(DEFAULT_YUNET_PATH):
    DEFAULT_YUNET_PATH = os.path.expanduser("~/.config/bioauth/models/face_detection_yunet_2023mar.onnx")

class FaceDetector:
    def __init__(self, model_path: str = DEFAULT_YUNET_PATH, conf_threshold: float = 0.6, nms_threshold: float = 0.3):
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.nms_threshold = nms_threshold
        self._detector = None
        self._current_size = None

    def _get_detector(self, width: int, height: int):
        if self._detector is None or self._current_size != (width, height):
            self._detector = cv2.FaceDetectorYN.create(
                self.model_path,
                "",
                (width, height),
                self.conf_threshold,
                self.nms_threshold,
                5000
            )
            self._current_size = (width, height)
        return self._detector

    def detect(self, image: np.ndarray):
        """Возвращает список обнаруженных лиц или пустой список."""
        if image is None:
            return []
        h, w, _ = image.shape
        detector = self._get_detector(w, h)
        retval, faces = detector.detect(image)
        if faces is not None and len(faces) > 0:
            return faces
        return []
