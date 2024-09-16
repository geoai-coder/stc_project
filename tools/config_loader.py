# config_loader.py
import json
import os


class ConfigLoader:
    def __init__(self, json_path):
        self.json_path = json_path
        self.config = self._load_config()

    def _load_config(self):
        """Load the configuration from the JSON file."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"Configuration file not found: {self.json_path}")

        with open(self.json_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_config(self):
        """Get the entire configuration dictionary."""
        return self.config

    def get_value(self, *keys):
        """Retrieve a value from the configuration using a list of keys."""
        config = self.config
        for key in keys:
            # print(config[key])
            config = config.get(key, {})
            if not isinstance(config, dict):
                return config
        return config


# Example usage
if __name__ == "__main__":
    # Provide the path to your JSON configuration file
    config_path = '../static/config.json'

    # Instantiate the ConfigLoader
    config_loader = ConfigLoader(config_path)

    # Get the entire configuration
    config = config_loader.get_config()
    print("Full Configuration:", config)

    # Example: Get specific configuration values
    encdataset_path = config_loader.get_value('encdataset', 'baidu_path')
    print("Baidu Path:", encdataset_path)
