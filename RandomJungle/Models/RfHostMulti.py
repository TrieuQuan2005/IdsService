from RandomJungle.Models.BaseRFModel import BaseRFModel


class RfHostMulti(BaseRFModel):
    def __init__(self):
        super().__init__(
            n_estimators=200,
            max_depth=10,
            min_samples_split=8,
            min_samples_leaf=4,
            class_weight="balanced"
        )
