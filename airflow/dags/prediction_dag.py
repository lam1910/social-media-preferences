import pendulum
from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException, AirflowException, AirflowFailException


def _check_for_new_data(ti) -> None:
    import os
    from pathlib import Path

    # Declare the good_data folder path
    p = Path('/opt/airflow/data/good_data')

    # Generate list with all the csv files in good_data folder
    files = list(p.glob('*.csv'))

    if files:

        # If the .txt file to track files to make predictions does not exist
        if not os.path.exists('/opt/airflow/data/good_data/prediction_checklist.txt'): 

            # Create .txt file to later write which files were used for predictions
            Path('/opt/airflow/data/good_data/prediction_checklist.txt').touch(exist_ok=True)

            # Pass the list of new file paths to next task make_predictions (paths are passed as PosixPath)
            ti.xcom_push(key='predict_new_files', value=files)

        # If the file to track predictions already exists
        else:
            # Get the prediction history of files...
            with open('/opt/airflow/data/good_data/prediction_checklist.txt', mode='r') as f:
                ingested: list = [csv.strip() for csv in f]

            # Check if there are new files
            new_files: list = [csv for csv in p.glob('*.csv') if str(csv) not in ingested]

            # If there are new files pass the list of paths to the next task
            if new_files:
                ti.xcom_push(key='predict_new_files', value=new_files)

            # If there are not new files, skip the task
            else:
                raise AirflowSkipException()

    # If good_data folder is empty skip the task
    else:
        raise AirflowSkipException()
    


def _make_predictions(ti) -> None:
    import requests
    import duckdb
    import json
    from airflow.hooks.base import BaseHook

    # Response handlers for HTTP status codes

    # HTTP Code 200
    def handle_200(new_files) -> None:
        # Append the name of files in prediction_checklist.txt file
        with open('/opt/airflow/data/good_data/prediction_checklist.txt', mode='a') as f:
            for csv in new_files:
                f.write(csv + '\n')


    # HTTP Code 400
    def handle_400() -> None:
        # Fail the task without retry
        raise AirflowFailException()


    # HTTP Code 500
    def handle_500() -> None:
        # Fail the task and wait for retry
        raise AirflowException()


    # Get the connection to the app API from the airflow metastore
    app_conn = BaseHook.get_connection('http_conn_fastapi')

    # API url
    url: str = f'http://{app_conn.host}:{app_conn.port}/predict'

    # Fetch new files from previous task
    new_files = [str(file_path) for file_path in ti.xcom_pull(key='predict_new_files')]

    # Initiate an in-memory duckdb database 
    conn = duckdb.connect(':memory:')

    # Load the csv file(s) at once and fetch a Pandas Dataframe
    prediction_data = conn.execute(f'SELECT * FROM read_csv({new_files});').fetchdf()
    
    # Parse the df to json
    prediction_json = prediction_data.to_json(orient='records')

    # Make the API call
    response = requests.post(url, json={"prediction_features":prediction_json})

    # Mapping status codes with corresponding handlers
    response_handler = {
        200: lambda: handle_200(new_files),
        400: handle_400,
        422: handle_400,
        500: handle_500,
    }

    # Call the corresponding function 
    response_handler.get(response.status_code, lambda: print(f'response_handler: status code {response.status_code} not found'))()


# Optional arguments for DAG execution. Number of retries when a task is set to retry and delay time between retries. 
args = { 
    'retries':3,
    'retry_delay':timedelta(minutes=1)
}

with DAG (
    dag_id='prediction_dag',
    schedule='*/2 * * * *',
    start_date=pendulum.now().subtract(minutes=2),
    catchup=False,
    max_active_runs=1,
    default_args=args
) as dag:


    check_for_new_data = PythonOperator(
        task_id='check_for_new_data',
        python_callable=_check_for_new_data
        )

    make_predictions = PythonOperator(
        task_id='xmake_predictions',
        python_callable=_make_predictions
        )

# Execution order of tasks
check_for_new_data >> make_predictions