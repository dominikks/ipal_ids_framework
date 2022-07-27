from abc import ABC, abstractmethod
import json
from pathlib import Path
import time

import ipal_iids.settings as settings
from ipal_iids.utils import open_file, relative_to_config
import joblib


class Combiner(ABC):

    _name = None
    _combiner_default_settings = {
        "idss": [],  # List of the idss whose outputs are used as input for the combiner
        "model-file": None,
    }

    def __init__(self):
        self.settings = settings.combiners[self._name]

        self._default_settings = {}
        self._add_default_settings(self._combiner_default_settings)

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

    def _load_events(self, idss, ipal=None, state=None):
        """
        Load events from a file for training.
        """
        if ipal and state:
            settings.logger.error("Only state or message supported")
            exit(1)

        events = []
        annotations = []

        start = time.time()
        settings.logger.info("Loading training file started at {}".format(start))

        with open_file(state or ipal) as file:
            for msg in file.readline():
                msg = json.loads(msg)

                if state:
                    events.append(
                        [
                            idss[ids_name].new_state_msg(msg)
                            for ids_name in self.settings["idss"]
                        ]
                    )
                else:
                    events.append(
                        [
                            idss[ids_name].new_ipal_msg(msg)
                            for ids_name in self.settings["idss"]
                        ]
                    )

                annotations.append(msg["malicious"])

        end = time.time()
        settings.logger.info(
            "Loading training file ended at {} ({}s)".format(end, end - start)
        )

        return events, annotations

    @abstractmethod
    def train(self, idss, ipal=None, state=None):
        pass

    def new_ipal_msg(self, idss, msg):
        event = [idss[ids_name].new_ipal_msg(msg) for ids_name in self.settings["idss"]]
        return self._process_event(event)

    def new_state_msg(self, idss, msg):
        event = [
            idss[ids_name].new_state_msg(msg) for ids_name in self.settings["idss"]
        ]
        return self._process_event(event)

    @abstractmethod
    def _process_event(self, event):
        pass

    def save_trained_model(self):
        if self.settings["model-file"] is None:
            return False

        model = {"settings": self.settings, **self._get_model()}

        joblib.dump(model, self._resolve_model_file_path(), compress=3)

        return True

    def load_trained_model(self, model):
        if self.settings["model-file"] is None:
            return False

        try:  # Open model file
            model = joblib.load(self._resolve_model_file_path())
        except FileNotFoundError:
            settings.logger.info(
                "Model file {} not found.".format(str(self._resolve_model_file_path()))
            )
            return False

        self.settings = model["settings"]
        self._load_model(model)

    @abstractmethod
    def _get_model(self):
        pass

    @abstractmethod
    def _load_model(self, model):
        pass
