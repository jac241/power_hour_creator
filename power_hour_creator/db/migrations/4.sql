CREATE INDEX IF NOT EXISTS tracks_power_hour_id_index ON tracks(power_hour_id);
CREATE UNIQUE INDEX IF NOT EXISTS tracks_power_hour_id_position_unique_index ON tracks(power_hour_id, position)
