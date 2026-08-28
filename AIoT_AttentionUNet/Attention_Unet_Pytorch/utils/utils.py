import argparse
import os
import random
import re

import matplotlib.pyplot as plt
import numpy as np


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


def visualize(imgs, pred):
    fig = plt.figure(figsize=(15, 10))
    columns = 2
    rows = 5  # nb images
    ax = []  # loop around here to plot more images
    i = 0
    for j, img in enumerate(imgs):
        ax.append(fig.add_subplot(rows, columns, i + 1))
        ax[-1].set_title("Input")
        plt.imshow(img, cmap="gray")
        ax.append(fig.add_subplot(rows, columns, i + 2))
        ax[-1].set_title("Mask")
        plt.imshow(pred[j], cmap="gray")
        i += 2
        if i >= 15:
            break
    # plt.show()
    fig.savefig("plots/prediction.png")
    plt.close(fig)


def plot_att_map(img, map):
    """
    Plot the attention map and save it.

    :param img: Original image
    :type img: np.array
    :param map: Attention map
    :type map: np.array
    """
    # 确保 img 和 map 是 numpy 数组
    img = np.array(img)
    map = np.array(map)
    
    # 计算注意力图的实际尺寸
    att_size = int(np.sqrt(map.size))  # 假设注意力图是正方形
    
    # 重塑注意力图
    map = map.reshape(att_size, att_size)
    
    # 如果需要，将注意力图调整为与原图相同的尺寸
    if att_size != img.shape[0]:
        from skimage.transform import resize
        map = resize(map, (img.shape[0], img.shape[1]))
    
    # 创建图形
    plt.figure(figsize=(10, 5))
    
    # 显示原图
    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title('Original Image')
    plt.axis('off')
    
    # 显示注意力图
    plt.subplot(1, 2, 2)
    plt.imshow(img, cmap='gray', alpha=0.5)
    plt.imshow(map, cmap='jet', alpha=0.5)
    plt.title('Attention Map')
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig('plots/att_map.png')
    plt.close()


def learning_curves(train, val):
    fig, ax = plt.subplots(1, figsize=(12, 8))
    fig.suptitle("Training Curves")
    ax.plot(train, label="Entraînement")
    ax.plot(val, label="Validation")
    ax.set_ylabel("Loss", fontsize=14)
    ax.set_xlabel("Epoch", fontsize=14)
    fig.savefig("plots/plot.png")
    plt.close(fig)


def get_args():
    """
    Argument parser.

    :return: Object containing all the parameters needed to train a model
    :rtype: Dict
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--epochs", "-e", type=int, default=1, help="number of epochs of training"
    )
    parser.add_argument(
        "--batch_size", "-bs", type=int, default=16, help="size of the batches"
    )
    parser.add_argument("--lr", type=float, default=0.001, help="adam: learning rate")
    parser.add_argument(
        "--att", "-a",
        dest="att",
        action="store_true",
        help="If flag, use attention block",
    )
    parser.add_argument(
        "--size", type=int, default=256, help="Size of the image, one number"
    )
    parser.add_argument("--drop_r", "-d", type=float, default=0.2, help="Dropout rate")
    parser.add_argument(
        "--filters", "-f",
        type=int,
        default=8,
        help="Number of filters in first conv block",
    )
    args = parser.parse_args()
    print_red(args)
    return args
