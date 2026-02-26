class SystemMetric:

    def __init__(self, name="HybridSystem"):
        self.name = name
        self.tp = 0
        self.tn = 0
        self.fp = 0
        self.fn = 0

    def update(self, y_true: int, y_pred: int):
        if y_true == 1 and y_pred == 1:
            self.tp += 1
        elif y_true == 0 and y_pred == 0:
            self.tn += 1
        elif y_true == 0 and y_pred == 1:
            self.fp += 1
        elif y_true == 1 and y_pred == 0:
            self.fn += 1

    def recall(self):
        return self.tp / (self.tp + self.fn) if (self.tp + self.fn) else 0

    def fpr(self):
        return self.fp / (self.fp + self.tn) if (self.fp + self.tn) else 0

    def precision(self):
        return self.tp / (self.tp + self.fp) if (self.tp + self.fp) else 0

    def accuracy(self):
        total = self.tp + self.tn + self.fp + self.fn
        return (self.tp + self.tn) / total if total else 0

    def report(self):
        print(f"\n=== {self.name} ===")
        print(f"TP: {self.tp}  TN: {self.tn}  FP: {self.fp}  FN: {self.fn}")
        print(f"Recall (Detection Rate): {self.recall():.4f}")
        print(f"FPR                   : {self.fpr():.4f}")
        print(f"Precision             : {self.precision():.4f}")
        print(f"Accuracy              : {self.accuracy():.4f}")