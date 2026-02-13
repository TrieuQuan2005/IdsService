from src.RandomJungle.Models.BaseRFModel import BaseRFModel


class RfHostBin(BaseRFModel):
    def __init__(self):
        super().__init__(
            n_estimators=300,
            max_depth = 20,
            min_samples_split = 5,
            min_samples_leaf = 2,
            class_weight = "balanced_subsample",
        )
