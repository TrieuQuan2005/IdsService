from RandomJungle.Models.BaseRFModel import BaseRFModel


class RfFlowMulti(BaseRFModel):
    def __init__(self):
        super().__init__(
            n_estimators=400,
            max_depth = 25,
            min_samples_split = 4,
            min_samples_leaf = 1,
            class_weight = "balanced_subsample",
        )
