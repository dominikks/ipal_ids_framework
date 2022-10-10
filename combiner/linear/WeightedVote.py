from combiner.combiner import Combiner


class WeightedVote(Combiner):

    _name = "WeightedVote"
    _weightedvote_default_settings = {
        "weights": {},  # A weight for each IDS name
        "threshold": 1,
    }

    def __init__(self, name=None):
        super().__init__(name=name)
        self._add_default_settings(self._weightedvote_default_settings)

    def combine(self, msg):
        weight_sum = sum(
            [
                self.settings["weights"].get(name, 0) if alert else 0
                for name, alert in msg["alerts"].items()
            ]
        )

        alert = weight_sum >= self.settings["threshold"]
        return alert, weight_sum
