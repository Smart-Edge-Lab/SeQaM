import json
import os
import re


class JsonReader ():

    def __init__(self, experiment_file) -> None:
        self._file_ = experiment_file

    @staticmethod
    def _substitute_env_vars(text: str) -> str:
        """
        Replaces all occurrences of $VAR with its value
        from the environment variable VAR
        """
        new_string = ''
        start = 0
        for m in re.finditer(r"\$([a-zA-Z0-9_]+)\s*\|\s*([^\s\",]+)", text):
            end, new_start = m.span()
            new_string += text[start:end]
            var_name = m.group(1)
            default_value = m.group(2)
            rep = os.environ[var_name] if var_name in os.environ else default_value
            new_string += rep
            start = new_start
        new_string += text[start:]
        return new_string

    def readFile (self) :
        
        with open(self._file_, 'r') as file:
            text = file.read()
            text = self._substitute_env_vars(text)
            # Load JSON data from file
            data = json.loads(text)
            return data