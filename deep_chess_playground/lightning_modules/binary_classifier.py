from deep_chess_playground.lightning_modules.basic_module import BasicModule
from torchmetrics.classification import BinaryAccuracy, BinaryPrecision, BinaryRecall, BinaryF1Score
from torch import nn


class BinaryClassifier(BasicModule):
    def __init__(self, pytorch_module, optimizer, threshold=0.5, metrics=None, **kwargs):
        metrics = metrics or {}
        metrics.setdefault("accuracy", BinaryAccuracy(threshold=threshold))
        metrics.setdefault("precision", BinaryPrecision(threshold=threshold))
        metrics.setdefault("recall", BinaryRecall(threshold=threshold))
        metrics.setdefault("f1", BinaryF1Score(threshold=threshold))
        loss_fn = nn.BCEWithLogitsLoss()
        super().__init__(pytorch_module, optimizer, loss_fn, metrics)
