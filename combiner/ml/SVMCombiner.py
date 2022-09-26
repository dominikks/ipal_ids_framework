from combiner.combiner import Combiner
import ipal_iids.settings as settings
from sklearn import svm


class SVMCombiner(Combiner):

    _name = "SVMCombiner"
    _needs_training = True

    _svmcombiner_default_settings = {"use_metrics": False}

    def __init__(self, name=None):
        super().__init__(name)
        self._add_default_settings(self._svmcombiner_default_settings)

        self._svm = None
        self._ids_order = None

    def _get_activations(self, msg):
        return [
            float(msg["metrics" if self.settings["use_metrics"] else "alerts"][ids])
            for ids in self._ids_order
        ]

    def train(self, msgs):
        self._ids_order = list(msgs[0]["alerts"].keys())

        m = svm.SVC()

        events = []
        annotations = []

        for msg in msgs:
            events.append(self._get_activations(msg))
            annotations.append(msg["malicious"] is not False)

        settings.logger.info("Fitting SVM Combiner")
        m.fit(events, annotations)

        settings.logger.info("SVM Combiner trained")
        self._svm = m

    def combine(self, msg):
        activations = self._get_activations(msg)
        alert = bool(self._svm.predict([activations])[0])
        return alert, 1 if alert else 0

    def _get_model(self):
        return {
            "model": self._svm,
            "ids_order": self._ids_order,
        }

    def _load_model(self, model):
        self._svm = model["model"]
        self._ids_order = model["ids_order"]
