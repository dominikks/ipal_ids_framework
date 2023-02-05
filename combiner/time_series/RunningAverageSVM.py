from combiner.combiner import Combiner
import ipal_iids.settings as settings
from sklearn import svm


class RunningAverageSVMCombiner(Combiner):

    _name = "RunningAverageSVM"
    _needs_training = True

    _svmcombiner_default_settings = {"new_weight": 0.05}

    def __init__(self, name=None):
        super().__init__(name)
        self._add_default_settings(self._svmcombiner_default_settings)

        self._svm = None
        self._ids_order = None

    def _get_activations(self, msg, old_average):
        return [self.settings["new_weight"] * float(msg["metrics"][ids]) + (1 - self.settings["new_weight"]) * old_average for ids, old_average in zip(self._ids_order, old_average)]

    def train(self, msgs):
        self._ids_order = list(msgs[0]["alerts"].keys())
        self._running_average = [0 for _ in self._ids_order]

        m = svm.SVC()

        events = []
        annotations = []

        running_average = [0 for _ in self._ids_order]

        for msg in msgs:
            running_average = self._get_activations(msg, running_average)
            events.append(running_average)
            annotations.append(msg["malicious"] is not False)

        settings.logger.info("Fitting SVM Running Average Combiner")
        m.fit(events, annotations)

        settings.logger.info("SVM Combiner Running Average trained")
        self._svm = m

    def combine(self, msg):
        self._running_average = self._get_activations(msg, self._running_average)
        alert = bool(self._svm.predict([self._running_average])[0])
        return alert, 1 if alert else 0

    def _get_model(self):
        return {
            "model": self._svm,
            "ids_order": self._ids_order,
        }

    def _load_model(self, model):
        self._svm = model["model"]
        self._ids_order = model["ids_order"]
        self._running_average = [0 for _ in self._ids_order]
