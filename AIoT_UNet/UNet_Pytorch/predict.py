import numpy as np
import torch
import os
import skimage.io as io
import models.unet as unet
import utils.postprocessing as pp
import utils.utils as utils

# 解析命令行参数
args = utils.get_args()
# 数据集文件夹路径
DATASET_PATH = "D:\\developProgram\\AIoT\\dataset"
# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的文件夹路径
current_folder_path = os.path.dirname(current_file_path)
# 获取数据集文件夹路径
BASE_PATH = os.path.join(DATASET_PATH, args.dataset)
# 模型路径
MODEL_PATH = os.path.join(current_folder_path, "saved_models", args.dataset, "net.pth")
# 数据集路径
DATASET_PATH = os.path.join(BASE_PATH, "test/images/")
# 创建预测掩码保存的文件夹
PRED_MASKS_PATH = os.path.join("D:\\developProgram\\AIoT\\pred_masks\\UNet", args.dataset)


def load_model(path):
    model = unet.Unet(filters=8)
    model.load_state_dict(torch.load(path))
    return model


def get_datasets(path_folder):
    file_list = utils.list_files_path(path_folder)
    img_list = []
    for file in file_list:
        img_list.append(utils.yield_img(file))
    return img_list, file_list


def predict(model_path, dataset_path):
    net = load_model(model_path)
    img_list, file_list = get_datasets(dataset_path)
    for i, img in enumerate(img_list):
        file_name = file_list[i].split("/")[-1]
        mask = net(torch.Tensor(img))
        mask = np.array(mask.detach().numpy())
        mask = (mask > 0.5).astype(np.uint8).reshape(256, 256) * 255
        # 保存预测的掩码
        io.imsave(
            os.path.join(PRED_MASKS_PATH, file_name),
            mask,
        )


if __name__ == "__main__":
    predict(MODEL_PATH, DATASET_PATH)
