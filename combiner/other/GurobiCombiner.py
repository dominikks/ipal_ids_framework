from combiner.combiner import Combiner
import gurobipy
import ipal_iids.settings as settings


class GurobiCombiner(Combiner):

    _name = "GurobiCombiner"
    _needs_training = True

    _gurobicombiner_default_settings = {"use_metrics": False}

    def __init__(self, name=None):
        super().__init__(name=name)
        self._add_default_settings(self._gurobicombiner_default_settings)

        self._weights = None

    def _get_activation(self, msg, ids_name):
        return float(
            msg["metrics" if self.settings["use_metrics"] else "alerts"][ids_name]
        )

    def train(self, msgs):
        ids_names = list(msgs[0]["alerts"].keys())

        settings.logger.info("Creating Gurobi model for optimization")

        # Create the optimization model
        m = gurobipy.Model(self._name)

        # Add a weight variable for each ids
        weight_vars = [m.addVar(name=f"w_{ids_name}") for ids_name in ids_names]

        # Add a slack variable for each message
        slack_vars = [m.addVar(name=f"slack_{i}") for i in range(len(msgs))]

        # The objective is to minimize the slack
        m.setObjective(
            gurobipy.quicksum([var ** 2 for var in slack_vars]), gurobipy.GRB.MINIMIZE,
        )

        # Add soft constraints for each message
        for msg_index, msg in enumerate(msgs):
            activations = [
                self._get_activation(msg, ids_name) for ids_name in ids_names
            ]

            s = gurobipy.quicksum(
                weight_vars[i] * activations[i] for i in range(len(ids_names))
            )

            if msg["malicious"] is not False:
                m.addConstr(s + slack_vars[msg_index] >= 1)
            else:
                # We cannot use strict inequality as gurobi does not support it
                m.addConstr(s - slack_vars[msg_index] <= 1)

        settings.logger.info("Starting model optimization...")
        m.optimize()
        settings.logger.info(f"Optimization done, objective value: {m.objVal}")

        self._weights = {
            ids_name: weight_var.x
            for ids_name, weight_var in zip(ids_names, weight_vars)
        }
        settings.logger.info(f"Weights: {self._weights}")

    def combine(self, msg):
        weighted_sum = sum(
            [
                self._weights.get(name, 0) * float(metric)
                for name, metric in msg[
                    "metrics" if self.settings["use_metrics"] else "alerts"
                ].items()
            ]
        )

        alert = weighted_sum >= 1
        return alert, weighted_sum

    def _get_model(self):
        return {"weights": self._weights}

    def _load_model(self, model):
        self._weights = model["weights"]
