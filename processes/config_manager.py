import pandas as pd

class ConfigManager:

    def __init__(self, config_file_path):
        """Load config file """
        self.config = self.load_config(config_file_path)
    
    def load_config(self, config_file_path):
        """Create and return dictionary"""
        df = pd.read_excel(config_file_path)
        return pd.Series(df.VALUE.values, index=df.NAME).to_dict()
    
    def get(self, key):
        """Return a specific key of the dictionary"""
        return self.config.get(key)