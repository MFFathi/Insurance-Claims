import psycopg2
import pytest
from src.utils.Database import Database


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """
    Fixture to setup and teardown the database for testing.
    Runs once per test session.
    """
    Database.connect()
    Database.init()
    yield
    Database.close()


def test_database_connection():
    """Test if the database connection is established."""
    assert Database.connection is not None
    assert Database.connection.closed == 0


def test_can_create_table():
    """Test if a table can be created."""
    cur = Database.cursor()
    sql = """
        CREATE TABLE test_table (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER
        );
    """
    cur.execute(sql)
    Database.commit()

    cur.execute(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'test_table');"
    )
    assert cur.fetchone()[0] is True


def test_can_insert_into_table():
    """Test if data can be inserted into a table."""
    cur = Database.cursor()
    cur.execute("INSERT INTO test_table (name, age) VALUES ('Alice', 30);")
    Database.commit()

    cur.execute("SELECT * FROM test_table;")
    assert cur.fetchall() == [(1, 'Alice', 30)]


def test_can_delete_from_table():
    """Test if data can be deleted from a table."""
    cur = Database.cursor()
    cur.execute("DELETE FROM test_table WHERE name = 'Alice';")
    Database.commit()

    cur.execute("SELECT * FROM test_table;")
    assert cur.fetchall() == []


def test_can_drop_table():
    """Test if a table can be dropped."""
    cur = Database.cursor()
    cur.execute("DROP TABLE IF EXISTS test_table;")
    Database.commit()

    cur.execute(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'test_table');"
    )
    assert cur.fetchone()[0] is False


def test_can_run_init_sql():
    """Test if the database initialization SQL scripts run correctly."""
    Database.init()
    cur = Database.cursor()

    cur.execute("INSERT INTO init_check_table VALUES ('init_check', 1);")
    Database.commit()
    
    cur.execute("SELECT * FROM init_check_table;")
    assert cur.fetchall() == [('init_check', 1)]


def test_debug_delete_all_tables():
    """Test if all tables can be deleted using DEBUG_delete_all_tables."""
    Database.DEBUG_delete_all_tables("DANGEROUSLY DELETE ALL TABLES")

    cur = Database.cursor()
    cur.execute(
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
    )
    assert cur.fetchone()[0] == 0



def test_can_close_connection():
    """Test if the database connection can be closed properly."""
    Database.close()
    assert Database.connection.closed == 1
