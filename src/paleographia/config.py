import copy
import tomllib
from pathlib import Path


def load_config(path="configs/pilot.toml"):
    with Path(path).open("rb") as stream:
        return copy.deepcopy(tomllib.load(stream))
