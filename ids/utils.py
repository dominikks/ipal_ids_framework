from .autoregression.Autoregression import Autoregression
from .classifier.BLSTM import BLSTM
from .classifier.DecisionTree import DecisionTree
from .classifier.ExtraTrees import ExtraTrees
from .classifier.IsolationForest import IsolationForest
from .classifier.NaiveBayes import NaiveBayes
from .classifier.RandomForest import RandomForest
from .classifier.SVM import SVM
from .interarrivaltime.Mean import InterArrivalTimeMean
from .interarrivaltime.Range import InterArrivalTimeRange
from .simple.histogram import Histogram
from .simple.minmax import MinMax
from .simple.steadytime import SteadyTime
from .oracles.OptimalIDS import OptimalIDS
from .oracles.DummyIDS import DummyIDS
from .oracles.PrecomputedIDS import PrecomputedIDS

idss = [
    Autoregression,
    BLSTM,
    DecisionTree,
    DummyIDS,
    ExtraTrees,
    Histogram,
    InterArrivalTimeMean,
    InterArrivalTimeRange,
    IsolationForest,
    MinMax,
    NaiveBayes,
    OptimalIDS,
    RandomForest,
    SVM,
    SteadyTime,
    PrecomputedIDS,
]


def get_all_iidss():
    return {ids._name: ids for ids in idss}
