from combiner.combiner import Combiner
from sklearn.linear_model import LogisticRegression as LogisticRegressionModel
import ipal_iids.settings as settings


class LogisticRegression(Combiner):
    _name = "LogisticRegression"
    _needs_training = True

    def __init__(self, name=None):
        super().__init__(name)

        self._model = None
        self._ids_order = None

    def _get_activations(self, msg):
        return [float(msg["alerts"][ids]) for ids in self._ids_order]

    def train(self, msgs):
        self._ids_order = list(msgs[0]["alerts"].keys())

        m = LogisticRegressionModel()

        events = []
        annotations = []

        for msg in msgs:
            events.append(self._get_activations(msg))
            annotations.append(msg["malicious"] is not False)

        settings.logger.info("Fitting LogisticRegression Combiner")
        m.fit(events, annotations)

        settings.logger.info("LogisticRegression Combiner trained")
        self._model = m

    def combine(self, msg):
        activations = self._get_activations(msg)
        alert = bool(self._model.predict([activations])[0])
        return alert, 1 if alert else 0

    def _get_model(self):
        return {
            "model": self._model,
            "ids_order": self._ids_order,
        }

    def _load_model(self, model):
        self._model = model["model"]
        self._ids_order = model["ids_order"]
