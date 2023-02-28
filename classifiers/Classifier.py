class Classifier:
    def classify(self, test_data):
        pass


class ThresholdClassifier(Classifier):
    def __init__(self, thresholds):
        self.thresholds = thresholds

    def classify(self, test_data):
        touched = False
        for j, rc in enumerate(test_data):
            if rc < self.thresholds[j]:
                touched = True
        return touched
