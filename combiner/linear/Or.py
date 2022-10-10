from combiner.combiner import Combiner


class OrCombiner(Combiner):

    _name = "Or"

    def __init__(self, name=None):
        super().__init__(name=name)

    def combine(self, msg):
        alert = any(msg["alerts"].values())
        return alert, 1 if alert else 0
