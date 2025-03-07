from pendulum import datetime
from airflow import DAG
from airflow.decorators import task


with DAG (
    dag_id='ingestion_dag',
    schedule='*/1 * * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1
) as dag:

    @task.bash
    def read_data(ti):
        from pathlib import Path
        import duckdb
        import subprocess
        
        # Declare the raw_data folder path
        p = Path('/opt/airflow/data/raw_data')

        # Check if there are available csv files to ingest
        if list(p.glob('*.csv')):

            # Pick a random csv file from the raw_data directory
            random_file_path = subprocess.getoutput(f'bash $AIRFLOW_HOME/scripts/shell/random_file.sh ')

            # Read its contents with duckdb
            conn = duckdb.connect(':memory:')
            current_file = conn.execute(f'SELECT * FROM read_csv("{random_file_path}");')

            # Push the Dataframe via XCOM
            ti.xcom_push(key='new_raw_data', value=current_file.fetchdf())

            # Return the path of the random csv via XCOM
            return f'echo "{random_file_path}"'
        
        else:
            # If there are no files, skip
            return 'exit 99;'
    
    _read_data = read_data()


    @task.bash
    def save_file(ti):
        # Read the XCOM with key "return_value" pushed by read_data task and move file to good data folder
        return 'mv {{ ti.xcom_pull(key="return_value") }} $AIRFLOW_HOME/data/good_data && echo {{ ti.xcom_pull(key="return_value") }}'

    _save_file = save_file()

# Execution order of tasks
_read_data >> _save_file