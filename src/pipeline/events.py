import queue
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class PipelineEvent:
    event_type: str          # "track" | "frame" | "error" | "status"
    camera_id: str
    payload: Any = None
    timestamp: float = field(default=0.0)


class EventBus:
    """Simple thread-safe event queue shared by runners and the coordinator."""

    def __init__(self, maxsize: int = 10_000):
        self._q: queue.Queue[PipelineEvent] = queue.Queue(maxsize=maxsize)

    def put(self, event: PipelineEvent, block: bool = False) -> None:
        try:
            self._q.put_nowait(event)
        except queue.Full:
            logger.warning("EventBus full — dropping %s event from %s",
                           event.event_type, event.camera_id)

    def get(self, timeout: float = 1.0) -> Optional[PipelineEvent]:
        try:
            return self._q.get(timeout=timeout)
        except queue.Empty:
            return None

    def qsize(self) -> int:
        return self._q.qsize()
