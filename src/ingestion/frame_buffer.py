import threading
from collections import deque
from typing import Optional
import numpy as np
import time


class FrameBuffer:
    def __init__(self, maxlen: int = 30):
        self._buffer: deque = deque(maxlen=maxlen)
        self._lock = threading.Lock()

    def put(self, frame: np.ndarray) -> None:
        with self._lock:
            self._buffer.append((time.time(), frame.copy()))

    def get(self) -> Optional[tuple[float, np.ndarray]]:
        with self._lock:
            if self._buffer:
                return self._buffer[-1]
            return None

    def get_all(self) -> list[tuple[float, np.ndarray]]:
        with self._lock:
            return list(self._buffer)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)
