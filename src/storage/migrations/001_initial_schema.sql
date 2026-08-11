-- Heat Map System — Full schema (PostgreSQL / Supabase)
-- SQLAlchemy create_all() also builds this; use this file for manual migration or Supabase SQL editor.

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL       PRIMARY KEY,
    email           VARCHAR(256) NOT NULL UNIQUE,
    password_hash   VARCHAR(256) NOT NULL,
    role            VARCHAR(16)  NOT NULL DEFAULT 'customer',
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

CREATE TABLE IF NOT EXISTS shops (
    id          SERIAL       PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    address     TEXT,
    owner_id    INTEGER      NOT NULL REFERENCES users(id),
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_shops_owner ON shops (owner_id);

CREATE TABLE IF NOT EXISTS cameras (
    id          VARCHAR(64)  PRIMARY KEY,
    name        VARCHAR(128) NOT NULL,
    source_url  TEXT         NOT NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    shop_id     INTEGER      REFERENCES shops(id)
);

CREATE INDEX IF NOT EXISTS idx_cameras_shop ON cameras (shop_id);

CREATE TABLE IF NOT EXISTS tracking_events (
    id          SERIAL       PRIMARY KEY,
    camera_id   VARCHAR(64)  NOT NULL REFERENCES cameras(id),
    track_id    INTEGER      NOT NULL,
    x           FLOAT        NOT NULL,
    y           FLOAT        NOT NULL,
    timestamp   FLOAT        NOT NULL,
    confidence  FLOAT        NOT NULL DEFAULT 0.0
);

CREATE INDEX IF NOT EXISTS idx_tracking_camera_ts ON tracking_events (camera_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_tracking_track     ON tracking_events (track_id);

CREATE TABLE IF NOT EXISTS dwell_records (
    id             SERIAL      PRIMARY KEY,
    camera_id      VARCHAR(64) NOT NULL REFERENCES cameras(id),
    track_id       INTEGER     NOT NULL,
    zone_id        VARCHAR(64) NOT NULL,
    entry_time     FLOAT       NOT NULL,
    exit_time      FLOAT       NOT NULL,
    dwell_seconds  FLOAT       NOT NULL,
    recorded_at    TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dwell_zone ON dwell_records (zone_id, entry_time);
