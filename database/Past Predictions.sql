-- Table: public.past_predictions

-- DROP TABLE IF EXISTS public.past_predictions;

CREATE TABLE past_predictions (
    id SERIAL PRIMARY KEY,      -- Auto-incrementing unique ID
    data JSON NOT NULL,        -- Stores raw data in JSON format
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  
                                -- Auto-filled with current timestamp
    feature_1 FLOAT,            -- Example feature columns
    feature_2 FLOAT,  
    feature_3 FLOAT,  
    feature_4 FLOAT,  
    feature_5 FLOAT  
);

SELECT * FROM past_predictions ORDER BY insertion_timestamp DESC;



-- For testing
-- INSERT INTO past_predictions (data, feature_1, feature_2, feature_3, feature_4, feature_5)  
-- VALUES (
--    '{"customer_id": 101, "age": 25, "purchase_amount": 250.5}',  -- JSON data
--    0.9, 2.2, 3.1, 2.7, 1.3     -- Numerical features
-- );


-- SELECT data->>'customer_id' AS customer_id, 
--       feature_3, feature_4
-- FROM past_predictions;


-- DELETE FROM past_predictions
-- WHERE data->>'customer_id' = '101'; -- Deletes a specific entry

-- DELETE FROM past_predictions
-- WHERE id = (SELECT MAX(id) FROM past_predictions); -- Deletes most recent

-- ALTER SEQUENCE past_predictions_id_seq RESTART WITH 1; -- Resets auto-increment ID to 1


-- DELETE FROM past_predictions; -- Fully clears the table
-- TRUNCATE TABLE past_predictions RESTART IDENTITY; -- RESET EVERYTHING BUTTON