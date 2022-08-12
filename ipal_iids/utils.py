import gzip
from pathlib import Path
import sys

import ipal_iids.settings as settings


def open_file(filename, mode="r", **args):
    filename = str(filename)
    if filename is None:
        return None
    elif filename.endswith(".gz"):
        return gzip.open(filename, mode, **args)
    elif filename == "-":
        return sys.stdin
    else:
        return open(filename, mode, **args)


def relative_to_config(file: str) -> Path:
    """
    translate string of a file path to the resolved Path when
    interpreting it as relative to the config file's location
    """
    config_file = Path(settings.config).resolve()
    file_path = Path(file)
    return (config_file.parent / file_path).resolve()

