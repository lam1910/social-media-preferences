from pendulum import datetime
from airflow import DAG, Dataset
from airflow.decorators import task

# ToDo:
# Change the schedule
# Change the start_date


with DAG (
    dag_id = 'ingestion-dag',
    schedule = '@daily',
    start_date = datetime(2025, 1, 1),
    catchup = False
) as dag:

    @task.bash
    def read_data(ti):
        from pathlib import Path
        import pandas as pd
        import subprocess
        
        # Declare the raw_data folder path
        p = Path('/opt/airflow/data/raw_data')

        # Check if there are available csv files to ingest
        if list(p.glob('*.csv')):
            # Pick a random csv file from the raw_data directory
            random_file = subprocess.getoutput(f'bash $AIRFLOW_HOME/scripts/shell/random_file.sh ')
            # Read its contents
            current_data = pd.read_csv(random_file)
            # Push the Dataframe via XCOM
            ti.xcom_push(key='new_raw_data', value=current_data)
            # Return the path of the random csv via XCOM
            return f'echo "{random_file}"'
        else:
            # If there are no files, mark the task execution state as skipped
            return 'exit 99;'
    
    _read_data = read_data()


    @task.bash
    def save_file(ti):
        # df = ti.xcom_pull(key='new_raw_data') Not in use for the moment
        # Read the XCOM with key "return_value" pushed by read_data task and move file to good data folder
        return 'mv {{ ti.xcom_pull(key="return_value") }} $AIRFLOW_HOME/data/good_data'

    _save_file = save_file()


# Execution order of tasks
_read_data >> _save_file