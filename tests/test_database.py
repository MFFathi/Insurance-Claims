import psycopg2


def test_underlying_pg_connection():
    psycopg2.connect(
        "dbname=insurance_claims user=postgres password=postgres host=db port=5432")