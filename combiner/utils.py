from .ml.SVMCombiner import SVMCombiner
from .other.GurobiCombiner import GurobiCombiner
from .linear.MetricVote import MetricVote
from .linear.And import AndCombiner
from .oracle.OptimalCombiner import OptimalCombiner
from .other.HeuristicCombiner import HeuristicCombiner
from .linear.WeightedVote import WeightedVote
from .linear.Or import OrCombiner
from .linear.MajorityVote import MajorityVote
from .linear.LogisticRegression import LogisticRegression


combiners = [
    MajorityVote,
    OrCombiner,
    AndCombiner,
    WeightedVote,
    MetricVote,
    HeuristicCombiner,
    OptimalCombiner,
    GurobiCombiner,
    SVMCombiner,
    LogisticRegression,
]


def get_all_combiners():
    return {combiner._name: combiner for combiner in combiners}

