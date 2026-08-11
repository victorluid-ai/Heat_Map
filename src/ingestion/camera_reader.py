import threading
import time
import logging
import cv2
import numpy as np
from typing import Optional
from .frame_buffer import FrameBuffer

logger = logging.getLogger(__name__)

RECONNECT_DELAY = 5.0
RECONNECT_MAX_ATTEMPTS = 10


class CameraReader:
    def __init__(self, camera_id: str, source: str | int, buffer_size: int = 30):
        self.camera_id = camera_id
        self._source = source
        self._buffer = FrameBuffer(maxlen=buffer_size)
        self._cap: Optional[cv2.VideoCapture] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def start(self) -> None:
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True, name=f"cam-{self.camera_id}")
        self._thread.start()
        logger.info("Camera %s started (source=%s)", self.camera_id, self._source)

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        if self._cap:
            self._cap.release()
        logger.info("Camera %s stopped", self.camera_id)

    def get_frame(self) -> Optional[tuple[float, np.ndarray]]:
        return self._buffer.get()

    def _open(self) -> bool:
        self._cap = cv2.VideoCapture(self._source)
        return self._cap.isOpened()

    def _read_loop(self) -> None:
        attempts = 0
        while self._running:
            if self._cap is None or not self._cap.isOpened():
                if attempts >= RECONNECT_MAX_ATTEMPTS:
                    logger.error("Camera %s: max reconnect attempts reached", self.camera_id)
                    break
                if not self._open():
                    attempts += 1
                    logger.warning("Camera %s: open failed, retry %d/%d", self.camera_id, attempts, RECONNECT_MAX_ATTEMPTS)
                    time.sleep(RECONNECT_DELAY)
                    continue
                attempts = 0

            ret, frame = self._cap.read()
            if not ret:
                if isinstance(self._source, str) and not self._source.startswith("rtsp"):
                    self._running = False
                    break
                logger.warning("Camera %s: read failed, reconnecting", self.camera_id)
                self._cap.release()
                self._cap = None
                time.sleep(RECONNECT_DELAY)
                continue

            self._buffer.put(frame)
