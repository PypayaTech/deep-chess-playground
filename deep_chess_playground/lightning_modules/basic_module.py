import pytorch_lightning as pl


class BasicModule(pl.LightningModule):
    def __init__(self, pytorch_module, optimizer, loss_fn, metrics=None):
        super().__init__()
        self.pytorch_module = pytorch_module
        self.optimizer = optimizer
        self.loss_fn = loss_fn
        self.metrics = metrics or {}

    def forward(self, x):
        return self.pytorch_module(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        self.log("train_loss", loss)
        for name, metric in self.metrics.items():
            self.log(f"train_{name}", metric(y_hat, y))
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        self.log("val_loss", loss)
        for name, metric in self.metrics.items():
            self.log(f"val_{name}", metric(y_hat, y))
        return loss

    def test_step(self, batch, batch_idx):
        x, y = batch
        y_hat = self(x)
        loss = self.loss_fn(y_hat, y)
        self.log("test_loss", loss)
        for name, metric in self.metrics.items():
            self.log(f"test_{name}", metric(y_hat, y))
        return loss

    def configure_optimizers(self):
        return self.optimizer

    def add_metric(self, name, metric):
        self.metrics[name] = metric
