-- Aufruf: psql --dbname=postgres --username=postgres --file=/init/buch/sql/create-db.sql

CREATE USER buch PASSWORD 'p';
CREATE DATABASE buch;
GRANT ALL ON DATABASE buch TO buch;

CREATE TABLESPACE buchspace OWNER buch LOCATION '/tablespace/buch';
