CREATE SCHEMA IF NOT EXISTS marketing_ingestion_statistics;

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.batch_columns_stats (
    batch_id UUID PRIMARY KEY,
    num_expected_features INT CHECK (num_expected_features >= 0) NOT NULL,
    num_observed_features INT CHECK (num_observed_features >= 0) NOT NULL,
    num_new_features INT CHECK (num_new_features >= 0) NOT NULL,
    num_missing_features INT CHECK (num_missing_features >= 0) NOT NULL,
    num_data_errors INT CHECK (num_data_errors >= 0) NOT NULL,
    num_samples INT CHECK (num_samples >= 0) NOT NULL,
    num_affected_samples INT CHECK (num_affected_samples >= 0) NOT NULL,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.column_error_types (
    id UUID PRIMARY KEY,
    batch_id UUID NOT NULL REFERENCES marketing_ingestion_statistics.batch_columns_stats(batch_id),
    feature TEXT NOT NULL,
    col_error_type TEXT NOT NULL,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.feature_error_stats (
    id UUID PRIMARY KEY,
    batch_id UUID NOT NULL REFERENCES marketing_ingestion_statistics.batch_columns_stats(batch_id),
    feature TEXT NOT NULL,
    error_type TEXT NOT NULL,
    num_records INT CHECK (num_records >= 0) NOT NULL,
    num_affected_records INT CHECK (num_affected_records >= 0) NOT NULL,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.sample_value_discovery (
    id UUID PRIMARY KEY,
    batch_id UUID NOT NULL REFERENCES marketing_ingestion_statistics.batch_columns_stats(batch_id),
    feature_error_id UUID NOT NULL REFERENCES marketing_ingestion_statistics.feature_error_stats(id),
    feature TEXT NOT NULL,
    value TEXT NOT NULL,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS marketing_ingestion_statistics.ingestion_metadata (
    batch_id UUID PRIMARY KEY REFERENCES marketing_ingestion_statistics.batch_columns_stats(batch_id),
    file_name TEXT NOT NULL,
    execution_timestamp TIMESTAMP NOT NULL,
    insertion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);
