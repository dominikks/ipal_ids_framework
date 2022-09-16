from combiner.other.GurobiCombiner import GurobiCombiner
from combiner.voting.MetricVote import MetricVote
from .voting.And import AndCombiner
from .oracle.OptimalCombiner import OptimalCombiner
from .other.HeuristicCombiner import HeuristicCombiner
from .voting.WeightedVote import WeightedVote
from .voting.Or import OrCombiner
from .voting.MajorityVote import MajorityVote


combiners = [
    MajorityVote,
    OrCombiner,
    AndCombiner,
    WeightedVote,
    MetricVote,
    HeuristicCombiner,
    OptimalCombiner,
    GurobiCombiner,
]


def get_all_combiners():
    return {combiner._name: combiner for combiner in combiners}

