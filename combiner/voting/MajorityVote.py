from combiner.combiner import Combiner


class MajorityVote(Combiner):

    _name = "MajorityVote"

    def __init__(self, name=None):
        super().__init__(name=name)

    def combine(self, msg):
        # Count the number of alerts as votes
        vote_count = sum(msg["alerts"].values())

        alert = vote_count > (len(msg["alerts"]) / 2)
        return alert, 1 if alert else 0
