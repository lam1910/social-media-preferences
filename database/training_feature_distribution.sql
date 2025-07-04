CREATE TABLE IF NOT EXISTS training_feature_distribution (
    feature_name TEXT NOT NULL,
    value INTEGER NOT NULL,
    count INTEGER NOT NULL,
    PRIMARY KEY (feature_name, value)
);
