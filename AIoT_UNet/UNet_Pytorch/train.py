import os
import numpy as np
import progressbar
import skimage.io as io
import sklearn.model_selection as sk
import torch
import torch.nn as nn
import torch.optim as optim
import models.unet as unet
import utils.data as data
import utils.utils as utils
import logging
import sys

# 解析命令行参数
args = utils.get_args()
# 进度条的格式
widgets = [
    " [",
    progressbar.Timer(),
    "] ",
    progressbar.Bar(),
    " (",
    progressbar.ETA(),
    ") ",
]
# 数据集文件夹路径
DATASET_PATH = "D:\\developProgram\\AIoT\\dataset"
# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 获取当前文件所在的文件夹路径
current_folder_path = os.path.dirname(current_file_path)
# 获取数据集文件夹路径
BASE_PATH = os.path.join(DATASET_PATH, args.dataset)
# 定义保存模型的路径
SAVE_PATH = os.path.join(current_folder_path, "saved_models", args.dataset, "net.pth")
# 定义数据集图片路径
IMG_PATH = os.path.join(BASE_PATH, "train/images/")
# 定义数据集标签路径
LABEL_PATH = os.path.join(BASE_PATH, "train/masks/")
# 定义保存模型的损失值，初始值无穷大
LOSS = np.inf
# 定义快照路径
snapshot_path = os.path.join(current_folder_path, "plots", args.dataset)


def save_model(net, loss):
    global LOSS
    if loss < LOSS:
        LOSS = loss
        torch.save(net.state_dict(), SAVE_PATH)


def get_datasets(path_img, path_label, config):
    # 获取数据集路径
    img_path_list = utils.list_files_path(path_img)
    label_path_list = utils.list_files_path(path_label)
    # 打乱数据集
    img_path_list, label_path_list = utils.shuffle_lists(img_path_list, label_path_list)
    # 8：2划分训练集和验证集
    img_train, img_val, label_train, label_val = sk.train_test_split(
        img_path_list, label_path_list, test_size=0.2, random_state=42
    )
    # 读取数据集
    dataset_train = data.JB_Dataset(
        config.batch_size, config.size, img_train, label_train
    )
    dataset_val = data.JB_Dataset(config.batch_size, config.size, img_val, label_val)
    return dataset_train, dataset_val


def train(path_imgs, path_labels, config, epochs=5):
    # 创建快照目录
    logging.basicConfig(
        filename=snapshot_path + "/log.txt",
        level=logging.INFO,
        format="[%(asctime)s.%(msecs)03d] %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info(str(args))
    # 获得UNet模型
    net = unet.Unet(config.filters)
    # 使用Adam优化器
    optimizer = optim.Adam(net.parameters(), lr=config.lr)
    criterion = nn.BCELoss()
    # 加载数据集
    dataset_train, dataset_val = get_datasets(path_imgs, path_labels, config)
    # 初始化损失列表
    train_loss = []
    val_loss = []
    # 调度器
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, epochs)
    # 训练模型
    for epoch in range(epochs):
        epoch_train_loss = []
        epoch_val_loss = []
        utils.print_gre("Epoch {}/{}".format(epoch + 1, epochs))
        # 训练模式
        with progressbar.ProgressBar(
            max_value=len(dataset_train), widgets=widgets
        ) as bar:
            net.train()
            for i in range(len(dataset_train)):
                bar.update(i)
                # 获取数据
                imgs, labels = dataset_train[i]
                # 优化器清零
                optimizer.zero_grad()
                # 得到模型输出
                output = net(imgs)
                # 计算损失
                loss_train = criterion(output, labels)
                # 反向传播
                loss_train.backward()
                # 更新参数
                optimizer.step()
                epoch_train_loss.append(loss_train.item())
        # 计算平均损失
        train_loss_epoch = np.array(epoch_train_loss).mean()
        train_loss.append(train_loss_epoch)
        # 验证模式
        with progressbar.ProgressBar(
            max_value=len(dataset_val), widgets=widgets
        ) as bar2:
            net.eval()
            for j in range(len(dataset_val)):
                bar2.update(j)
                output = net(imgs)
                loss_val = criterion(output, labels)
                epoch_val_loss.append(loss_val.item())
        val_loss_epoch = np.array(epoch_val_loss).mean()
        val_loss.append(val_loss_epoch)
        # 记录日志
        logging.info(
            "iteration %d : train_loss : %f, val_loss: %f"
            % (epoch + 1, train_loss_epoch, val_loss_epoch)
        )
        # 打印损失
        utils.print_gre(
            "Loss train {}\nLoss val {}".format(
                np.array(epoch_train_loss).mean(), val_loss_epoch
            )
        )
        scheduler.step()
    # 保存模型
    save_model(net, val_loss_epoch)
    # 绘制学习曲线
    try:
        utils.learning_curves(
            train_loss, val_loss, snapshot_path + "/learning_curves.png"
        )
    except Exception as e:
        logging.error("Error during learning curves visualization: {}".format(e))
    # 返回最佳模型
    return net


if __name__ == "__main__":
    net = train(
        IMG_PATH,
        LABEL_PATH,
        config=args,
        epochs=args.epochs,
    )
