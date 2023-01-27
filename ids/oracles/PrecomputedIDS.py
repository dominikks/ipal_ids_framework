from ids.ids import MetaIDS


class PrecomputedIDS(MetaIDS):

    _name = "Precomputed"
    _description = "Dummy IDS that is never meant to do any classifications. Only used as a dummy with precomputed outputs for combiners."

    def __init__(self, name=None):
        super().__init__(name=name)

    def train(self, ipal=None, state=None):
        pass

    def new_ipal_msg(self, msg):
        raise NotImplementedError(
            "PrecomputedIDS is not meant to be used for classification."
        )

    def new_state_msg(self, msg):
        raise NotImplementedError(
            "PrecomputedIDS is not meant to be used for classification."
        )

    def save_trained_model(self):
        return True

    def load_trained_model(self):
        return True
