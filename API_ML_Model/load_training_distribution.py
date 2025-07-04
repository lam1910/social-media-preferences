import pandas as pd
from database import engine
from sqlalchemy import text

# 1. Load your CSV file
file_path = "final_selected_df.csv"
df = pd.read_csv(file_path)

# 2. Initialize empty list to collect counts
rows = []

# 3. For each feature, compute counts
features = ["age", "gradyear", "NumberOffriends"]

for feature in features:
    counts = df[feature].value_counts().reset_index()
    counts.columns = ["value", "count"]
    counts["feature_name"] = feature
    rows.append(counts)

# 4. Concatenate all counts into one DataFrame
result = pd.concat(rows, ignore_index=True)

# 5. Reorder columns to match table
result = result[["feature_name", "value", "count"]]

# 6. Clear previous records


with engine.connect() as conn:
    conn.execute(text("DELETE FROM training_feature_distribution"))
    conn.commit()


# 7. Insert new snapshot
result.to_sql(
    "training_feature_distribution",
    engine,
    if_exists="append",
    index=False
)

print("✅ Training distribution snapshot successfully loaded into the database.")
