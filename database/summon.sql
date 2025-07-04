SELECT *
FROM marketing_ingestion_statistics.batch_columns_stats
ORDER BY insertion_timestamp DESC
LIMIT 10;

SELECT *
FROM marketing_ingestion_statistics.column_error_types
ORDER BY insertion_timestamp DESC
LIMIT 10;

SELECT *
FROM marketing_ingestion_statistics.feature_error_stats
ORDER BY insertion_timestamp DESC
LIMIT 10;

SELECT *
FROM marketing_ingestion_statistics.ingestion_metadata
ORDER BY insertion_timestamp DESC
LIMIT 10;
