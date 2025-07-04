	-- Column Error Types
WITH total_samples_per_batch AS (
  SELECT
    batch_id,
    SUM(num_samples) AS total_samples
  FROM marketing_ingestion_statistics.batch_columns_stats
  WHERE insertion_timestamp >= NOW() - INTERVAL '7 days'
  GROUP BY batch_id
),
error_counts AS (
  SELECT
    date_trunc('minute', insertion_timestamp) AS time,
    batch_id,
    col_error_type,
    COUNT(*) AS error_count
  FROM marketing_ingestion_statistics.column_error_types
  WHERE insertion_timestamp >= NOW() - INTERVAL '7 days'
  GROUP BY time, batch_id, col_error_type
)
SELECT
  e.time,
  e.col_error_type,
  ROUND(100.0 * SUM(e.error_count)::numeric / NULLIF(SUM(t.total_samples), 0), 2) AS invalid_rate
FROM error_counts e
JOIN total_samples_per_batch t ON e.batch_id = t.batch_id
GROUP BY e.time, e.col_error_type
ORDER BY e.time, e.col_error_type;

-- How many affected per file
SELECT
  m.file_name,
  f.feature,
  f.error_type,
  f.num_records,
  f.num_affected_records,
  s.num_data_errors,
  s.num_samples
FROM marketing_ingestion_statistics.feature_error_stats f
JOIN marketing_ingestion_statistics.ingestion_metadata m ON f.batch_id = m.batch_id
JOIN marketing_ingestion_statistics.batch_columns_stats s ON f.batch_id = s.batch_id
ORDER BY m.file_name, f.feature;

-- Percentage affected
SELECT
  f.batch_id,
  f.feature,
  f.error_type,
  f.num_affected_records,
  s.num_samples,
  ROUND(100.0 * f.num_affected_records::numeric / NULLIF(s.num_samples, 0), 2) AS percent_affected
FROM marketing_ingestion_statistics.feature_error_stats f
JOIN marketing_ingestion_statistics.batch_columns_stats s ON f.batch_id = s.batch_id
ORDER BY f.batch_id, f.feature;

-- Recent File Ingestion
SELECT *
FROM marketing_ingestion_statistics.ingestion_metadata
WHERE insertion_timestamp >= NOW() - INTERVAL '7 days'
ORDER BY insertion_timestamp DESC;

-- Experiment to see what errors greater expectation has the most
SELECT
  m.execution_timestamp AS time,
  f.feature,
  f.error_type,
  f.num_affected_records
FROM marketing_ingestion_statistics.feature_error_stats f
JOIN marketing_ingestion_statistics.ingestion_metadata m
  ON f.batch_id = m.batch_id
WHERE m.execution_timestamp >= NOW() - INTERVAL '7 days'
ORDER BY time;

-- Join for valid vs invalid
WITH total_samples_per_batch AS (
  SELECT
    batch_id,
    SUM(num_samples) AS total_samples
  FROM marketing_ingestion_statistics.batch_columns_stats
  GROUP BY batch_id
),
error_counts AS (
  SELECT
    batch_id,
    error_type,
    SUM(num_affected_records) AS error_count
  FROM marketing_ingestion_statistics.feature_error_stats
  GROUP BY batch_id, error_type
)
SELECT
  ec.error_type,
  ROUND(100.0 * SUM(ec.error_count)::numeric / NULLIF(SUM(ts.total_samples), 0), 2) AS contribution_to_invalid_rate
FROM error_counts ec
JOIN total_samples_per_batch ts ON ec.batch_id = ts.batch_id
GROUP BY ec.error_type
ORDER BY contribution_to_invalid_rate DESC;

-- Checking each error_type's error_rate
WITH total_per_minute AS (
  SELECT
    date_trunc('minute', insertion_timestamp) AS time,
    SUM(num_samples) AS total_samples
  FROM marketing_ingestion_statistics.batch_columns_stats
  GROUP BY time
),
error_breakdown AS (
  SELECT
    date_trunc('minute', insertion_timestamp) AS time,
    error_type,
    SUM(num_affected_records) AS error_count
  FROM marketing_ingestion_statistics.feature_error_stats
  GROUP BY time, error_type
)
SELECT
  t.time,
  e.error_type,
  ROUND(100.0 * e.error_count::numeric / NULLIF(t.total_samples, 0), 2) AS error_rate
FROM total_per_minute t
JOIN error_breakdown e ON e.time = t.time
ORDER BY t.time, e.error_type;



-- Grafana (Valid vs Invalid)
SELECT
  date_trunc('minute', insertion_timestamp) AS time,
  ROUND(100.0 * SUM(num_data_errors)::numeric / NULLIF(SUM(num_samples), 0), 2) AS invalid_rate,
  ROUND(100.0 - (100.0 * SUM(num_data_errors)::numeric / NULLIF(SUM(num_samples), 0)), 2) AS valid_rate
FROM marketing_ingestion_statistics.batch_columns_stats
WHERE $__timeFilter(insertion_timestamp)
GROUP BY time
ORDER BY time;


-- Experiment (Missing & New Errors)
SELECT
  date_trunc('minute', insertion_timestamp)::timestamp AS time,
  COUNT(*) AS missing_errors
FROM marketing_ingestion_statistics.column_error_types
WHERE $__timeFilter(insertion_timestamp)
  AND col_error_type = 'missing'
GROUP BY time
ORDER BY time;


SELECT
  date_trunc('minute', insertion_timestamp)::timestamp AS time,
  COUNT(*) AS new_errors
FROM marketing_ingestion_statistics.column_error_types
WHERE $__timeFilter(insertion_timestamp)
  AND col_error_type = 'new'
GROUP BY time
ORDER BY time;


