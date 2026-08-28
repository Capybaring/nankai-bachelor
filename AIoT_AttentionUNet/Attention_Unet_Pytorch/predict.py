# -*- coding: utf-8 -*-

import numpy as np
import skimage.io as io
import skimage.color as color  # 导入 color 模块
import torch
import os

import models.unet as unet
import utils.postprocessing as pp
import utils.utils as utils

# 数据集文件夹路径
DATASET_PATH = "D:\\developProgram\\AIoT\\dataset"
# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的文件夹路径
current_folder_path = os.path.dirname(current_file_path)
# 获取数据集文件夹路径
BASE_PATH = os.path.join(DATASET_PATH, "isic2018/")


def pred(net, imgs):
    output, _ = net(torch.Tensor(imgs))  # 移除.cuda()
    return output


def load_model(path):
    model = unet.Unet(filters=8, attention=True)  # 移除.cuda()
    model.load_state_dict(torch.load(path))
    return model


# predict.py


def yield_img(file, size=256):
    """
    读取并处理单个图像文件。

    :param file: 图像文件路径
    :param size: 图像目标尺寸
    :return: 处理后的图像数组
    """
    img = io.imread(file)

    # 打印图像原始尺寸信息，用于调试
    # print(f"图像路径: {file}, 原始形状: {img.shape}")

    # 处理三通道图像
    if len(img.shape) == 3 and img.shape[2] == 3:
        # 将RGB图像转换为灰度图
        img = color.rgb2gray(img)
        # print(f"转换为灰度后的形状: {img.shape}")

    # 归一化处理
    img = np.array(img) / 255

    # 调整图像尺寸（如果需要）
    if img.shape != (size, size):
        from skimage.transform import resize

        img = resize(img, (size, size), anti_aliasing=True)
        print(f"调整尺寸后的形状: {img.shape}")

    # 重塑为模型输入格式 (batch=1, channels=1, height, width)
    img = img.reshape(1, 1, size, size)

    return img


def get_images(path_folder):
    file_list = utils.list_files_path(path_folder)
    img_list = []
    for file in file_list:
        img_list.append(yield_img(file))
    return img_list, file_list


if __name__ == "__main__":
    net = load_model(os.path.join(current_folder_path, "saved_models/net.pth"))
    # print(net)
    img_list, file_list = get_images(BASE_PATH + "test/images/")
    for i, img in enumerate(img_list):
        file_name = file_list[i].split("/")[-1]
        mask = pred(net, img)
        mask = mask.detach().numpy()  # 移除.cpu()
        mask = pp.remove_blobs((mask > 0.5).astype(np.uint8).reshape(256, 256) * 255)
        # 转换为uint8（核心步骤）
        if mask.dtype == np.float32 or mask.dtype == np.float64:
            # 将[0.0, 1.0]转换为[0, 255]
            mask = (mask * 255).astype(np.uint8)
        io.imsave(os.path.join(current_folder_path, "pred_masks", file_name), mask)
