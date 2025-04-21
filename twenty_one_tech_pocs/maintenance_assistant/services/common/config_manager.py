import os
from dotenv import load_dotenv


class ConfigManager:
    """Manages loading and accessing configuration from a .env file."""

    def __init__(self, env_path=None):
        """
        Initializes the ConfigManager and loads environment variables.

        Args:
            env_path (str, optional): The path to the .env file. 
                                      Defaults to finding .env in the project root or parent directories.
        """
        if env_path:
            load_dotenv(dotenv_path=env_path)
        else:
            load_dotenv()  # Searches for .env in current or parent directories

    def get_llm_config(self, prefix="LLM_") -> dict:
        """
        Retrieves LLM configuration parameters from environment variables.

        Args:
            prefix (str): The prefix for LLM-related environment variables (e.g., "LLM_").

        Returns:
            dict: A dictionary containing the LLM configuration parameters.
        """
        config = {}
        # Define expected keys and their types (optional, for validation/casting)
        expected_keys = {
            "NAME": str,
            "TEMPERATURE": float,
            "MAX_TOKENS": int,
            "TIMEOUT": int,
            "MAX_RETRIES": int,
            "API_KEY": str,
            "BASE_URL": str,
        }

        for key, key_type in expected_keys.items():
            env_var = f"{prefix}{key}"
            value = os.getenv(env_var)
            if value is not None:
                try:
                    # Attempt to cast to the expected type if defined
                    if key_type:
                        # Handle potential empty strings for optional numeric types
                        if value == '' and key_type in (int, float):
                            # Or set a default like 0 or 0.0 if appropriate
                            config[key.lower()] = None
                        else:
                            config[key.lower()] = key_type(value)
                    else:
                        config[key.lower()] = value
                except (ValueError, TypeError):
                    print(
                        f"Warning: Could not cast environment variable {env_var} ('{value}') to type {key_type}. Using raw string value.")
                    # Keep as string if casting fails
                    config[key.lower()] = value
            else:
                # Set to None if the environment variable is not found
                config[key.lower()] = None

        # Filter out None values before returning, as get_llm handles defaults
        return {k: v for k, v in config.items() if v is not None}
