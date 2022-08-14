from combiner.combiner import Combiner


class OptimalCombiner(Combiner):
    """
    This combiner is an oracle that always classifies correctly when at least one of the given IDSs classifies correctly.
    """

    _name = "OptimalCombiner"

    def __init__(self, name=None):
        super().__init__(name=name)

    def combine(self, msg):
        malicious = msg["malicious"] is not False
        ids_outputs = list(msg["alerts"].values())

        if malicious in ids_outputs:
            # At least one is correct: give correct output
            return malicious, 1 if malicious else 0
        else:
            # All IDSs are wrong: give wrong output
            return not malicious, 0 if malicious else 1

