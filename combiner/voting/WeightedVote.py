from combiner.combiner import Combiner


class WeightedVote(Combiner):

    _name = "WeightedVote"
    _weightedvote_default_settings = {
        "weights": {},  # A weight for each IDS name
        "threshold": 1,
    }

    def __init__(self):
        super().__init__()
        self._add_default_settings(self._weightedvote_default_settings)

    def train(self, idss, ipal=None, state=None):
        # This Combiner does not need to be trained
        pass

    def combine(self, msg):
        weight_sum = sum(
            [
                (self.settings["weights"][name] or 0) if alert else 0
                for name, alert in msg["alerts"].items()
            ]
        )

        alert = weight_sum >= self.settings["threshold"]
        return alert, weight_sum

    def _get_model(self):
        return {}

    def _load_model(self, model):
        return {}
