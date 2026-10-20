-- Aufruf: psql --dbname=buch --username=postgres --file=/init/buch/sql/create-schema.sql

CREATE SCHEMA IF NOT EXISTS buch AUTHORIZATION buch;

ALTER ROLE buch SET search_path = 'buch';
ALTER ROLE buch SET default_tablespace = 'buchspace';
