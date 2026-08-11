import cv2
import numpy as np


def bgr_to_rgb(frame: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


def resize_frame(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    return cv2.resize(frame, (width, height), interpolation=cv2.INTER_LINEAR)


def frame_to_png_bytes(frame: np.ndarray) -> bytes:
    success, buffer = cv2.imencode(".png", frame)
    if not success:
        raise RuntimeError("Failed to encode frame to PNG")
    return buffer.tobytes()


def frame_to_jpeg_bytes(frame: np.ndarray, quality: int = 80) -> bytes:
    success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not success:
        raise RuntimeError("Failed to encode frame to JPEG")
    return buffer.tobytes()
