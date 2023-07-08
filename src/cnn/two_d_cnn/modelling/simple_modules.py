import torch.nn as nn


class ConvolutionalBlock(nn.Module):
    def __init__(self, in_channels=256, out_channels=256, kernel_size=(3, 3), padding="same"):
        super().__init__()
        self.conv = nn.Conv2d(in_channels=in_channels,
                              out_channels=out_channels,
                              kernel_size=kernel_size,
                              padding=padding)
        self.relu = nn.ReLU()
        self.batch_norm = nn.BatchNorm2d(num_features=out_channels)

    def forward(self, x):
        x = self.conv(x)
        x = self.relu(x)
        x = self.batch_norm(x)
        return x


class ResidualBlock(nn.Module):
    def __init__(self, in_channels=256, out_channels=256, kernel_size=(3, 3), padding="same"):
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=in_channels,
                      out_channels=out_channels,
                      kernel_size=kernel_size,
                      padding=padding),
            nn.BatchNorm2d(in_channels),
            nn.ReLU())
        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=out_channels,
                      out_channels=out_channels,
                      kernel_size=kernel_size,
                      padding=padding),
            nn.BatchNorm2d(in_channels))
        self.relu = nn.ReLU()

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.conv2(out)
        out += residual
        out = self.relu(out)
        return out
