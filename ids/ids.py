import gzip
import hashlib
import json
import sys

from pathlib import Path

import ipal_iids.settings as settings
from ipal_iids.utils import open_file, relative_to_config


class MetaIDS:

    _name = None
    _description = ""
    _requires = []
    _metaids_default_settings = {"model-file": None}
    _supports_preprocessor = False

    def __init__(self, name=None):
        self._name = name
        self.settings = settings.idss[self._name]

        self._default_settings = {}
        self._add_default_settings(self._metaids_default_settings)

        self._open_file = open_file

    def _add_default_settings(self, settings):
        for key, value in settings.items():
            assert key not in self._default_settings
            self._default_settings[key] = value

            # Fill current configuration with default values
            if key not in self.settings:
                self.settings[key] = value

    def _resolve_model_file_path(self) -> Path:
        """
        translate model-file path into absolute Path using
        config file location
        """
        if self.settings["model-file"] is None:
            raise Exception("Can't resolve model file since no model file was provided")
        return relative_to_config(self.settings["model-file"])

    def _add_msg_hash(self, msg, nbytes=2):
        fingerprint = json.dumps(
            [
                msg["src"],
                msg["dest"],
                msg["protocol"],
                msg["activity"],
                msg["type"],
                msg["length"],
                msg["data"],
                # not id, timestamp, responds_to, malicious
            ]
        )

        # Create n-byte hash of the fingerprint
        fingerprint = fingerprint.encode("utf-8")
        msg["hash"] = int(hashlib.sha1(fingerprint).hexdigest()[: nbytes * 2], 16)

    # what data (ipal messages / state informatin) does this IDS need for its learning and intrusion detection phase?
    def requires(self, dataformat):
        if dataformat not in ["train.state", "live.state", "train.ipal", "live.ipal"]:
            settings.logger.critical(
                "Unexpected format requested: {}".format(dataformat)
            )
        return dataformat in self._requires

    # the IDS is given the path to file(s) containing its requested training data
    def train(self, ipal=None, state=None):
        raise NotImplementedError

    # if a new ipal message is available during the intrustion detection phase, this function is called
    # with the message in json format. Return if an alert is thrown by this IDS
    def new_ipal_msg(self, msg):
        raise NotImplementedError

    # if new state information is available during the intrustion detection phase, this function is called
    # with the message in json format. Return if an alert is thrown by this IDS
    def new_state_msg(self, msg):
        raise NotImplementedError

    def save_trained_model(self):
        raise NotImplementedError

    def load_trained_model(self):
        raise NotImplementedError

    def visualize_model(self):
        raise NotImplementedError
