from abc import ABC, abstractmethod
from pathlib import Path

import ipal_iids.settings as settings
from ipal_iids.utils import relative_to_config
import joblib


class Combiner(ABC):

    _name = None
    _combiner_default_settings = {
        "state-idss": None,  # IDS names to be used (None means all compatible to state/ipal)
        "ipal-idss": None,
        "model-file": None,
    }

    def __init__(self, idss):
        self.settings = settings.combiner

        self._default_settings = {}
        self._add_default_settings(self._combiner_default_settings)

        # Add all compatible IDSS if not specifically set
        if self.settings["state-idss"] is None:
            self.settings["state-idss"] = [
                ids._name
                for ids in idss
                if ids.requires("train.state") and ids.requires("live.state")
            ]
        if self.settings["ipal-idss"] is None:
            self.settings["ipal-idss"] = [
                ids._name
                for ids in idss
                if ids.requires("train.ipal") and ids.requires("live.ipal")
            ]

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

    # def _load_ipal_events(self, idss, ipal):
    #     """
    #     Load events from an IPAL file for training.
    #     """
    #     events = []
    #     annotations = []

    #     start = time.time()
    #     settings.logger.info("Loading IPAL training file started at {}".format(start))

    #     with open_file(ipal) as file:
    #         for msg in file.readline():
    #             msg = json.loads(msg)

    #             events.append(
    #                 [
    #                     idss[ids_name].new_ipal_msg(msg)
    #                     for ids_name in self.settings["ipal-idss"]
    #                 ]
    #             )
    #             annotations.append(msg["malicious"])

    #     end = time.time()
    #     settings.logger.info(
    #         "Loading IPAL training file ended at {} ({}s)".format(end, end - start)
    #     )

    #     return events, annotations

    # def _load_state_events(self, idss, state):
    #     """
    #     Load events from a state file for training.
    #     """
    #     events = []
    #     annotations = []

    #     start = time.time()
    #     settings.logger.info("Loading state training file started at {}".format(start))

    #     with open_file(state) as file:
    #         for msg in file.readline():
    #             msg = json.loads(msg)

    #             events.append(
    #                 [
    #                     idss[ids_name].new_state_msg(msg)
    #                     for ids_name in self.settings["state-idss"]
    #                 ]
    #             )
    #             annotations.append(msg["malicious"])

    #     end = time.time()
    #     settings.logger.info(
    #         "Loading state training file ended at {} ({}s)".format(end, end - start)
    #     )

    #     return events, annotations

    @abstractmethod
    def train(self, idss, ipal=None, state=None):
        pass

    @abstractmethod
    def process_ipal_msg(self, ids_outputs):
        pass

    @abstractmethod
    def process_state_msg(self, ids_outputs):
        pass

    def save_trained_model(self):
        if self.settings["model-file"] is None:
            return False

        model = {"settings": self.settings, **self._get_model()}

        joblib.dump(model, self._resolve_model_file_path(), compress=3)

        return True

    def load_trained_model(self):
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
