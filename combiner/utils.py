from .voting.WeightedVote import WeightedVote
from .voting.Or import OrCombiner
from .voting.MajorityVote import MajorityVote


combiners = [MajorityVote, OrCombiner, WeightedVote]


def get_all_combiners():
    return {combiner._name: combiner for combiner in combiners}

