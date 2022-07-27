from combiner.combiner import Combiner


class OrCombiner(Combiner):

    _name = "Or"

    def __init__(self):
        super().__init__()

    def train(self, idss, ipal=None, state=None):
        # This Combiner does not need to be trained
        pass

    def process_ipal_msg(self, ids_outputs):
        alert = any([alert for alert, metric in ids_outputs.values()])
        return alert, 1 if alert else 0

    def process_state_msg(self, ids_outputs):
        # For this combiner, ipal and state behave identical
        return self.process_ipal_msg(ids_outputs)

    def _get_model(self):
        return {}

    def _load_model(self, model):
        return {}
