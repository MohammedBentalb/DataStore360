import os

def get_engine(con_id: str = 'postgres_datastore'):
    try:
        from airflow.providers.postgres.hooks.postgres import PostgresHook
        return PostgresHook(postgres_conn_id=con_id).get_sqlalchemy_engine()
    except ImportError:
        from sqlalchemy import create_engine
        return create_engine(os.environ.get("DATASTORE_URI", ""))