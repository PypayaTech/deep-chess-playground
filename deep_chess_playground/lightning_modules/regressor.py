from deep_chess_playground.lightning_modules.basic_module import BasicModule
from torchmetrics import MeanSquaredError, MeanAbsoluteError, R2Score
from torch import nn


class Regressor(BasicModule):
    def __init__(self, pytorch_module, optimizer, metrics=None, **kwargs):
        metrics = metrics or {}
        metrics.setdefault("mse", MeanSquaredError())
        metrics.setdefault("mae", MeanAbsoluteError())
        metrics.setdefault("r2", R2Score())
        loss_fn = nn.MSELoss()
        super().__init__(pytorch_module, optimizer, loss_fn, metrics)
