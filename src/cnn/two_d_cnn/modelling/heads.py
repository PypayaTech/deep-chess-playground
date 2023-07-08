import torch.nn as nn
import pytorch_lightning as pl


class AlphaZeroMoveClassificationHead(pl.LightningModule):
    """The head is used to propose good moves.

    It has the same format as AlphaZero architecture.
    "A move in chess may be described in two parts: selecting the piece to move, and then...".
    Check this paper for more details https://arxiv.org/abs/1712.01815."""
    def __init__(self, input_planes):
        super().__init__()
        self.conv = nn.Conv2d(input_planes, 73, kernel_size=(1, 1), padding="valid")
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.conv(x)
        x = self.relu(x)
        x = self.softmax(x)
        return x


class ValueWDLHead(pl.LightningModule):
    """The head is used to evaluate the position. The output is probability distribution [W, D, L] where:\n
    W - white wins\n
    D - draw\n
    L - white losses"""
    def __init__(self, input_planes):
        super().__init__()
        self.conv = nn.Conv2d(input_planes, 3, kernel_size=(1, 1), padding="valid")
        self.relu = nn.ReLU()
        self.global_average_pooling = nn.AdaptiveAvgPool2d((1, 1))
        self.flatten = nn.Flatten()
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        x = self.conv(x)
        x = self.relu(x)
        x = self.global_average_pooling(x)
        x = self.flatten(x)
        x = self.softmax(x)
        return x
