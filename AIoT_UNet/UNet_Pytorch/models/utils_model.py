import torch
import torch.nn as nn


class DoubleConv(nn.Module):
    """(convolution => [BN] => ReLU) * 2"""

    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.double_conv(x)


class Down_Block(nn.Module):
    """Downscaling with maxpool then double conv"""

    def __init__(self, in_channels, out_channels, drop=0.5):
        super().__init__()
        self.conv = DoubleConv(in_channels, out_channels)
        self.down = nn.Sequential(nn.MaxPool2d(2), nn.Dropout(drop))

    def forward(self, x):
        c = self.conv(x)
        return c, self.down(c)


class Bridge(nn.Module):
    def __init__(self, in_channels, out_channels, drop):
        super().__init__()
        self.conv = nn.Sequential(
            DoubleConv(in_channels, out_channels), nn.Dropout(drop)
        )

    def forward(self, x):
        return self.conv(x)


class Up_Block(nn.Module):
    """Upscaling then double conv"""

    def __init__(self, in_channels, out_channels, drop=0.5):
        super().__init__()
        self.up = nn.ConvTranspose2d(
            in_channels, out_channels, kernel_size=(2, 2), stride=(2, 2)
        )
        self.conv = nn.Sequential(
            DoubleConv(in_channels, out_channels), nn.Dropout(p=drop)
        )
    def forward(self, x, conc):
        x1 = self.up(x)
        x = torch.cat([conc, x1], dim=1)
        return None, self.conv(x)


class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1), nn.Sigmoid()
        )

    def forward(self, x):
        return self.conv(x)