import os
import numpy as np
from PIL import Image
import torch
from scipy.ndimage import zoom
from torch.utils.data import Dataset


def process_sample(sample, output_size):
    """图像预处理函数 (可直接整合到Dataset类中)"""
    image, label = sample["image"], sample["label"]
    h, w = image.shape[:2]
    # 动态调整尺寸
    if (h, w) != output_size:
        # 图像缩放（保持通道）
        image = zoom(image, (output_size[0] / h, output_size[1] / w, 1), order=3)
        # 标签缩放（最近邻）
        label = zoom(label, (output_size[0] / h, output_size[1] / w), order=0)
    # 转换为Tensor并归一化
    image = torch.from_numpy(image.astype(np.float32)).permute(2, 0, 1) / 255.0
    label = (torch.from_numpy(label.astype(np.float32)) > 0.5).long()
    return {"image": image, "label": label}


class LoadDataset(Dataset):
    def __init__(self, base_dir, model="train"):
        # 获取文件路径
        self.image_dir = os.path.join(base_dir, model + "/images")
        self.mask_dir = os.path.join(base_dir, model + "/masks")
        # 获取排序后的文件列表
        self.image_files = [f for f in os.listdir(self.image_dir)]
        self.mask_files = [f for f in os.listdir(self.mask_dir)]

    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        # 获取文件路径
        image_path = os.path.join(self.image_dir, self.image_files[idx])
        mask_path = os.path.join(self.mask_dir, self.mask_files[idx])
        # 读取并预处理数据
        image = np.array(Image.open(image_path).convert("L"))  # 灰度图 [H, W]
        image = np.expand_dims(image, axis=-1)  # 添加通道维度 [H, W, 1]
        mask = np.array(Image.open(mask_path).convert("L"))  # 灰度图 [H, W]
        # 初始二值化处理
        mask = (mask > 128).astype(np.float32)
        # 封装样本
        sample = {"image": image, "label": mask}
        # 处理样本
        sample = process_sample(sample, output_size=(256, 256))
        # 标注
        sample["case_name"] = self.image_files[idx]
        return sample
