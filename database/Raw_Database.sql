-- Table: public.Clustering Marketing

-- DROP TABLE IF EXISTS public."Clustering Marketing";

CREATE TABLE IF NOT EXISTS public."Clustering Marketing"
(
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public."Clustering Marketing"
    OWNER to postgres;


DROP TABLE IF EXISTS marketing_data_raw;

	CREATE TABLE marketing_data_raw (
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


copy marketing_data_raw 
FROM 'C:\Program Files\PostgreSQL\17\data\03_Clustering_Marketing.csv' 
DELIMITER ',' 
CSV HEADER;



