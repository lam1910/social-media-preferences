# Data Science in production project instructions

For the data science in production course, you will be developing an ML powered application. This project will be developed in a group of 3 to 4 people and will represent 60% of your final grade.

You are free to choose the use case you want (energy consumption prediction, fraud detection, etc). However, it should be a simple use case (the modeling part should not take you more than 2 hours) as the goal of the project is to focus more on the operationalization of a Machine Learning powered application and not the ML model development step.

Your final application will be composed of the following components (technologies to use between parenthesis):

- A user interface where the user can make on-demand predictions and view past predictions ([streamlit](https://streamlit.io/))
- An API for exposing the ML model ([FastAPI](https://fastapi.tiangolo.com/)) and saving the predictions to the database
- An SQL database for saving data (predictions along with the used features, ...)
([PostgreSQL](https://www.postgresql.org/), [SQLAlchemy](https://www.sqlalchemy.org/))
- A prediction job to make scheduled predictions each n mins ([Airflow](https://airflow.apache.org/))
- An ingestion job to ingest and validate the data quality ([great expectations](https://greatexpectations.io/) or [TensorFlow Data Validation](https://www.tensorflow.org/tfx/guide/tfdv#overview))
- A monitoring dashboard to monitor data quality problems of the ingested data and the drift of training and serving data ([Grafana](https://grafana.com/))


These components will interact as shown in this architecture:

<p align="center">
    <img
        src="../images/project-architecture.png"
        alt="Project architecture"
    />
</p>

# User interface

To make predictions and visualize past prediction, you will develop a webapp that is composed of 2 webpages:

1. **Prediction page**: for making single and multi prediction. It should contain:
- A **form** to fill in the features for a single sample prediction.
- An **upload button** to upload a csv file for making multiple predictions: the file should contain the inference data in the correct format without labels (just saying :wink: )
- A **predict button** to make on-demand predictions by calling the model API service

**Note**:

- When predictions are returned by the model service (API), they need to be displayed as a dataframe along with the features used for making the prediction
- For single and multi predictions, you should not save the data in a csv file and send the file path to the API, you should read the data and send it instead

2. **Past predictions page** for visualizing past predictions. It should contain:
- A **date selection component** to select the start and end date
- A **prediction source drop list** to select the source of the predictions to retrieve
  - `webapp`: to show only predictions made using the webapp
  - `scheduled predictions`: to show predictions made using the prediction job
  - `all`: to show predictions made from the webapp or the prediction job


# Model service (API)

To make predictions, the model will not be stored in the webapp as it will be used by multiple services (webapp and prediction job). It will instead be exposed as API that the webapp and the prediction job can call to request predictions.

This API will be used for:

- serving the model (making predictions)
- saving the model predictions and used features in the database
- returning past predictions and used features to the webapp

It should contain the following endpoints:

- `predict`: for making model predictions from the the webapp or the prediction job (it should be used for single and multi prediction and it should not take a file as input)
- `past-predictions`: to get the model past predictions along with the used features

# Database

To store past predictions and data quality issues, you be putting in place a `PostgreSQL` database that will be used by:

1. The model service to save the model predictions and query them (write + read)
2. The data ingestion job to save data quality problems (write)
3. The dashboard to display data quality problems and data drift (read)


# Data ingestion job

To simulate having a continuous flow of data, you will be developing a data ingestion job for:

- Ingesting new data each 1 minute
- Validating the data quality of the ingested data
- Raising alerts if any data quality issue
- Saving data issues in the database for monitoring

## Notebook to generate data issues

As your dataset do not include too many data errors, you have to generate these errors yourself in your raw dataset. Example of data errors:

- A required feature (column) is missing
- Missing values in a required column
- Unknown values for a given feature (expected country values: China, India, Lebanon. new value: France)
- Wrong value for a given feature (-12 for the Age or child for gender, ...)
- A string value in a numerical column
- ...

You should generate a minimum of 7 error types. Duting the follow up session, you will need to demo the different error types in a notebook

## Script to split the dataset

To ingest new data, you need first to split your main dataset in multiple files and store them in a folder named *raw-data* that will feed your ingestion job as shown below. To do that, you need to create a python script that takes your dataset path, the path of *raw-data* folder and **the number of files to generate** (**not** the number of rows per file)

<p align="center">
    <img
        src="../images/project-data-preparation-for-ingestion-job.png"
        alt="Data preparation for ingestion job"
    />
</p>

## Data ingestion dag

In the data ingestion job, at each dag execution, you will:

1. Read **randomly** one file from the *raw-data* folder (you can delete the file afterward) (`read-data` task)
2. Validate its quality using *Great-expectation* or *TFDV* (`validate-data` task)
3. Save some statistics about the detected data problems to the database (statistics and not the rows themselves!!) along with statistics about the ingested data (nb rows, nb valid rows, nb invalid rows, filename, etc) (`save-statistics` task)
4. Generate a report of the data problems (for *great-expectations*, you can use [Data Docs](https://docs.greatexpectations.io/docs/reference/learn/terms/data_docs) to generate a html file) and raises an alert to the user using *teams* notification (`send-alerts` task). In this alert you need to include the followings:
   - Criticality of the data problem (high, medium, low)
   - Summary of the errors
   - Link to the report
5. Splits the ingested file if needed or move it (`save-file` task)
    - If no data quality issues found, store the file in a folder named *good_data*
    - If all rows have data problems, store the file in a folder named *bad_data*
    - If some rows have problems and some don't, split the file in 2 (one for *good_data* the other for *bad_data* folders)
    <p align="center">
        <img
            src="../images/project-data-quality-validation.png"
            alt="Split good and bad data"
        />
    </p>

As your dataset do not include too many data errors, you have to generate these errors yourself in your raw dataset. Example of data errors:

- A required feature (column) is missing
- Missing values in a required column
- Unknown values for a given feature (expected country values: China, India, Lebanon. new value: France)
- Wrong value for a given feature (-12 for the Age or child for gender, ...)
- A string value in a numerical column
- ...

The data ingestion dag should include the following tasks:

- read-data: reads one file randomly from *raw-data* and return the file path
- validate-data: checks for any data errors in the file and determines the data errors criticality
- save-statistics: saves statistics about the ingested data to the database
- send-alerts: generates the data validation report and sends an alert using *teams*
-  split-and-save-data: splits the file in 2 files if needed and saves them in folder *bad-data* or *good-data*

The tasks `send-alerts`, `split-and-save-data` and `save-data-errors` should be executed in parallal

<p align="center">
    <img
        src="../images/project-ingestion-dag.png"
        alt="Ingestion dag"
    />
</p>

# Prediction job

Now that you have your continous flow of data, you can put in place a prediction job to make scheduled predictions on the ingested data. Unlike the webapp where the user can make on-demand predictions, this job will be executed each 2 minutes automatically.

It should be composed of 2 tasks:

1. `check_for_new_data`: in this task, you will check if there are any new ingested files in the *good_data* folder. If so, you need to pass the list of these files to the next task, otherwise mark the dag run status as `skipped`([Dag run status](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html#dag-run-status)). **The dag run should be marked as skipped and not only the `make_predictions` task**
2. `make_predictions`: in this task, you will read the files passed by the `check_for_new_data` task and make API call to the model service to make predictions

**Note: You should not remove, move or rename the files in the folder *good_data* !**, you need to find another mechanism to determine what are the newly ingested files.

- Prediction dag tasks

<p align="center">
    <img
        src="../images/project-prediction-dag.png"
        alt="Prediction dag"
    />
</p>

- Prediction dag skipped when there is no newly ingested data

<p align="center">
    <img
        src="../images/project-prediction-dag-skipped.png"
        alt="Prediction dag when skipped"
    />
</p>

# Monitoring dashboards

To monitor the quality of the ingested data and the possible issues in the model, you will be developing **2 dashboards** using `Grafana`.

These dashboards should be
- querying data from the database
- updated in real time (in the defense, I expect the graphs to change after each data ingestion and prediction)

Make sure to:
- use the thresholds in the different graphs so that the graph colors will have a meaning (green ✅, orange ⚠️, red ❌)
- raise Grafana alerts in certain cases (example: all ingested data have errors, model predicting zero, ...)


For the 2 dashboards, make sure to use temporal statistics, for example:
- Histogram about the different types of the detected data problems in the last 10 min
- Average predictions in the last 10 min
- Histogram of the predicted classes in the last 30 min
- etc

### Ingested data monitoring dashboard:

This dashboard will be used by data operations team to monitor the ingested data problems. So the different graphs should be helpful for them to monitor the data and take actions to solve the encountered problems

Example of ingested data errors:
- Errors related to missing values are increasing or decreasing in the hours
- The amount of files with missing required features is decreasing

Example of graphs:
- Temporal graph with the % of invalid data samples compared to valid data samples in the last 10 min, etc
- Number of detected data problems per category at each ingestion
- ... 

### Data drift and prediction issues dashboard

This dashboard will be used by ML engineers and data scientist to detect ML model or application issues

Example of model errors:
- data drift between training and serving data: during training, users average age was 45 and in serving, it is 60
- Model making unexpected prediction for a period of time: predicting 0 for the house price, always predcting fraud, etc


Good luck 🤞 🍀
