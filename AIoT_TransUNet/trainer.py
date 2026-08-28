import logging
import sys
import torch
import torch.optim as optim
import utils
from data_process import LoadDataset
from torch.nn.modules.loss import CrossEntropyLoss
from torch.utils.data import DataLoader
from tqdm import tqdm
from utils import DiceLoss
import networks.vit_seg_configs as vit_seg_configs
from networks.vit_seg_modeling import VisionTransformer as ViT


# 配置模型参数
CONFIG = vit_seg_configs.config


def trainer(args, file_path, snapshot_path):
    logging.basicConfig(
        filename=snapshot_path + "/log.txt",
        level=logging.INFO,
        format="[%(asctime)s.%(msecs)03d] %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.info(str(args))

    # 初始化网络
    model = ViT(
        CONFIG,
        img_size=args.img_size,
        num_classes=args.num_classes,
    ).cpu()
    # 初始化参数
    base_lr = args.base_lr
    epoch = args.epoch
    # 加载数据集
    trainloader = DataLoader(
        LoadDataset(base_dir=file_path),
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=False,
        persistent_workers=True,
    )
    # 计算迭代次数
    iterations = epoch * len(trainloader)
    # 损失函数
    ce_loss = CrossEntropyLoss()
    dice_loss = DiceLoss(args.num_classes)
    # 初始化优化器
    optimizer = optim.SGD(
        model.parameters(), lr=base_lr, momentum=0.9, weight_decay=0.0001
    )
    # 加载模型
    model = model.to("cpu")
    model.train()

    logging.info(
        "{} iterations per epoch. {} max iterations ".format(
            len(trainloader), iterations
        )
    )

    iter_num = 0

    epoch_progress = tqdm(
        range(epoch),
        desc="全局Epoch进度",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [已用:{elapsed}, 剩余:{remaining}]",
    )
    epoch_losses = []
    for epoch_num in epoch_progress:
        batch_progress = tqdm(
            enumerate(trainloader),  # 核心：迭代trainloader
            total=len(trainloader),  # 显示总batch数
            desc=f"Epoch {epoch_num+1}/{epoch}",
            leave=False,  # 完成后自动清除
        )
        batch_losses = []
        for i_batch, sampled_batch in batch_progress:
            # 获取数据
            image_batch = sampled_batch["image"]
            label_batch = sampled_batch["label"]
            # 得到输出
            outputs = model(image_batch)
            # 计算损失
            loss_ce = ce_loss(outputs, label_batch[:].long())
            loss_dice = dice_loss(outputs, label_batch, softmax=True)
            # 记录损失
            loss = 0.5 * loss_ce + 0.5 * loss_dice
            batch_losses.append(loss.item())
            # 优化器清零
            optimizer.zero_grad()
            # 反向传播
            loss.backward()
            optimizer.step()
            # 计算步长
            lr_ = base_lr * (1.0 - iter_num / iterations) ** 0.9
            for param_group in optimizer.param_groups:
                param_group["lr"] = lr_

            iter_num = iter_num + 1
            logging.info(
                "iteration %d : loss : %f, loss_ce: %f"
                % (iter_num, loss.item(), loss_ce.item())
            )
        epoch_losses.append(sum(batch_losses) / len(batch_losses))
        if epoch_num >= epoch - 1:
            save_mode_path = "./saved_model/net.pth"
            torch.save(model.state_dict(), save_mode_path)
            logging.info("save model to {}".format(save_mode_path))
            # 绘制损失曲线
            utils.learning_curves(
                losses=epoch_losses,
                save_path=snapshot_path + "/loss_curves.png",
                title="Training Losses",
                epoch=epoch_num + 1,
            )

    return "Training Finished!"
