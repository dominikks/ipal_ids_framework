from combiner.combiner import Combiner


class MajorityVote(Combiner):

    _name = "MajorityVote"

    def __init__(self, idss):
        super().__init__(idss=idss)

    def train(self, idss, ipal=None, state=None):
        # This Combiner does not need to be trained
        pass

    def process_ipal_msg(self, ids_outputs):
        # Count the number of alerts as votes
        vote_count = sum([ids_outputs[ids][0] for ids in self.settings["ipal-idss"]])

        alert = vote_count > (len(self.settings["ipal-idss"]) / 2)
        return alert, 1 if alert else 0

    def process_state_msg(self, ids_outputs):
        # Count the number of alerts as votes
        vote_count = sum([ids_outputs[ids][0] for ids in self.settings["state-idss"]])

        alert = vote_count > (len(self.settings["state-idss"]) / 2)
        return alert, 1 if alert else 0

    def _get_model(self):
        return {}

    def _load_model(self, model):
        return {}
