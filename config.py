import json
import sys


class Config(dict):
    @classmethod
    def load(cls, filename):
        return Config(**json.load(open(filename, "r")))

    def __getattr__(self, name):
        if name in self:
            if isinstance(self[name], dict):
                return Config(**self[name])
            return self[name]

        raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


sys.modules[__name__] = Config.load("config.json")
