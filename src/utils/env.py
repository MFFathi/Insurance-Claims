import os
from typing import Optional

def get_env(key: str, default: Optional[str] = None) -> str:
    """
    Retrieve an environment variable with improved error handling.
    
    :param key: The name of the environment variable
    :param default: Optional default value if environment variable is not set
    :return: The value of the environment variable
    :raises ValueError: If no default is provided and the environment variable is not set
    """
    is_docker = os.path.exists('/.dockerenv')
    
    if key == 'DB_HOST':
        return 'db' if is_docker else '127.0.0.1'
    
    value = os.environ.get(key)
    
    if value is None:
        if default is not None:
            return default
        
        print(f"\n!!! ERROR: Environment variable {key} is not set !!!")
        print("Current environment variables:")
        for env_key, env_value in os.environ.items():
            print(f"{env_key}: {env_value}")
        
        raise ValueError(f"Environment variable {key} is not set and no default value provided")
    
    return value