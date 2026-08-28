import numpy as np
from numpy import array
import pandas as pd
import matplotlib.pyplot as plt
import math
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import torch
import torch.nn as nn


# 将时间序列按照指定时间片进行划分
def split_sequences(sequences, in_steps, out_steps):
    X, y = list(), list()
    for i in range(len(sequences) - 1):
        # 检查是否越界
        if i + in_steps + out_steps > len(sequences):
            break
        X.append(sequences[i : i + in_steps, :-1])
        y.append(sequences[i + in_steps : i + in_steps + out_steps, -1])
    return array(X), array(y)


# 获取原始数据集
df = pd.read_csv("merged_file.csv")
data = df[["avg_sentiment_score", "high", "low", "open", "close", "volume", "close"]]
# 转原始数据为numpy数组
data = np.array(data, dtype=np.float32)
# 获取特征数据平均值
mean = np.mean(data, axis=0)
# 获取特征数据方差
std = np.std(data, axis=0)
# 获取标准化后的数据
data = (data - mean) / std
# 按照0.9的比例划分训练集和验证集
data_train_ratio = 0.9
split_index = int(data_train_ratio * data.shape[0])
# 指定时间片
n_steps_in, n_steps_out = 10, 1
# 划分数据集
x_train, y_train = split_sequences(data[:split_index, :], n_steps_in, n_steps_out)
x_test, y_test = split_sequences(data[split_index:, :], n_steps_in, n_steps_out)

# 转为torch张量
x_train = torch.from_numpy(x_train).type(torch.Tensor)
y_train = torch.from_numpy(y_train).type(torch.Tensor)
x_test = torch.from_numpy(x_test).type(torch.Tensor)
y_test = torch.from_numpy(y_test).type(torch.Tensor)


# 反标准化
def inverse_normalize(standardized_data):
    # 对每个数据进行反标准化
    if isinstance(standardized_data, list):
        return [inverse_normalize(x) for x in standardized_data]
    return standardized_data * std[4] + mean[4]


# 输入维度
input_dim = 6
hidden_dim = 32
num_layers = 2
# 输出维度
output_dim = 1
# 训练轮次
num_epochs = 200


# 定义训练模型
class LSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim):
        super(LSTM, self).__init__()
        # 隐藏层维度
        self.hidden_dim = hidden_dim
        # 隐藏层数量
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    # 前向传播
    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).requires_grad_()
        out, (hn, cn) = self.lstm(x, (h0.detach(), c0.detach()))
        out = self.fc(out[:, -1, :])
        return out


# 初始化模型
model = LSTM(
    input_dim=input_dim,
    hidden_dim=hidden_dim,
    output_dim=output_dim,
    num_layers=num_layers,
)
# 计算损失值
loss_fn = torch.nn.MSELoss(size_average=True)
# 优化器
optimiser = torch.optim.Adam(model.parameters(), lr=0.01)
# 记录损失值
hist = np.zeros(num_epochs)
# 模型训练
for t in range(num_epochs):
    y_train_pred = model(x_train)
    # 计算准确率
    if len(y_train_pred) > 1 and len(y_train) > 1:
        # 判断增长趋势
        pred_ = y_train_pred[1:] > y_train_pred[:-1]
        label_ = y_train[1:] > y_train[:-1]
        accuracy = (label_ == pred_).sum().item() / len(pred_)
    else:
        accuracy = 0
    # 计算损失值
    loss = loss_fn(y_train_pred, y_train)
    if (t + 1) % 20 == 0:
        print("Epoch ", t + 1, "Loss: ", loss.item(),"Accuracy:", accuracy)
    hist[t] = loss.item()
    optimiser.zero_grad()
    loss.backward()
    optimiser.step()

# 模型预测
y_test_pred = model(x_test)
# 测试集上的预测值
y_test_pred = [inverse_normalize(preds) for preds in (y_test_pred.detach().numpy())]
y_test = [inverse_normalize(labels) for labels in (y_test.detach().numpy())]


# 绘图
def data_plot(preds, labels):
    # 设置时间步长
    day = 40
    # x轴数据
    days = list(range(day))
    # y轴数据
    preds = preds[:day]
    labels = labels[:day]
    # 设置画布大小
    fig, ax = plt.subplots(figsize=(12, 6))
    # 添加x,y内容
    ax.plot(days, preds, label="预测值", color="red")
    ax.plot(days, labels, label="实际值", color="blue")
    # 设置横纵主题
    ax.set_xlabel("时间步")
    ax.set_ylabel("开盘价")
    # 设置图表主题
    ax.set_title("LSTM预测开盘价 vs 实际开盘价")
    # 自定义参数
    plt.rcParams["font.sans-serif"] = ["SimHei"]
    plt.rcParams["axes.unicode_minus"] = False
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    # 保存
    plt.savefig("./prediction_result/lstm-prediction.png")
    # 绘图
    plt.show()


data_plot(y_test_pred, y_test)
