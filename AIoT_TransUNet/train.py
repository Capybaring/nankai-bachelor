import argparse
import os
from trainer import trainer

# 添加参数扩展
parser = argparse.ArgumentParser()
# 二分类
parser.add_argument(
    "--num_classes", type=int, default=2, help="output channel of network"
)
# 训练轮次
parser.add_argument(
    "--epoch", type=int, default=50, help="maximum epoch number to train"
)
# 训练批次大小
parser.add_argument("--batch_size", type=int, default=32, help="batch_size per gpu")
# 确定性训练
parser.add_argument(
    "--deterministic", type=int, default=1, help="whether use deterministic training"
)
# 步长
parser.add_argument(
    "--base_lr", type=float, default=0.01, help="segmentation network learning rate"
)
# 图片大小256
parser.add_argument(
    "--img_size", type=int, default=256, help="input patch size of network input"
)
# 添加数据集
parser.add_argument("--dataset", type=str, default="isic2018", help="dataset name")
# 添加参数
args = parser.parse_args()

# 数据集路径
DATASET_PATH = os.path.join("D:\\developProgram\\AIoT\\dataset", args.dataset)
# 快照路径
SNAPSHOT_PATH = os.path.join("./model/", "snapshot/")

if __name__ == "__main__":
    # 调用训练器
    trainer(args, DATASET_PATH, SNAPSHOT_PATH)
