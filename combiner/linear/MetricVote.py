from combiner.combiner import Combiner


class MetricVote(Combiner):

    _name = "MetricVote"
    _metricvote_default_settings = {
        "weights": {},  # A weight for each IDS name
        "threshold": 1,
    }

    def __init__(self, name=None):
        super().__init__(name=name)
        self._add_default_settings(self._metricvote_default_settings)

    def combine(self, msg):
        metric_sum = sum(
            [
                self.settings["weights"].get(name, 0) * metric
                for name, metric in msg["metrics"].items()
            ]
        )

        alert = bool(metric_sum >= self.settings["threshold"])
        return alert, metric_sum
