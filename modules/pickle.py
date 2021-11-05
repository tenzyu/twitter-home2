import pickle
from typing import Generic, TypeVar

D = TypeVar("D")


class Pickle(Generic[D]):
    __slots__ = ("path", "default_data", "data")
    data: D

    def __init__(self, path: str, default_data: D):
        self.path = path
        self.default_data = default_data
        self.load()

    def init(self):
        self.data = self.default_data
        self.save()

    def load(self):
        with open(self.path, "rb") as f:
            try:
                self.data = pickle.load(f)
            except EOFError:
                self.init()

    def save(self):
        with open(self.path, "wb") as f:
            pickle.dump(self.data, f)
