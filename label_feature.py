# Storage class for LABELS-FEATURES object correspondings
class LabelFeature:

    def __init__(self, labels: list, features: list) -> None:
        self.labels = labels
        self.features = features
