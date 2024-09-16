import json
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator

class HistogramPlotter:
    def __init__(self, input_json, input_dir='input', output_dir='output', data_extract_func=None):
        """
        初始化 HistogramPlotter 实例。

        参数:
        input_json (str): 输入 JSON 文件名。
        input_dir (str): 输入文件目录。
        output_dir (str): 输出文件目录。
        data_extract_func (function): 数据提取函数，接受 JSON 数据并返回 (labels, means)。
        """
        self.input_json_path = os.path.join(input_dir, input_json)
        self.output_dir = output_dir
        self.data_extract_func = data_extract_func
        self.data = self.load_data()
        self.labels, self.means = self.extract_data()

        # 配置绘图参数
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
        plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示问题
        os.makedirs(self.output_dir, exist_ok=True)

    def load_data(self):
        """
        从 JSON 文件中加载数据。

        返回:
        dict: 加载的 JSON 数据。
        """
        with open(self.input_json_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def extract_data(self):
        """
        提取数据。使用传入的提取函数。

        返回:
        tuple: 标签列表和均值数组。
        """
        return self.data_extract_func(self.data)

    def plot_sorted_bar(self, labels, values, ylabel, title, filename, color='skyblue', ylim=(0, 1.1)):
        """
        绘制排序后的柱状图。

        参数:
        labels (list): 标签列表。
        values (np.array): 值列表。
        ylabel (str): y 轴标签。
        title (str): 图表标题。
        filename (str): 保存文件名。
        color (str): 柱状图颜色。
        ylim (tuple): y 轴范围。
        """
        plt.figure(figsize=(12, 8))
        plt.bar(labels, values, color=color, alpha=0.7)
        plt.ylabel(ylabel)
        plt.ylim(*ylim)
        plt.gca().yaxis.set_major_locator(MultipleLocator(0.1))
        plt.title(title)
        plt.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5, color='lightgray', alpha=0.8)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename))
        plt.show()

    def plot_time_mean_sorted(self):
        """
        绘制时间文本占比平均值排序图。
        """
        sorted_indices = np.argsort(self.means)[::-1]
        sorted_labels = [self.labels[i] for i in sorted_indices]
        sorted_means = self.means[sorted_indices]
        self.plot_sorted_bar(sorted_labels, sorted_means, '时间文本占比', '时间文本占比排序图', 'time_mean_sorted.png')

    def plot_space_mean_sorted(self):
        """
        绘制空间文本占比平均值排序图。
        """
        sorted_indices = np.argsort(self.means)[::-1]
        sorted_labels = [self.labels[i] for i in sorted_indices]
        sorted_means = self.means[sorted_indices]
        self.plot_sorted_bar(sorted_labels, sorted_means, '空间文本占比', '空间文本占比排序图', 'space_mean_sorted.png', color='lightgreen')

    def plot_time_space_mean_sorted(self):
        """
        绘制时间和空间文本占比平均值排序图（按时间排序）。
        """
        sorted_indices = np.argsort(self.means)[::-1]
        sorted_labels = [self.labels[i] for i in sorted_indices]
        sorted_time_means = self.means[sorted_indices]
        sorted_space_means = self.means[sorted_indices]  # 修改这里根据实际需要提取空间数据

        x = np.arange(len(sorted_labels))
        width = 0.35

        plt.figure(figsize=(14, 10))
        bars1 = plt.bar(x - width / 2, sorted_time_means, width, label='时间文本占比', color='skyblue', alpha=0.7)
        bars2 = plt.bar(x + width / 2, sorted_space_means, width, label='空间文本占比', color='lightgreen', alpha=0.7)

        plt.ylabel('文本占比')
        plt.ylim(0, 1.1)
        plt.gca().yaxis.set_major_locator(MultipleLocator(0.1))
        plt.title('时间和空间文本占比排序图（按时间降序）')
        plt.xticks(x, sorted_labels, rotation=90)
        plt.legend()
        plt.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5, color='lightgray', alpha=0.8)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'time_space_mean_sorted.png'))
        plt.show()
