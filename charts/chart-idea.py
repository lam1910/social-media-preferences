import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import random

error_example = {'Missing label': 100, 'Gender not recognized': 20, 'Age not in range': 43}

colors = sns.color_palette('pastel')[0:5]

plt.pie(error_example.values(), labels=error_example.keys(), colors=colors, autopct='%.0f%%')
plt.title('Errors')
plt.savefig('charts/images/error_chart.png')


# Define parameters
years = [2024, 2025]
months = list(range(1, 13))
error_types = ['Missing label', 'Gender not recognized', 'Age not in range']
num_rows = 50  # Number of rows to generate

# Generate random data
np.random.seed(42)  # For reproducibility
data = {
    "Year": np.random.choice(years, num_rows),
    "Month": np.random.choice(months, num_rows),
    "Type of Error": np.random.choice(error_types, num_rows),
    "Number of Errors": np.random.randint(5, 50, num_rows)  # Random error count
}

# Create DataFrame
df_errors = pd.DataFrame(data)

df_errors = df_errors.groupby(['Month', 'Type of Error']).agg(
    {
        'Number of Errors': 'sum'
    }
)
df_errors = df_errors.reset_index()
a = sns.lineplot(data=df_errors, x='Month', y='Number of Errors', hue='Type of Error', estimator=None)
ax = sns.histplot(
    data=df_errors, x='Month', hue='Type of Error', bins=12, weights='Number of Errors', multiple='stack', shrink=0.8
)
ax.set_ylabel('Number of Errors')
plt.savefig('charts/images/error_chart_by_month.png')
plt.show()

# Parameters
start_date = "2025-01-01 00:00"
end_date = "2025-01-31 22:00"
interval = "2H"  # 2-hour interval

# Generate timestamps
timestamps = pd.date_range(start=start_date, end=end_date, freq=interval)
nb=50

# Generate API processing times
processing_times = [random.uniform(1, 3) for _ in range(nb)]  # Normal values: 50
processing_times.append(6.0)  # Special case of 10 seconds at the end
processing_times.extend([random.uniform(1, 3) for _ in range(nb)])  # Normal values: 50
processing_times.append(6.0)  # Special case of 10 seconds at the end
processing_times.extend([random.uniform(1, 3) for _ in range((nb+1) * 2, len(timestamps))])

# Combine into a DataFrame
df_time_avg = pd.DataFrame({
    "Timestamp": timestamps,
    "API_Processing_Time": processing_times
})
df_time_avg['Timestamp'] = pd.to_datetime(df_time_avg.Timestamp)
df_time_avg['Hour'] = df_time_avg.Timestamp.dt.hour
df_time_avg['Day'] = df_time_avg.Timestamp.dt.day
# Create a figure and set its size
plt.figure(figsize=(21,12))
ax = sns.lineplot(data=df_time_avg, x='Timestamp', y='API_Processing_Time', estimator=None, marker=False)
# get current xtick labels
xticks = ax.get_xticks()
# convert all xtick labels to selected format from ms timestamp
ax.set_xticklabels([pd.to_datetime(tm, unit='d').strftime('%Y-%m-%d') for tm in xticks],
 rotation=50)
ax.set_title('Average API Processing Time')
plt.savefig('charts/images/avg_api_speed.png')
plt.show()

# Define parameters
years = [2024, 2025]
months = list(range(1, 13))
sport_types = ['basketball','football','soccer','softball','volleyball','swimming','cheerleading','baseball','tennis','sports']
num_rows = 100  # Number of rows to generate

# Generate random data
np.random.seed(42)  # For reproducibility
data = {
    "Year": np.random.choice(years, num_rows),
    "Month": np.random.choice(months, num_rows),
    "Sport": np.random.choice(sport_types, num_rows),
    "Number of post": np.random.randint(16, 127, num_rows)  # Random error count
}
df_sport = pd.DataFrame(data)

df_sport = df_sport.groupby(['Month', 'Sport']).agg(
    {
        'Number of post': 'sum'
    }
)
df_sport = df_sport.reset_index()
a = sns.lineplot(data=df_sport, x='Month', y='Number of post', hue='Sport', estimator=None)
ax = sns.histplot(
    data=df_sport, x='Month', hue='Sport', bins=12, weights='Number of post', multiple='stack', shrink=0.8
)
ax.set_ylabel('Number of Post')
ax.set_xlabel('Month')
ax.set_title('Number of sport post per month')
plt.savefig('charts/images/sport_chart_by_month.png')
plt.show()

cols = [
    'basketball','football','soccer','softball','volleyball','swimming','cheerleading','baseball','tennis','sports',
    'cute','sex','sexy','hot','kissed','dance','band','marching','music','rock','god','church','jesus','bible','hair',
    'dress','blonde','mall','shopping','clothes','hollister','abercrombie','die','death','drunk','drugs'
]
rows = list(range(7))
rows = ['Group ' + str(idx) for idx in rows]

d_hm = {}
for row in rows:
    d_hm[row] = np.random.randint(0, 127, len(cols))

df_hm = pd.DataFrame.from_dict(d_hm, orient='index', columns=cols)

ax = sns.heatmap(data=df_hm.T, fmt='d', cmap='YlGnBu')
ax.set_xlabel('Group')
ax.set_ylabel('Keywords')
ax.set_title('Keyword of each groups')
plt.savefig('charts/images/keywords_chart.png')
plt.show()
