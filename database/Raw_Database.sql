-- First time user, copy the content of each part below, uncomment it, and run 1 TIMES

-- Creating a Database
--DO $$ 
--BEGIN
--    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = "DSP_Project") THEN
--        CREATE DATABASE "DSP_Project";
--    END IF;
--END $$;


-- Connecting to the server
--\c "DSP_Project";


-- Creating a Schema
--CREATE SCHEMA IF NOT EXISTS dsp;

-- Setting a path to the Schema
-- SET search_path TO dsp;

-- Table: dsp.Clustering Marketing

-- DROP TABLE IF EXISTS dsp."Clustering_Marketing";

-- CREATE TABLE IF NOT EXISTS dsp."Clustering_Marketing"
-- (
-- )

--TABLESPACE pg_default;

--ALTER TABLE IF EXISTS dsp."Clustering_Marketing"      
--    OWNER to postgres;



DROP TABLE IF EXISTS dsp.marketing_data_raw;

	CREATE TABLE dsp.marketing_data_raw (
    gradyear INTEGER,
    gender TEXT,
    age TEXT,
    NumberOffriends INTEGER,
    basketball INTEGER,
    football INTEGER,
    soccer INTEGER,
    softball INTEGER,
    volleyball INTEGER,
    swimming INTEGER,
    cheerleading INTEGER, 
    baseball INTEGER,
    tennis INTEGER,
    sports INTEGER,
    cute INTEGER,
    sex INTEGER,
    sexy INTEGER,
    hot INTEGER,
    kissed INTEGER,
    dance INTEGER,
    band INTEGER,
    marching INTEGER, 
    music INTEGER,
    rock INTEGER,
    god INTEGER,
    church INTEGER,
    jesus INTEGER,
    bible INTEGER,
    hair INTEGER,
    dress INTEGER,
    blonde INTEGER, 
    mall INTEGER,
    shopping INTEGER,
    clothes INTEGER,
    hollister INTEGER,
    abercrombie INTEGER,
    die_flag INTEGER,  
    death_flag INTEGER, 
    drunk INTEGER,
    drugs INTEGER
);


-- copy dsp.marketing_data_raw 
-- FROM '../03_Clustering_Marketing.csv' 
-- DELIMITER ',' 
-- CSV HEADER;



