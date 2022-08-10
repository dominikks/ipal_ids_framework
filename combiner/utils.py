from .oracle.OptimalCombiner import OptimalCombiner
from .voting.WeightedVote import WeightedVote
from .voting.Or import OrCombiner
from .voting.MajorityVote import MajorityVote


combiners = [MajorityVote, OrCombiner, WeightedVote, OptimalCombiner]


def get_all_combiners():
    return {combiner._name: combiner for combiner in combiners}

