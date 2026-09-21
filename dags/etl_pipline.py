from airflow.decorators import dag, task
from datetime import datetime, timedelta



@dag(
    dag_id="DataStore",
    schedule=None,
    start_date=datetime(2026,1, 1),
    catchup=False,
    default_args={
        'retries' : 2, "retry_delay": timedelta(minutes=5)
    }
)
def datastore_pipeline():
    @task
    def create_tables():
        from airflow.providers.postgres.hooks.postgres import PostgresHook  # correct
        hook = PostgresHook(postgres_conn_id="postgres_datastore")
        for file in ["01_create_staging.sql", "02_create_core.sql"]:
            with open(f"/opt/airflow/include/sql/{file}") as f:
                hook.run(f.read())
        print('------------------')
        print('tables ccreated')
        print('------------------')

    @task
    def raw_profiling_task():
        from src.profiling import make_profiling_report
        from src.config import RAW_REPORT_HTML, RAW_CSV
        make_profiling_report(RAW_CSV, RAW_REPORT_HTML)

    @task
    def extract_task():
        from src.extract import load_csv_to_staging
        load_csv_to_staging()

    @task
    def clean_task():
        from src.gdpr_cleaning import run_clean
        run_clean()

    @task
    def cleaned_profiling_task():
        from src.profiling import make_profiling_report
        make_profiling_report()

    @task
    def load_core_task():
        from src.load import run_load
        run_load()

    create_tables() >> raw_profiling_task() >> extract_task() >> clean_task() >> cleaned_profiling_task() >> load_core_task()

datastore_pipeline()