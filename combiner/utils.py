from .voting.MajorityVote import MajorityVote


combiners = [MajorityVote]


def get_all_combiners():
    return {combiner._name: combiner for combiner in combiners}

