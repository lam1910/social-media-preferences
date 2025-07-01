from pendulum import datetime # type: ignore

from airflow import DAG
from airflow.decorators import task # type:ignore
from airflow.models import Variable # type:ignore
from airflow.operators.dummy import DummyOperator # type:ignore 

from modules.mock_data_issues.generate_data_issues import generate_data_issues #type: ignore

from great_expectations import ExpectationSuite
import great_expectations.expectations as gxe # type: ignore
from great_expectations_provider.operators.validate_dataframe import ( # type: ignore
    GXValidateDataFrameOperator)


def retrieve_df_for_gx_validation():
    import duckdb # type: ignore
    
    conn = duckdb.connect('ingest.ddb')
    df = conn.execute('SELECT * FROM latest').fetchdf()
    return df


expectation_suite = ExpectationSuite(
    name='marketing_data_validation',
    expectations = [
        # 1. Number of features expected
        gxe.ExpectTableColumnCountToEqual(value=40),
        # 2. New features and # 3. Missing featuress
        gxe.ExpectTableColumnsToMatchSet(column_set=[
            'gradyear', 'gender', 'age', 
            'NumberOffriends', 'basketball','football', 
            'soccer', 'softball', 'volleyball', 
            'swimming','cheerleading', 'baseball', 
            'tennis', 'sports', 'cute', 
            'sex', 'sexy','hot', 'kissed', 
            'dance', 'band', 'marching', 
            'music', 'rock', 'god',
            'church', 'jesus', 'bible', 
            'hair', 'dress', 'blonde', 
            'mall','shopping', 'clothes', 
             'hollister', 'abercrombie', 'die', 
            'death','drunk', 'drugs']
            ),
        # 4. New Categories
        gxe.ExpectColumnValuesToBeInSet(
            column='gender', value_set=['F', 'M', 'NA']
        ),
        gxe.ExpectColumnValuesToBeBetween(
            column='gradyear', min_value=2006, max_value=2009
        ),
        gxe.ExpectColumnMaxToBeBetween(
            column='NumberOffriends', min_value=0, max_value=1000
        ),
        # 5. Null Values
        gxe.ExpectColumnValuesToNotBeNull(
            column='gradyear'
        ),
        gxe.ExpectColumnValuesToNotBeNull(
            column='gender'
        ),
        gxe.ExpectColumnValuesToNotBeNull(
            column='NumberOffriends'
        ),
        gxe.ExpectColumnValuesToNotBeNull(
            column='age'
        ),
        gxe.ExpectColumnValuesToNotBeNull(
            column='drunk'
        ),
        gxe.ExpectColumnValuesToNotBeNull(
            column='drugs'
        ),
        gxe.ExpectColumnValuesToNotBeNull(
            column='volleyball'
        ),
        # 6. Error Type
        gxe.ExpectColumnValuesToBeOfType(
            column='volleyball', type_='int16'
        ),
        gxe.ExpectColumnValuesToBeOfType(
            column='drugs', type_='int16'
        ),
        gxe.ExpectColumnValuesToBeOfType(
            column='drunk', type_='int16'
        ),
        # 7. Wrong input
        gxe.ExpectColumnValuesToMatchRegex(
            column="age",
            regex=r"^\d+(\.\d+)?$"
        )
    ]
)


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
        import duckdb # type: ignore
        import subprocess

        mock_issues = True if Variable.get('mock_issues') == 'True' else False

        print(f"Are we mocking issues today? {'yes' if mock_issues else 'no'}")
        # Declare the raw_data folder path
        p = Path('/opt/airflow/data/raw_data')

        # Check if there are available csv files to ingest
        if list(p.glob('*.csv')):

            # Pick a random csv file from the raw_data directory
            random_file_path = subprocess.getoutput(f'bash $AIRFLOW_HOME/scripts/shell/random_file.sh ')

            # Read its contents with duckdb
            conn = duckdb.connect('ingest.ddb')
            conn.execute(f"CREATE OR REPLACE TABLE latest AS SELECT * FROM read_csv_auto('{random_file_path}', nullstr='');")
            df = conn.execute('SELECT * FROM latest').fetchdf()

            if mock_issues:
                print("Generating data issues...")
                df = generate_data_issues(dataframe=df, chances=0.5)
                conn.execute('CREATE OR REPLACE TABLE latest AS SELECT * FROM df')

            df = conn.execute('SELECT * FROM latest').fetchdf()
            print(f'Read DF columns: {df.columns}')
            print(f'Read DF num cols: {len(df.columns)}')
            
            # Return the path of the random csv via XCOM
            return f'echo "{random_file_path}"'
        
        else:
            # If there are no files, skip
            return 'exit 99;'
    
    _read_data = read_data()

    
    validate_data = GXValidateDataFrameOperator(
        task_id="validate_data",
        configure_dataframe=retrieve_df_for_gx_validation,
        expect=expectation_suite,
        context_type="ephemeral",
        result_format="COMPLETE",
    )


    @task.bash
    def save_file(ti):
        import duckdb
        
        conn = duckdb.connect('ingest.ddb')
        df = conn.execute('SELECT * FROM latest').fetchdf()
        print(f'DF columns: {df.columns}')
        print(f'Number of columns: {len(df.columns)}')
        current_file_name = ti.xcom_pull(task_ids="read_data", key="return_value").split('/')[5]
        bad_data_save_path = f'/opt/airflow/data/bad_data/bad_{current_file_name}'
        good_data_save_path = f'/opt/airflow/data/good_data/{current_file_name}'
        
        gx_output = ti.xcom_pull(task_ids='validate_data', key='return_value')
        successful_validation = gx_output['success']
        successful_feature_validation = False

        print(f'Successful validation? {successful_validation}')
        print(f'Expected features? {successful_feature_validation}')

        
        for expectation in gx_output['expectations']:
            if (expectation['expectation_type'] == 'expect_table_columns_to_match_set' and expectation['success'] == True):
                successful_feature_validation = True
                break

        if successful_validation and successful_feature_validation:
            conn.execute(
                    f"""
                    COPY (
                        SELECT *
                        FROM latest
                    ) TO '{good_data_save_path}' (HEADER, DELIMITER ',');
                    """
                )

        
        # If columns set matches:
        if not successful_validation and successful_feature_validation:          
            bad_data_idx = []
            for expectation in gx_output['expectations']:
                if expectation['success'] == False:
                    column = expectation['kwargs'].get('column')
                    idx_list = expectation['result'].get('unexpected_index_list')
                    if column and idx_list:
                        bad_data_idx.extend(expectation['result']['unexpected_index_list'])
            
            if bad_data_idx:
                bad_data_idx = ', '.join(str(idx) for idx in {*bad_data_idx})    
            # Retrieving the bad rows
                conn.execute(
                    f"""
                    COPY (
                        WITH bad_data AS (
                            SELECT *, row_number() OVER () - 1 AS rn
                            FROM latest
                        )
                        SELECT * EXCLUDE rn
                        FROM bad_data
                        WHERE rn IN ({bad_data_idx})
                    ) TO '{bad_data_save_path}' (HEADER, DELIMITER ',');
                    """
                )
            
            # Retrieving the good rows
                conn.execute(
                    f"""
                    COPY (
                        WITH good_data AS (
                            SELECT *, row_number() OVER () - 1 AS rn
                            FROM latest
                        )
                        SELECT * EXCLUDE rn
                        FROM good_data
                        WHERE rn NOT IN ({bad_data_idx})
                    ) TO '{good_data_save_path}' (HEADER, DELIMITER ',');
                    """
                )
            else:
                conn.execute(
                    f"""
                    COPY (
                        SELECT *
                        FROM latest
                    ) TO '{good_data_save_path}' (HEADER, DELIMITER ',');
                    """
                )

        # If column set does not matches
        elif not successful_validation and not successful_feature_validation:
            conn.execute(
                    f"""
                    COPY (
                        SELECT *
                        FROM latest
                    ) TO '{bad_data_save_path}' (HEADER, DELIMITER ',');
                    """
                )
        # Read the XCOM with key "return_value" pushed by read_data task and move file to good data folder
        return 'rm {{ ti.xcom_pull(task_ids="read_data", key="return_value") }} && echo {{ ti.xcom_pull(task_ids="read_data", key="return_value") }}'
    
    _save_file = save_file()

    dummy_task = DummyOperator(task_id='send_alerts')

    dummy_task2 = DummyOperator(task_id='save_statistics')


# Execution order of tasks
_read_data >> validate_data >> [_save_file, dummy_task, dummy_task2]