from deep_chess_playground.lightning_modules.basic_module import BasicModule
from torchmetrics.classification import MulticlassAccuracy, MulticlassPrecision, MulticlassRecall, MulticlassF1Score
from torch import nn


class MultiClassClassifier(BasicModule):
    def __init__(self, pytorch_module, optimizer, num_classes, metrics=None, **kwargs):
        metrics = metrics or {}
        metrics.setdefault("accuracy", MulticlassAccuracy(num_classes=num_classes))
        metrics.setdefault("precision", MulticlassPrecision(num_classes=num_classes))
        metrics.setdefault("recall", MulticlassRecall(num_classes=num_classes))
        metrics.setdefault("f1", MulticlassF1Score(num_classes=num_classes))
        loss_fn = nn.CrossEntropyLoss()
        super().__init__(pytorch_module, optimizer, loss_fn, metrics)
