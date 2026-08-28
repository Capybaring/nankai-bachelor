import argparse
import logging
import os
import sys
import torch
import networks.vit_seg_configs as vit_seg_configs
from networks.vit_seg_modeling import VisionTransformer as ViT
from predictor import predictor

parser = argparse.ArgumentParser()

parser.add_argument(
    "--num_classes", type=int, default=2, help="output channel of network"
)
parser.add_argument(
    "--img_size", type=int, default=256, help="input patch size of network input"
)
parser.add_argument(
    "--dataset", type=str, default="BUSI-256", help="experiment_name"
)

args = parser.parse_args()


# 数据集路径
DATASET_PATH = os.path.join("D:\\developProgram\\AIoT\\dataset", args.dataset)
# 快照路径
SNAPSHOT_PATH = os.path.join("./pred/", "snapshot/")
# 模型路径
MODEL_PATH = os.path.join("D:\\developProgram\\AIoT\\TransUNet\\saved_model", args.dataset, "net.pth")
# 预测保存路径
PREDICTION_SAVE_PATH = os.path.join(
    "D:\\developProgram\\AIoT\\pred_masks\\TransNet", args.dataset
)
# 配置模型参数
CONFIG = vit_seg_configs.config


if __name__ == "__main__":
    # 配置模型信息
    model = ViT(CONFIG, img_size=args.img_size, num_classes=args.num_classes).cpu()
    # 加载模型
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device("cpu")))
    logging.basicConfig(
        filename=os.path.join(SNAPSHOT_PATH, "log.txt"),
        level=logging.INFO,
        format="[%(asctime)s.%(msecs)03d] %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info(str(args))

    predictor(args, model, PREDICTION_SAVE_PATH, DATASET_PATH)
