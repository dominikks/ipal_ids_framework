from combiner.combiner import Combiner


class MajorityVote(Combiner):
    def __init__(self, name=None):
        super().__init__(name=name)

    def train(self, idss, ipal=None, state=None):
        # This Combiner does not need to be trained
        pass

    def _process_event(self, event):
        # Count the number of alerts as votes
        vote_count = sum([alert for alert, metric in event])

        alert = vote_count >= (len(self.settings["idss"]) / 2)
        return alert, 1 if alert else 0

    def _get_model(self):
        return {}

    def _load_model(self, model):
        return {}
