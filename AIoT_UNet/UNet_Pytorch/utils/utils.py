import argparse
import os
import random
import re
import skimage.io as io
import skimage.color as color
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import numpy as np


def yield_img(file, size=256):
    """
    读取并处理单个图像文件。

    :param file: 图像文件路径
    :param size: 图像目标尺寸
    :return: 处理后的图像数组
    """
    img = io.imread(file)
    # 处理三通道图像
    if len(img.shape) == 3 and img.shape[2] == 3:
        # 将RGB图像转换为灰度图
        img = color.rgb2gray(img)
        # print(f"转换为灰度后的形状: {img.shape}")
    # 归一化处理
    img = np.array(img) / 255
    # 调整图像尺寸
    if img.shape != (size, size):
        from skimage.transform import resize

        img = resize(img, (size, size), anti_aliasing=True)
    # 重塑为模型输入格式 (batch=1, channels=1, height, width)
    img = img.reshape(1, 1, size, size)
    return img


def list_files_path(path):
    """
    List files from a path.

    :param path: Folder path
    :type path: str
    :return: A list containing all files in the folder
    :rtype: List
    """
    return sorted_alphanumeric(
        [path + f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    )


def shuffle_lists(lista, listb, seed=42):
    """
    Shuffle two list with the same seed.

    :param lista: List of elements
    :type lista: List
    :param listb: List of elements
    :type listb: List
    :param seed: Seed number
    :type seed: int
    :return: lista and listb shuffled
    :rtype: (List, List)
    """
    random.seed(seed)
    random.shuffle(lista)
    random.seed(seed)
    random.shuffle(listb)
    return lista, listb


def print_red(skk):
    """
    Print in red.

    :param skk: Str to print
    :type skk: str
    """
    print("\033[91m{}\033[00m".format(skk))


def print_gre(skk):
    """
    Print in green.

    :param skk: Str to print
    :type skk: str
    """
    print("\033[92m{}\033[00m".format(skk))


def sorted_alphanumeric(data):
    """
    Sort function.

    :param data: str list
    :type data: List
    :return: Sorted list
    :rtype: List
    """
    convert = lambda text: int(text) if text.isdigit() else text.lower()  # noqa
    alphanum_key = lambda key: [convert(c) for c in re.split("([0-9]+)", key)]  # noqa
    return sorted(data, key=alphanum_key)


def learning_curves(
    train_losses,
    val_losses,
    save_path,
    title="Training and Validation Curves",
    best_marker=True,
    early_stop_threshold=None,
):
    """
    绘制专业的学习曲线图表（无平滑处理）

    :param train_losses: 训练损失列表
    :param val_losses: 验证损失列表
    :param save_path: 图表保存路径
    :param title: 图表标题
    :param best_marker: 是否标记最佳验证点
    :param early_stop_threshold: 提前停止阈值 (在曲线上标记)
    """
    # 确保输入有效
    if len(train_losses) == 0 or len(val_losses) == 0:
        print("警告: 没有损失数据可绘制")
        return

    # 创建图表
    plt.figure(figsize=(12, 8))

    # 绘制曲线
    epochs = range(1, len(train_losses) + 1)
    plt.plot(
        epochs,
        train_losses,
        "b-",
        linewidth=2.5,
        alpha=0.7,
        marker="o",
        markersize=5,
        label="Training Loss",
    )
    plt.plot(
        epochs,
        val_losses,
        "r-",
        linewidth=2.5,
        alpha=0.7,
        marker="s",
        markersize=5,
        label="Validation Loss",
    )

    # 标记最佳验证点
    if best_marker and len(val_losses) > 0:
        best_epoch = np.argmin(val_losses) + 1
        best_val = min(val_losses)
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
    if early_stop_threshold is not None and len(val_losses) > early_stop_threshold:
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
    all_losses = train_losses + val_losses
    max_loss = max(all_losses)
    min_loss = min(all_losses)
    margin = (max_loss - min_loss) * 0.1  # 10%边距
    plt.ylim(max(0, min_loss - margin), max_loss + margin)

    # 添加图例
    plt.legend(
        fontsize=12, loc="upper right" if min_loss < max_loss / 2 else "lower right"
    )

    # 添加额外信息框
    info_text = f"Final Train Loss: {train_losses[-1]:.4f}\nFinal Val Loss: {val_losses[-1]:.4f}"
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


def get_args():
    """
    Argument parser.

    :return: Object containing all the parameters needed to train a model
    :rtype: Dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", "-ds", type=str, default="BUSI-256", help="dataset name"
    )
    parser.add_argument(
        "--epochs", "-e", type=int, default=10, help="number of epochs of training"
    )
    parser.add_argument(
        "--batch_size", "-bs", type=int, default=16, help="size of the batches"
    )
    parser.add_argument("--lr", type=float, default=0.001, help="adam: learning rate")
    parser.add_argument(
        "--size", type=int, default=256, help="Size of the image, one number"
    )
    parser.add_argument("--drop_r", "-d", type=float, default=0.2, help="Dropout rate")
    parser.add_argument(
        "--filters",
        "-f",
        type=int,
        default=8,
        help="Number of filters in first conv block",
    )
    args = parser.parse_args()
    return args
