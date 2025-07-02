from pendulum import datetime # type: ignore

from airflow import DAG
from airflow.decorators import task # type:ignore
from airflow.models import Variable # type:ignore
from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.dummy import DummyOperator # type:ignore 
from airflow.operators.python import PythonOperator

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


def parse_gxe_output(gxe_output: dict, file_name: str) -> dict: 
    expectations = gxe_output.get("expectations", [])

    num_expected_features = None
    num_observed_features = None
    expected_set = set()
    observed_set = set()

    for e in expectations:
        if e["expectation_type"] == "expect_table_column_count_to_equal":
            num_expected_features = e["kwargs"].get("value")
            num_observed_features = e["result"].get("observed_value")
        elif e["expectation_type"] == "expect_table_columns_to_match_set":
            expected_set = set(e["kwargs"].get("column_set", []))
            observed_set = set(e["result"].get("observed_value", []))

    new_features = [*observed_set - expected_set]
    missing_features = [*expected_set - observed_set]

    num_new_features = len(new_features)
    num_missing_features = len(missing_features)

    #num_data_errors = gxe_output["statistics"].get("unsuccessful_expectations", 0)
    num_samples = 0
    num_affected_samples = 0

    for e in expectations:
        res = e.get("result", {})
        if isinstance(res, dict) and "element_count" in res:
            num_samples = max(num_samples, res.get("element_count", 0))
        if isinstance(res, dict) and "unexpected_count" in res:
            num_affected_samples += res.get("unexpected_count", 0)

    
    column_error_types = [(f, 'missing') for f in missing_features] + [(f, 'new') for f in new_features]

    feature_error_stats = []
    different_error_types = set()

    for e in expectations:
        if not e.get("success", True) and "column" in e.get("kwargs", {}):
            column = e["kwargs"]["column"]
            error_type = e["expectation_type"]
            result = e.get("result", {})
            num_records = result.get("element_count", num_samples)
            num_affected = result.get("unexpected_count", 0)
            different_error_types.add(error_type)

            feature_error_stats.append((column, error_type, num_records, num_affected))

    num_distinct_error_types = len(different_error_types) + (1 if num_new_features else 0) +( 1 if num_new_features else 0)


    batch_columns_stats = (
        num_expected_features, num_observed_features,
        num_new_features, num_missing_features, num_distinct_error_types,
        num_samples, num_affected_samples
    )

    ingestion_metadata = (file_name,)

    return {
        "ingestion_metadata": ingestion_metadata,
        "batch_columns_stats": batch_columns_stats,
        "column_error_types": column_error_types,
        "feature_error_stats": feature_error_stats,
    }


def _save_statistics(ti):
    from pathlib import Path

    ddl_queries_path = '/opt/airflow/scripts/sql/ingestion_statistics_demo_ver.sql'
    gxe_output = ti.xcom_pull(task_ids='validate_data', key='return_value')
    file_name = ti.xcom_pull(task_ids='read_data', key='return_value')

    print(f'File: {file_name}, Output passed {gxe_output}')

    parsed = parse_gxe_output(gxe_output, file_name)

    pg_hook = PostgresHook(postgres_conn_id='pg_conn_ingestion_statistics')


    with open(ddl_queries_path, 'r') as f:
        ddl_queries = f.read()

    # If schema and tables does not exist, create them
    pg_hook.run(ddl_queries)

    # Insert batch metadata first to get the batch_id
    insert_metadata_sql = """
        INSERT INTO marketing_ingestion_statistics.ingestion_metadata (file_name, execution_timestamp)
        VALUES (%s, NOW())
        RETURNING batch_id;
    """
    batch_id = pg_hook.get_first(insert_metadata_sql, parameters=parsed["ingestion_metadata"])[0]

    # Storing if we got a missing or new feature
    insert_batch_sql = """
        INSERT INTO marketing_ingestion_statistics.batch_columns_stats (
            batch_id, num_expected_features, num_observed_features, num_new_features,
            num_missing_features, num_data_errors, num_samples, num_affected_samples)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    pg_hook.run(insert_batch_sql, parameters=(batch_id, *parsed["batch_columns_stats"]))

    # Inserting multiples rows at once
    def bulk_insert(table_name, headers, rows):
        pg_hook.insert_rows(
            table=table_name,
            rows=rows,
            target_fields=headers,
            commit_every=100
        )

    if parsed["column_error_types"]:
        rows = [(batch_id, row[0], row[1]) for row in parsed["column_error_types"]]
        bulk_insert("marketing_ingestion_statistics.column_error_types", ["batch_id", "feature", "col_error_type"], rows)

    if parsed["feature_error_stats"]:
        rows = [(batch_id, row[0], row[1], row[2], row[3]) for row in parsed["feature_error_stats"]]
        bulk_insert("marketing_ingestion_statistics.feature_error_stats", ["batch_id", "feature", "error_type", "num_records", "num_affected_records"], rows)

    print(f"Ingestion statistics saved for batch_id {batch_id}")


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


    save_statistics = PythonOperator(
        task_id='save_statistics',
        python_callable=_save_statistics
        )


# Execution order of tasks
_read_data >> validate_data >> [_save_file, dummy_task, save_statistics]