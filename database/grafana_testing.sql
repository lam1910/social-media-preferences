DROP TABLE IF EXISTS marketing_ingestion_statistics.batch_columns_stats;
DROP TABLE IF EXISTS marketing_ingestion_statistics.column_error_types;

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.batch_columns_stats (
    batch_id UUID PRIMARY KEY,
    num_expected_features INT NOT NULL,
    num_observed_features INT NOT NULL,
    num_new_features INT NOT NULL,
    num_missing_features INT NOT NULL,
    num_data_errors INT NOT NULL,
    num_samples INT NOT NULL,
    num_affected_samples INT NOT NULL,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO marketing_ingestion_statistics.batch_columns_stats (
    batch_id, num_expected_features, num_observed_features,
    num_new_features, num_missing_features, num_data_errors,
    num_samples, num_affected_samples, insertion_timestamp
) VALUES
('b89a46e1-ef23-4e5b-9c17-07e88b00f1a3', 40, 38, 1, 2, 120, 1000, 110, NOW()),
('e6a2b28b-45d4-4bf0-9292-0c2c71ea4b89', 40, 37, 0, 3, 95, 980, 90, NOW() - INTERVAL '3 minutes'),
('4d509a15-bb06-4f9e-9e1f-c4cae12a3e34', 40, 39, 2, 1, 105, 1005, 85, NOW() - INTERVAL '6 minutes'),
('9a0a0951-3be3-4f4d-90a2-91d8b8d11c72', 40, 35, 0, 5, 130, 970, 120, NOW() - INTERVAL '9 minutes'),
('f9637e27-40f4-4ec7-b17a-7892ae28d115', 40, 36, 1, 4, 90, 960, 80, NOW() - INTERVAL '12 minutes'),
('d7a78b8a-c8e5-418f-a26a-4f5d18d45b9c', 40, 40, 0, 0, 50, 1020, 40, NOW() - INTERVAL '15 minutes'),
('0f3beabc-0a91-4a24-880d-bdc871fac69d', 40, 37, 1, 3, 115, 985, 110, NOW() - INTERVAL '18 minutes'),
('c924bc81-68a2-4bdb-836f-9501a191a4f0', 40, 38, 0, 2, 70, 995, 65, NOW() - INTERVAL '21 minutes'),
('efc1e0b2-f34c-4c22-b582-21309726f78f', 40, 39, 1, 1, 85, 1000, 75, NOW() - INTERVAL '24 minutes'),
('7a2d03a0-7868-4de3-bd26-3b62c21b3812', 40, 36, 0, 4, 100, 975, 95, NOW() - INTERVAL '27 minutes');

UPDATE marketing_ingestion_statistics.batch_columns_stats
SET insertion_timestamp = NOW()
WHERE insertion_timestamp IS NULL;

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.column_error_types (
    batch_id UUID,
    feature TEXT,
    col_error_type TEXT,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO marketing_ingestion_statistics.column_error_types (
    batch_id, feature, col_error_type, insertion_timestamp
) VALUES
('68c558f2-4eb8-4154-8847-ad146b80ef04', 'volleyball', 'missing', NOW() - INTERVAL '0 minutes'),
('68c558f2-4eb8-4154-8847-ad146b80ef04', 'age', 'new', NOW() - INTERVAL '0 minutes'),

('fbd3ec6a-361a-4f60-8ade-ddac993aa1dc', 'drunk', 'new', NOW() - INTERVAL '5 minutes'),
('fbd3ec6a-361a-4f60-8ade-ddac993aa1dc', 'gradyear', 'missing', NOW() - INTERVAL '5 minutes'),
('fbd3ec6a-361a-4f60-8ade-ddac993aa1dc', 'volleyball', 'new', NOW() - INTERVAL '5 minutes'),

('0b87523e-9344-4057-8490-e74738ff1b17', 'drugs', 'missing', NOW() - INTERVAL '10 minutes'),

('5aafbc6e-fd29-4063-9369-b96d6403b246', 'gradyear', 'missing', NOW() - INTERVAL '15 minutes'),
('5aafbc6e-fd29-4063-9369-b96d6403b246', 'age', 'missing', NOW() - INTERVAL '15 minutes'),

('8acfb12f-234b-4e4d-8f36-2b6e49c9a3b1', 'gender', 'new', NOW() - INTERVAL '20 minutes'),

('dcbd1850-3f59-4bb3-9a42-2e9a259dddf9', 'drugs', 'new', NOW() - INTERVAL '25 minutes'),
('dcbd1850-3f59-4bb3-9a42-2e9a259dddf9', 'drunk', 'missing', NOW() - INTERVAL '25 minutes');

SELECT
    batch_id,
    feature,
    col_error_type,
    insertion_timestamp
FROM marketing_ingestion_statistics.column_error_types
ORDER BY insertion_timestamp DESC
LIMIT 10;

SELECT
  date_trunc('minute', insertion_timestamp) AS time,
  col_error_type AS error_type,
  COUNT(*) AS error_count
FROM marketing_ingestion_statistics.column_error_types
WHERE insertion_timestamp >= NOW() - INTERVAL '1 hour'
  AND col_error_type IN ('missing', 'new')
GROUP BY time, col_error_type
ORDER BY time, col_error_type;



SELECT
  batch_id,
  num_expected_features,
  num_observed_features,
  num_new_features,
  num_missing_features,
  num_data_errors,
  num_samples,
  num_affected_samples,
  insertion_timestamp
FROM marketing_ingestion_statistics.batch_columns_stats
ORDER BY insertion_timestamp DESC
LIMIT 10;

WITH total_errors AS (
  SELECT
    date_trunc('minute', insertion_timestamp) AS time,
    SUM(num_data_errors) AS total_errors,
    SUM(num_samples) AS total_samples
  FROM marketing_ingestion_statistics.batch_columns_stats
  WHERE insertion_timestamp >= NOW() - INTERVAL '1 hour'
  GROUP BY time
),
error_breakdown AS (
  SELECT
    date_trunc('minute', insertion_timestamp) AS time,
    col_error_type,
    COUNT(*) AS type_error_count
  FROM marketing_ingestion_statistics.column_error_types
  WHERE insertion_timestamp >= NOW() - INTERVAL '1 hour'
    AND col_error_type IN ('missing', 'new')
  GROUP BY time, col_error_type
)
SELECT
  t.time,
  e.col_error_type,
  ROUND(100.0 * e.type_error_count::numeric / NULLIF(t.total_samples, 0), 2) AS contribution_to_invalid_rate,
  ROUND(100.0 * e.type_error_count::numeric / NULLIF(t.total_errors, 0), 2) AS percentage_of_errors
FROM error_breakdown e
JOIN total_errors t ON e.time = t.time
ORDER BY t.time, e.col_error_type;


