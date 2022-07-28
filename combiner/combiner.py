from abc import ABC, abstractmethod
from pathlib import Path

import ipal_iids.settings as settings
from ipal_iids.utils import relative_to_config
import joblib


class Combiner(ABC):

    _name = None
    _combiner_default_settings = {
        "model-file": None,
    }

    def __init__(self):
        self.settings = settings.combiner

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

    @abstractmethod
    def train(self, idss, ipal=None, state=None):
        pass

    @abstractmethod
    def combine(self, ids_outputs):
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
