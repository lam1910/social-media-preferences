-- Table: public.past_predictions

-- DROP TABLE IF EXISTS public.past_predictions;

CREATE TABLE past_predictions (
    id SERIAL PRIMARY KEY,      
    features JSON NOT NULL,        
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
    prediction integer            
);

SELECT * FROM past_predictions ORDER BY insertion_timestamp DESC;


-- SELECT features ->>'xxxxx' AS xxxxx,      
-- FROM past_predictions;


-- DELETE FROM past_predictions
-- WHERE features->>'xxx_id' = 'ID No.'; -- Deletes a specific entry

-- DELETE FROM past_predictions
-- WHERE id = (SELECT MAX(id) FROM past_predictions); -- Deletes most recent

-- ALTER SEQUENCE past_predictions_id_seq RESTART WITH 1; -- Resets auto-increment ID to 1


-- DELETE FROM past_predictions; -- Fully clears the table
-- TRUNCATE TABLE past_predictions RESTART IDENTITY; -- RESET EVERYTHING BUTTON