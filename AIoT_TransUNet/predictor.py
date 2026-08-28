import numpy as np
from torch.utils.data import DataLoader
from data_process import LoadDataset
from tqdm import tqdm
import logging
import os
import torch
import matplotlib.pyplot as plt
from scipy.ndimage import zoom
from utils import calculate_metric_percase


def test_single_volume(
    image, label, net, classes, patch_size=[256, 256], test_save_path=None, case=None
):
    image, label = (
        image.squeeze(0).cpu().detach().numpy(),
        label.squeeze(0).cpu().detach().numpy(),
    )
    if len(image.shape) == 3 and image.shape[0] > 1:
        prediction = np.zeros_like(label)
        for ind in range(image.shape[0]):
            slice = image[ind, :, :]
            x, y = slice.shape[0], slice.shape[1]
            if x != patch_size[0] or y != patch_size[1]:
                slice = zoom(slice, (patch_size[0] / x, patch_size[1] / y), order=3)
            input = torch.from_numpy(slice).unsqueeze(0).unsqueeze(0).float().cpu()
            net.eval()
            with torch.no_grad():
                outputs = net(input)
                out = torch.argmax(torch.softmax(outputs, dim=1), dim=1).squeeze(0)
                out = out.cpu().detach().numpy()
                if x != patch_size[0] or y != patch_size[1]:
                    pred = zoom(out, (x / patch_size[0], y / patch_size[1]), order=0)
                else:
                    pred = out
                prediction[ind] = pred
    else:
        if len(image.shape) == 3 and image.shape[0] == 1:
            image = image[0]  # 降维到(256,256)

        input = torch.from_numpy(image).unsqueeze(0).unsqueeze(0).float().cpu()
        net.eval()
        with torch.no_grad():
            out = torch.argmax(torch.softmax(net(input), dim=1), dim=1).squeeze(0)
            prediction = out.cpu().detach().numpy()
    metric_list = []
    for i in range(1, classes):
        metric_list.append(calculate_metric_percase(prediction == i, label == i))

    # 只保存预测图片
    plt.figure(figsize=(8, 8))
    # 使用灰度颜色映射显示预测结果
    plt.imshow(prediction, cmap="gray", vmin=0, vmax=1)
    plt.axis("off")
    plt.savefig(
        os.path.join(test_save_path, f"{case}_pred.png"),
        bbox_inches="tight",
        pad_inches=0,
        dpi=150,
    )
    plt.close()
    return metric_list


def predictor(args, model, test_save_path=None, file_path=None):
    db_test = LoadDataset(base_dir=file_path, model="test")
    testloader = DataLoader(db_test, batch_size=1, shuffle=False, num_workers=1)
    logging.info("{} test iterations per epoch".format(len(testloader)))
    model.eval()
    metric_list = 0.0
    for i_batch, sampled_batch in tqdm(enumerate(testloader)):
        h, w = sampled_batch["image"].size()[2:]
        image, label, case_name = (
            sampled_batch["image"],
            sampled_batch["label"],
            sampled_batch["case_name"][0],
        )
        metric_i = test_single_volume(
            image,
            label,
            model,
            classes=args.num_classes,
            patch_size=[args.img_size, args.img_size],
            test_save_path=test_save_path,
            case=case_name,
        )
        metric_list += np.array(metric_i)
        logging.info(
            "idx %d case %s mean_dice %f mean_hd95 %f"
            % (
                i_batch,
                case_name,
                np.mean(metric_i, axis=0)[0],
                np.mean(metric_i, axis=0)[1],
            )
        )
    metric_list = metric_list / len(db_test)
    for i in range(1, args.num_classes):
        logging.info(
            "Mean class %d mean_dice %f mean_hd95 %f"
            % (i, metric_list[i - 1][0], metric_list[i - 1][1])
        )
    performance = np.mean(metric_list, axis=0)[0]
    mean_hd95 = np.mean(metric_list, axis=0)[1]
    logging.info(
        "Testing performance in best val model: mean_dice : %f mean_hd95 : %f"
        % (performance, mean_hd95)
    )
    return "Testing Finished!"
