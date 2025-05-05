import os


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class ConfigurationAware:
    def __init__(self):
        self._home_path_ = os.environ.get('SEQAM_CONFIG_PATH') or os.path.join(ROOT_PATH, "Configuration")
