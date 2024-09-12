import torch.nn as nn
from deep_chess_playground.pytorch_modules.cnn.two_d_cnn.simple_modules import ConvolutionalBlock, ResidualBlock


class ConvolutionalTower:
    def __init__(self, input_planes, num_blocks, channels):
        super().__init__(channels, channels)
        self.blocks = nn.ModuleList()
        self.blocks.append(ConvolutionalBlock(input_planes, channels))
        for _ in range(num_blocks - 1):
            self.blocks.append(ConvolutionalBlock(channels, channels))

    def forward(self, x):
        for block in self.blocks:
            x = block(x)
        return x


class ResidualTower:
    def __init__(self, input_planes, num_blocks, channels):
        super().__init__(channels, channels)
        self.blocks = nn.ModuleList()
        self.blocks.append(ResidualBlock(input_planes, channels))
        for _ in range(num_blocks - 1):
            self.blocks.append(ResidualBlock(channels, channels))

    def forward(self, x):
        for block in self.blocks:
            x = block(x)
        return x
