from typing import *
import json
import re
import shutil
import os


class UrlResolver:

    def __init__(self) -> None:
        super().__init__()
        self.load_data()

    def load_data(self):
        if not os.path.exists("dict_sources.json"):
            shutil.copy("dict_sources.default.json", "dict_sources.json")

        with open("dict_sources.json", 'r', encoding='utf-8') as f:
            self.source_data = json.load(f)

    def save_data(self):
        with open("dict_sources.json", 'w', encoding='utf-8') as f:
            json.dump(self.source_data, f)

    def resolve(self, word: str) -> Optional[str]:

        for pattern, url in self.source_data:
            if re.match(pattern, word) is not None:
                return url % word

        return None
