"""Модуль безопасного и быстрого захвата кадров с V4L2/OpenCV."""

import time
import cv2
import logging

logger = logging.getLogger(__name__)

class VideoCaptureHandler:
    def __init__(self, device_index: int = 0, warmup_frames: int = 1, timeout: float = 1.5):
        self.device_index = device_index
        self.warmup_frames = warmup_frames
        self.timeout = timeout

    def capture_frame(self):
        """Захватывает один стабильный кадр после короткого прогрева экспозиции."""
        cap = cv2.VideoCapture(self.device_index, cv2.CAP_V4L2)
        if not cap.isOpened():
            logger.error(f"Cannot open video device {self.device_index}")
            return None

        start_time = time.time()
        try:
            for _ in range(self.warmup_frames):
                if time.time() - start_time > self.timeout:
                    logger.warning("Capture timed out during warmup")
                    return None
                ret, _ = cap.read()
                if not ret:
                    time.sleep(0.05)

            ret, frame = cap.read()
            if ret and frame is not None:
                return frame
            return None
        finally:
            cap.release()
