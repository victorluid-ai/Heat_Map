from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(String(16), nullable=False, default="customer")  # "admin" | "customer"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    shops = relationship("Shop", back_populates="owner")


class Shop(Base):
    __tablename__ = "shops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    address = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    owner = relationship("User", back_populates="shops")
    cameras = relationship("Camera", back_populates="shop")


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    source_url = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    shop_id = Column(Integer, ForeignKey("shops.id"), nullable=True, index=True)

    shop = relationship("Shop", back_populates="cameras")
    tracking_events = relationship("TrackingEvent", back_populates="camera", lazy="dynamic")
    dwell_records = relationship("DwellRecord", back_populates="camera", lazy="dynamic")


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String(64), ForeignKey("cameras.id"), nullable=False, index=True)
    track_id = Column(Integer, nullable=False, index=True)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    timestamp = Column(Float, nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=0.0)

    camera = relationship("Camera", back_populates="tracking_events")


class DwellRecord(Base):
    __tablename__ = "dwell_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera_id = Column(String(64), ForeignKey("cameras.id"), nullable=False, index=True)
    track_id = Column(Integer, nullable=False)
    zone_id = Column(String(64), nullable=False, index=True)
    entry_time = Column(Float, nullable=False)
    exit_time = Column(Float, nullable=False)
    dwell_seconds = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    camera = relationship("Camera", back_populates="dwell_records")
