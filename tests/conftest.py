import os
import pytest

def print_environment():
    """Debug function to print all current environment variables"""
    print("\n--- CURRENT ENVIRONMENT VARIABLES ---")
    for key, value in os.environ.items():
        print(f"{key}: {value}")
    print("--- END OF ENVIRONMENT VARIABLES ---\n")

@pytest.fixture(scope="session", autouse=True)
def set_env_variables():
    """
    Set environment variables for database connection
    Ensures variables are available during test execution
    """
    os.environ['DB_HOST'] = 'db'
    os.environ['POSTGRES_PORT'] = '5432'
    os.environ['POSTGRES_DB'] = 'insurance_claims'
    os.environ['POSTGRES_USER'] = 'postgres'
    os.environ['POSTGRES_PASSWORD'] = 'postgres'

    print_environment()