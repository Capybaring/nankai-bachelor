import numpy as np
import torch
from medpy import metric
import torch.nn as nn
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


class DiceLoss(nn.Module):
    def __init__(self, n_classes):
        super(DiceLoss, self).__init__()
        self.n_classes = n_classes

    def _one_hot_encoder(self, input_tensor):
        tensor_list = []
        for i in range(self.n_classes):
            temp_prob = input_tensor == i  # * torch.ones_like(input_tensor)
            tensor_list.append(temp_prob.unsqueeze(1))
        output_tensor = torch.cat(tensor_list, dim=1)
        return output_tensor.float()

    def _dice_loss(self, score, target):
        target = target.float()
        smooth = 1e-5
        intersect = torch.sum(score * target)
        y_sum = torch.sum(target * target)
        z_sum = torch.sum(score * score)
        loss = (2 * intersect + smooth) / (z_sum + y_sum + smooth)
        loss = 1 - loss
        return loss

    def forward(self, inputs, target, weight=None, softmax=False):
        if softmax:
            inputs = torch.softmax(inputs, dim=1)
        target = self._one_hot_encoder(target)
        if weight is None:
            weight = [1] * self.n_classes
        assert (
            inputs.size() == target.size()
        ), "predict {} & target {} shape do not match".format(
            inputs.size(), target.size()
        )
        class_wise_dice = []
        loss = 0.0
        for i in range(0, self.n_classes):
            dice = self._dice_loss(inputs[:, i], target[:, i])
            class_wise_dice.append(1.0 - dice.item())
            loss += dice * weight[i]
        return loss / self.n_classes


def calculate_metric_percase(pred, gt):
    pred[pred > 0] = 1
    gt[gt > 0] = 1
    if pred.sum() > 0 and gt.sum() > 0:
        dice = metric.binary.dc(pred, gt)
        hd95 = metric.binary.hd95(pred, gt)
        return dice, hd95
    elif pred.sum() > 0 and gt.sum() == 0:
        return 1, 0
    else:
        return 0, 0

def learning_curves(
    losses,
    save_path,
    title="losses",
    best_marker=True,
    early_stop_threshold=None,
    epoch=1,
):
    """
    绘制专业的学习曲线图表（无平滑处理）

    :param losses: 训练损失列表
    :param save_path: 图表保存路径
    :param title: 图表标题
    :param best_marker: 是否标记最佳验证点
    :param early_stop_threshold: 提前停止阈值 (在曲线上标记)
    """

    # 创建图表
    plt.figure(figsize=(12, 8))

    # 绘制曲线（无平滑）
    epochs = range(1, epoch+1)
    plt.plot(
        epochs,
        losses,
        "b-",
        linewidth=2.5,
        alpha=0.7,
        marker='o',
        markersize=5,
        label="Loss",
    )

    # 标记最佳验证点
    if best_marker and len(losses) > 0:
        best_epoch = np.argmin(losses) + 1
        best_val = min(losses)
        plt.scatter(
            best_epoch,
            best_val,
            s=200,
            c="gold",
            marker="*",
            edgecolor="black",
            zorder=10,
            label=f"Best Val: {best_val:.4f} (Epoch {best_epoch})",
        )

        # 添加垂直线
        plt.axvline(x=best_epoch, color="gray", linestyle="--", alpha=0.5)

    # 标记提前停止点（如果有）
    if early_stop_threshold is not None and len(losses) > early_stop_threshold:
        plt.axvline(
            x=early_stop_threshold,
            color="purple",
            linestyle=":",
            linewidth=2,
            label=f"Early Stop Threshold (Epoch {early_stop_threshold})",
        )

    # 设置图表元素
    plt.title(title, fontsize=16, pad=20)
    plt.xlabel("Epochs", fontsize=14)
    plt.ylabel("Loss", fontsize=14)

    # 设置网格和刻度
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.gca().xaxis.set_major_locator(MaxNLocator(integer=True))  # 仅显示整数刻度

    # 自动调整Y轴范围
    all_losses = losses
    max_loss = max(all_losses)
    min_loss = min(all_losses)
    margin = (max_loss - min_loss) * 0.1  # 10%边距
    plt.ylim(max(0, min_loss - margin), max_loss + margin)

    # 添加图例
    plt.legend(
        fontsize=12, loc="upper right" if min_loss < max_loss / 2 else "lower right"
    )

    # 添加额外信息框
    info_text = f"Final Loss: {losses[-1]:.4f}"
    plt.figtext(
        0.15,
        0.02,
        info_text,
        fontsize=11,
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray"),
    )

    # 保存高质量图表
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"学习曲线已保存至: {save_path}")