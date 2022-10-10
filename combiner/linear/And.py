from combiner.combiner import Combiner


class AndCombiner(Combiner):

    _name = "And"

    def __init__(self, name=None):
        super().__init__(name=name)

    def combine(self, msg):
        alert = all(msg["alerts"].values())
        return alert, 1 if alert else 0
