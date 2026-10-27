-- Aufruf: psql --dbname=patient --username=postgres --file=/init/buch/sql/create-schema.sql

CREATE SCHEMA IF NOT EXISTS patient AUTHORIZATION patient;

ALTER ROLE patient SET search_path = 'patient';
ALTER ROLE patient SET default_tablespace = 'patientspace';
