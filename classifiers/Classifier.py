class Classifier:
    def classify(self, test_data):
        pass


class ThresholdClassifier(Classifier):
    def __init__(self, baseline, rate=0.99):
        self.thresholds = baseline * rate

    def classify(self, test_data):
        touched = False
        for j, rc in enumerate(test_data):
            if rc < self.thresholds[j]:
                touched = True
        return touched

#
# class RandomForestClassifier(Classifier):
#     def __init__(self):
#         # self.model = ?
#         # want to load a pretrained model
#
#     def classify(self, test_data):
#         pass
#
#
#     def classify(self):
