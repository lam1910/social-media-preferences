-- SET search_path TO dsp;

-- Table: dsp.past_predictions

-- DROP TABLE IF EXISTS dsp.past_predictions;

CREATE TABLE dsp.past_predictions (
    id SERIAL PRIMARY KEY,      
    features JSON NOT NULL,        
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    prediction integer            
);

-- SELECT * FROM dsp.past_predictions ORDER BY insertion_timestamp DESC;


-- SELECT features ->>'xxxxx' AS xxxxx,      
-- FROM dsp.past_predictions;


-- DELETE FROM dsp.past_predictions
-- WHERE features->>'xxx_id' = 'ID No.'; -- Deletes a specific entry

-- DELETE FROM dsp.past_predictions
-- WHERE id = (SELECT MAX(id) FROM dsp.past_predictions); -- Deletes most recent

-- ALTER SEQUENCE dsp.past_predictions_id_seq RESTART WITH 1; -- Resets auto-increment ID to 1


-- DELETE FROM dsp.past_predictions; -- Fully clears the table
-- TRUNCATE TABLE dsp.past_predictions RESTART IDENTITY; -- RESET EVERYTHING BUTTON