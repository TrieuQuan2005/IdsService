class MultiClassMetric:

    def __init__(self, name="MultiClassModel"):
        self.name = name
        self.total = 0
        self.correct = 0
        self.class_total = {}
        self.class_correct = {}

    def update(self, y_true, y_pred):
        self.total += 1

        # tổng theo từng class
        self.class_total[y_true] = self.class_total.get(y_true, 0) + 1

        if y_true == y_pred:
            self.correct += 1
            self.class_correct[y_true] = self.class_correct.get(y_true, 0) + 1

    def accuracy(self):
        return self.correct / self.total if self.total else 0

    def per_class_accuracy(self):
        result = {}
        for cls in self.class_total:
            correct = self.class_correct.get(cls, 0)
            total = self.class_total[cls]
            result[cls] = correct / total if total else 0
        return result

    def report(self):
        print(f"\n=== {self.name} ===")
        print(f"Overall Accuracy: {self.accuracy():.4f}")
        print("Per-class Accuracy:")
        for cls, acc in self.per_class_accuracy().items():
            print(f"  {cls}: {acc:.4f}")