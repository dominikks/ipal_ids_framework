from .voting.Or import OrCombiner
from .voting.MajorityVote import MajorityVote


combiners = [MajorityVote, OrCombiner]


def get_all_combiners():
    return {combiner._name: combiner for combiner in combiners}

