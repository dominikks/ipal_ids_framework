from combiner.combiner import Combiner


class OrCombiner(Combiner):

    _name = "Or"

    def __init__(self):
        super().__init__()

    def train(self, idss, ipal=None, state=None):
        # This Combiner does not need to be trained
        pass

    def combine(self, msg):
        alert = any(msg["alerts"].values())
        return alert, 1 if alert else 0

    def _get_model(self):
        return {}

    def _load_model(self, model):
        return {}
