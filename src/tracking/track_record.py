from dataclasses import dataclass


@dataclass
class TrackUpdate:
    camera_id: str
    track_id: int
    x: float
    y: float
    timestamp: float
    confidence: float


@dataclass
class DwellUpdate:
    camera_id: str
    track_id: int
    zone_id: str
    entry_time: float
    exit_time: float
