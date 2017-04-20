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
  start_time  integer NOT NULL,
  full_song   integer NOT NULL DEFAULT 0,
  power_hour_id integer NOT NULL, FOREIGN KEY(power_hour_id) REFERENCES power_hours(id)
);

CREATE INDEX IF NOT EXISTS tracks_power_hour_id_index ON tracks(power_hour_id);
CREATE UNIQUE INDEX IF NOT EXISTS tracks_power_hour_id_position_unique_index ON tracks(power_hour_id, position);

INSERT INTO power_hours(name) VALUES ("New Power Hour");
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (0, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (1, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (2, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (3, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (4, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (5, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (6, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (7, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (8, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (9, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (10, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (11, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (12, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (13, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (14, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (15, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (16, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (17, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (18, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (19, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (20, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (21, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (22, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (23, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (24, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (25, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (26, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (27, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (28, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (29, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (30, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (31, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (32, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (33, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (34, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (35, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (36, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (37, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (38, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (39, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (40, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (41, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (42, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (43, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (44, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (45, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (46, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (47, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (48, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (49, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (50, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (51, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (52, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (53, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (54, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (55, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (56, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (57, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (58, "", "", 0, 0, 0, 1);
INSERT INTO tracks(position, url, title, length, start_time, full_song, power_hour_id) VALUES (59, "", "", 0, 0, 0, 1)
