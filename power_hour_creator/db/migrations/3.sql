ALTER TABLE tracks RENAME TO tmp_tracks;

CREATE TABLE IF NOT EXISTS tracks (
  id          integer PRIMARY KEY AUTOINCREMENT,
  position    integer NOT NULL,
  url         text NOT NULL,
  title       text NOT NULL,
  length      integer NOT NULL,
  start_time  decimal(7, 3) NOT NULL,
  full_song   integer NOT NULL DEFAULT 0,
  power_hour_id integer NOT NULL, FOREIGN KEY(power_hour_id) REFERENCES power_hours(id) ON DELETE CASCADE
);

INSERT INTO tracks(id, position, url, title, length, start_time, full_song, power_hour_id)
  SELECT id, position, url, title, length, start_time, full_song, power_hour_id
  FROM tmp_tracks;

DROP TABLE tmp_tracks
