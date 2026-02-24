from RandomJungle.Models.BaseRFModel import BaseRFModel


class RfHostBin(BaseRFModel):
    def __init__(self):
        super().__init__(
            n_estimators=250,
            max_depth=15,
            min_samples_split=6,
            min_samples_leaf=3,
            class_weight="balanced"
        )
