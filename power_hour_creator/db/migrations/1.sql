CREATE TABLE IF NOT EXISTS power_hours (
  id    integer PRIMARY KEY AUTOINCREMENT,
  name  text NOT NULL
);

CREATE TABLE IF NOT EXISTS tracks (
  id          integer PRIMARY KEY AUTOINCREMENT,
  url         text NOT NULL,
  title       text NOT NULL,
  length      integer NOT NULL,
  start_time  integer NOT NULL,
  full_song   integer NOT NULL DEFAULT 0,
  power_hour_id integer NOT NULL, FOREIGN KEY(power_hour_id) REFERENCES power_hours(id)
);

CREATE INDEX IF NOT EXISTS tracks_power_hour_id_index ON tracks(power_hour_id)