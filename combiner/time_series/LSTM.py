from combiner.combiner import Combiner

from tensorflow.keras.models import Sequential  # noqa: E402
from tensorflow.keras.layers import LSTM  # noqa: E402
from tensorflow.keras.layers import Dense  # noqa: E402
from tensorflow.keras.optimizers import Adam  # noqa: E402
import tensorflow

import ipal_iids.settings as settings  # noqa: E402


class LSTMCombiner(Combiner):

    _name = "LSTMCombiner"
    _needs_training = True

    _lstmcombiner_default_settings = {
        "use_metrics": False,
        "sequence_length": 32,
        "epochs": 50,
    }

    def __init__(self, name=None):
        super().__init__(name=name)
        self._add_default_settings(self._lstmcombiner_default_settings)

        self._lstm = None
        self._ids_order = None

        self._buffer = []

    def _lstm_model(self, input_dim):
        model = Sequential()

        model.add(
            LSTM(input_dim, input_shape=(self.settings["sequence_length"], input_dim))
        )
        model.add(Dense(1, activation="sigmoid"))

        model.compile(loss="binary_crossentropy", optimizer=Adam(), metrics=["acc"])

        model.summary(print_fn=settings.logger.info)

        return model

    def _get_activations(self, msg):
        return [
            float(msg["metrics" if self.settings["use_metrics"] else "alerts"][ids])
            for ids in self._ids_order
        ]

    def _get_sequences(self, events, annotations):
        Xseq, Yseq = [], []

        for i in range(0, len(events) - self.settings["sequence_length"] + 1):
            Xseq.append(events[i : i + self.settings["sequence_length"]])
            Yseq.append(annotations[i + self.settings["sequence_length"] - 1])

        return Xseq, Yseq

    def train(self, msgs):
        self._ids_order = list(msgs[0]["alerts"].keys())
        self._lstm = self._lstm_model(len(self._ids_order))

        events = []
        annotations = []

        for msg in msgs:
            events.append(self._get_activations(msg))
            annotations.append(msg["malicious"] is not False)

        X, Y = self._get_sequences(events, annotations)

        settings.logger.info(
            f"Training LSTM combiner for {self.settings['epochs']} epochs..."
        )
        self._lstm.fit(X, Y, epochs=self.settings["epochs"], verbose=10)

    def combine(self, msg):
        self._buffer.append(self._get_activations(msg))

        if len(self._buffer) > self.settings["sequence_length"]:
            self._buffer.pop(0)
        elif len(self._buffer) < self.settings["sequence_length"]:
            return False, 0

        prediction = self._lstm.predict([self._buffer])[0]
        alert = bool(prediction > 0.5)

        return alert, prediction

    def save_trained_model(self):
        if not super().save_trained_model():
            return False

        self._lstm.save(self._resolve_model_file_path().with_suffix(".keras"))

        return True

    def load_trained_model(self):
        if not super().load_trained_model():
            return False

        self._lstm = tensorflow.keras.models.load_model(
            self._resolve_model_file_path().with_suffix(".keras")
        )

        return True

    def _get_model(self):
        return {
            "ids_order": self._ids_order,
        }

    def _load_model(self, model):
        self._ids_order = model["ids_order"]

