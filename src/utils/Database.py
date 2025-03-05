import time
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .env import get_env

CONNECTION_RETRY_LIMIT = 5
CONNECTION_RETRY_DELAY = 2


class Database:
    connection: psycopg2.extensions.connection

    @classmethod
    def connect(cls) -> None:
        """ 
        Connect to database as defined in env
        Should be run once and only once

        NOTE: Database.init MUST be run after this to fully setup database
        """

        cls.host = get_env("DB_HOST", "127.0.0.1")
        cls.port = get_env("POSTGRES_PORT")
        cls.dbname = get_env("POSTGRES_DB")
        cls.user = get_env("POSTGRES_USER")
        cls.password = get_env("POSTGRES_PASSWORD")
        cls.connection_tries = 0

        print(f"Connecting to database on {cls.host}:{cls.port}")
        cls._verify_db_exists()

    @classmethod
    def init(cls) -> None:
        """
        Initialize database ( runs init_sql)
        Should be run once and only once
        """
        cls._run_init_sql()

    @classmethod
    def cursor(cls) -> psycopg2.extensions.cursor:
        return cls.connection.cursor()

    @classmethod
    def commit(cls):
        cls.connection.commit()

    @classmethod
    def close(cls):
        cls.connection.close()

    @classmethod
    def DEBUG_delete_all_tables(cls, verify: str):
        """
        Delete all tables in database
        verify must be "DANGEROUSLY DELETE ALL TABLES"
        """

        if verify != "DANGEROUSLY DELETE ALL TABLES":
            raise Exception("You must verify that you want to delete all tables \
                            in the database by passing the string 'DANGEROUSLY DELETE ALL TABLES'  \
                            as the first argument to this function")

        cur = cls.cursor()
        cur.execute("DROP SCHEMA public CASCADE;")
        cur.execute("CREATE SCHEMA public;")
        cur.execute("GRANT ALL ON SCHEMA public TO postgres;")
        cur.execute("GRANT ALL ON SCHEMA public TO public;")
        cls.commit()

    @classmethod
    def _create_db_connection(cls, dbname: str) -> None:
        """
        Create a database connection to given dbname
        Sets that database to cls.connection
        """

        cls.connection_tries += 1
        try:
            cls.connection = psycopg2.connect(
                dbname=dbname,
                user=cls.user,
                password=cls.password,
                host=cls.host,
                port=cls.port
            )
        except psycopg2.OperationalError as e:
            if cls.connection_tries > CONNECTION_RETRY_LIMIT:
                raise e

            print(
                f"Failed to connect to database {dbname} on {cls.host}:{cls.port}. Retrying...")
            time.sleep(CONNECTION_RETRY_DELAY)
            cls._create_db_connection(dbname)

    @classmethod
    def _verify_db_exists(cls) -> bool:
        """
        Check if database defined by cls.dbname exists and create it if it doesn't
        """

        dbname = cls.dbname
        cls._create_db_connection("postgres")
        cur = cls.cursor()

        cur.execute("SELECT datname FROM pg_database;")
        all_databases = cur.fetchall()

        if (dbname,) not in all_databases:
            print(f"Database {dbname} does not exist. Creating it now...")
            cls.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cur.execute("create database "+dbname+";")
            cls.commit()
            print("Database created successfully")

        cls.close()

        cls._create_db_connection(cls.dbname)

    @classmethod
    def _run_init_sql(cls) -> bool:
        """
        Runs initialization SQL files
        """
        cls._run_sql_file("src/init_sql/tests/init_check_table.sql")
        return True

    @classmethod
    def _run_sql_in_dir(cls, path: str) -> bool:
        """
        Runs SQL files in a given directory or a specific SQL file
        """
        if os.path.isdir(path):
            for entry in os.scandir(path):
                if entry.is_file() and entry.name.endswith('.sql'):
                    cls._run_sql_file(entry.path)
                elif entry.is_dir():
                    cls._run_sql_in_dir(entry.path)
        elif os.path.isfile(path):
            cls._run_sql_file(path)
        
        return True

    @classmethod
    def _run_sql_file(cls, path: str) -> bool:
        """
        Runs given sql file
        """

        print(f"Running sql file {path}")
        file = open(path, "r")
        sql = file.read()

        cur = cls.cursor()
        cur.execute(sql)
        cls.commit()

        file.close()
        print(f"Successfully ran sql file {path}")