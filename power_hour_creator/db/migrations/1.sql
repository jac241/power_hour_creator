CREATE TABLE IF NOT EXISTS power_hours (
  id    integer PRIMARY KEY AUTOINCREMENT,
  name  text NOT NULL
);

CREATE TABLE IF NOT EXISTS tracks (
  id          integer PRIMARY KEY AUTOINCREMENT,
  position    integer NOT NULL,
  url         text NOT NULL,
  title       text NOT NULL,
  length      integer NOT NULL,
  start_time  decimal(7, 3) NOT NULL,
  full_song   integer NOT NULL DEFAULT 0,
  power_hour_id integer NOT NULL, FOREIGN KEY(power_hour_id) REFERENCES power_hours(id)
);

CREATE INDEX IF NOT EXISTS tracks_power_hour_id_index ON tracks(power_hour_id);
CREATE UNIQUE INDEX IF NOT EXISTS tracks_power_hour_id_position_unique_index ON tracks(power_hour_id, position);

INSERT INTO power_hours(name) VALUES ("New Power Hour");
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 0, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 1, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 2, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 3, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 4, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 5, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 6, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 7, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 8, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 9, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 10, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 11, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 12, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 13, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 14, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 15, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 16, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 17, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 18, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 19, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 20, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 21, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 22, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 23, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 24, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 25, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 26, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 27, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 28, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 29, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 30, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 31, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 32, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 33, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 34, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 35, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 36, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 37, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 38, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 39, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 40, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 41, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 42, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 43, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 44, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 45, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 46, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 47, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 48, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 49, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 50, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 51, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 52, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 53, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 54, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 55, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 56, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 57, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 58, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1;
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) SELECT 59, "", "", 0, 0, 0, id FROM power_hours ORDER BY ROWID ASC LIMIT 1
