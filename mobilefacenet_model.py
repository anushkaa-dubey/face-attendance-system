import torch
import torch.nn as nn
import torch.nn.functional as F


class Conv_block(nn.Module):
    def __init__(self, in_c, out_c, kernel, stride, padding=0, groups=1):
        super().__init__()

        self.conv = nn.Conv2d(
            in_c,
            out_c,
            kernel,
            stride,
            padding,
            groups=groups,
            bias=False
        )

        self.bn = nn.BatchNorm2d(out_c)
        self.prelu = nn.PReLU(out_c)

    def forward(self, x):
        return self.prelu(self.bn(self.conv(x)))


class Linear_block(nn.Module):
    def __init__(self, in_c, out_c, kernel, stride, padding=0, groups=1):
        super().__init__()

        self.conv = nn.Conv2d(
            in_c,
            out_c,
            kernel,
            stride,
            padding,
            groups=groups,
            bias=False
        )

        self.bn = nn.BatchNorm2d(out_c)

    def forward(self, x):
        return self.bn(self.conv(x))


class Depth_Wise(nn.Module):
    def __init__(self, in_c, out_c, stride, expansion=2):
        super().__init__()

        mid_c = out_c * expansion

        self.conv = Conv_block(
            in_c,
            mid_c,
            1,
            1
        )

        self.conv_dw = Conv_block(
            mid_c,
            mid_c,
            3,
            stride,
            1,
            groups=mid_c
        )

        self.project = Linear_block(
            mid_c,
            out_c,
            1,
            1
        )

        self.residual = (stride == 1 and in_c == out_c)

    def forward(self, x):
        shortcut = x

        x = self.conv(x)
        x = self.conv_dw(x)
        x = self.project(x)

        if self.residual:
            x = x + shortcut

        return x


class Residual(nn.Module):
    def __init__(self, channels, num_block):
        super().__init__()

        modules = []

        for _ in range(num_block):
            modules.append(
                Depth_Wise(
                    channels,
                    channels,
                    1
                )
            )

        self.model = nn.Sequential(*modules)

    def forward(self, x):
        return self.model(x)


class Output_layer(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv_6_dw = Linear_block(
            512,
            512,
            7,
            1,
            0,
            groups=512
        )

        self.linear = nn.Linear(
            512,
            136,
            bias=False
        )

        self.bn = nn.BatchNorm1d(136)

    # def forward(self, x):
    #     x = self.conv_6_dw(x)
    #     x = x.view(x.shape[0], -1)
    #     x = self.linear(x)
    #     x = self.bn(x)

    #     return x
    def forward(self, x):
        x = self.conv_6_dw(x)
        x = x.view(x.shape[0], -1)

        return x


class MobileFaceNet(nn.Module):

    def __init__(self):
        super().__init__()

        self.conv1 = Conv_block(
            3, 64, 3, 2, 1
        )

        self.conv2_dw = Conv_block(
            64, 64, 3, 1, 1,
            groups=64
        )

        self.conv_23 = Depth_Wise(
            64, 64, 2
        )

        self.conv_3 = Residual(
            64, 4
        )

        self.conv_34 = Depth_Wise(
            64, 128, 2
        )

        self.conv_4 = Residual(
            128, 6
        )

        # IMPORTANT:
        # checkpoint expects 512 intermediate channels here
        self.conv_45 = Depth_Wise(
            128,
            128,
            2,
            expansion=4
        )

        self.conv_5 = Residual(
            128, 2
        )

        self.conv_6_sep = Conv_block(
            128,
            512,
            1,
            1
        )

        self.output_layer = Output_layer()

    def forward(self, x):

        x = self.conv1(x)
        x = self.conv2_dw(x)

        x = self.conv_23(x)
        x = self.conv_3(x)

        x = self.conv_34(x)
        x = self.conv_4(x)

        x = self.conv_45(x)
        x = self.conv_5(x)

        x = self.conv_6_sep(x)

        x = self.output_layer(x)

        return F.normalize(x, p=2, dim=1)