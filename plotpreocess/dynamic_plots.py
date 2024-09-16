import json
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator
import matplotlib.font_manager as fm
from ctgucode.tools.SetGlobalVariables import config_loader, RelLabel

class DynDataVisualizer:
    def __init__(self, input_dir, output_dir, dynfilename='DynSemantic.json'):
        """
        初始化数据可视化类。

        :param input_dir: 输入文件夹路径
        :param output_dir: 输出图表保存文件夹
        :param dynfilename: 数据文件名
        """
        self.input_json_path = os.path.join(input_dir, dynfilename)
        self.output_dir = output_dir
        self.data = self.load_data()
        self.labels, self.time_means, self.space_means = self.extract_data()
        self._configure_plot()
        self.en_labels = self._generate_english_labels()  # 生成英文标签映射
        os.makedirs(self.output_dir, exist_ok=True)

    def _configure_plot(self):
        """
        配置绘图参数以支持中文显示和负号显示。
        """
        # 设置全局字体样式和大小
        # 设置全局字体
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 中文字体
        plt.rcParams['font.family'] = 'sans-serif'  # 使用无衬线字体系列
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # 查找 Times New Roman 字体路径
        try:
            times_new_roman = fm.findfont(fm.FontProperties(family='Times New Roman'))
            plt.rcParams['font.family'] = ['sans-serif', 'Times New Roman']  # 设置英文字体
        except:
            # 如果找不到 Times New Roman，则使用默认字体
            plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号 '-' 显示为方块的问题
        plt.rcParams['font.size'] = 22  # 设置全局字体大小
        plt.rcParams['axes.titlesize'] = 24  # 设置标题字体大小
        plt.rcParams['axes.labelsize'] = 22  # 设置 x 和 y 轴标签字体大小
        plt.rcParams['xtick.labelsize'] = 22  # 设置 x 轴刻度标签字体大小
        plt.rcParams['ytick.labelsize'] = 22  # 设置 y 轴刻度标签字体大小
        plt.rcParams['legend.fontsize'] = 22  # 设置图例字体大小

    def load_data(self):
        """
        读取 JSON 文件数据。

        :return: JSON 数据
        """
        with open(self.input_json_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def extract_data(self):
        """
        提取 JSON 数据中的标签、时间平均值和空间平均值。

        :return: 标签列表、时间平均值数组、空间平均值数组
        """
        labels = []
        time_means = []
        space_means = []

        for key, value in self.data.items():
            labels.append(key)
            time_means.append(value.get("T", 0))
            space_means.append(value.get("L", 0))

        return labels, np.array(time_means), np.array(space_means)

    def _generate_english_labels(self):
        """
        从 RelLabel 生成英文标签映射。

        :return: 原标签到英文标签的映射
        """
        en_labels = {chinese_label: details['english'] for chinese_label, details in RelLabel.items()}
        return en_labels

    def plot_time_space_mean_sorted(self):
        """
        绘制时间和空间文本占比平均值排序图（按时间排序），中文和英文版本。
        """
        self._plot_time_space_mean_sorted_version('cn', self.labels, '时间和空间维度动态语义图（按时间降序）',
                                                  '动态语义值', self.time_means, self.space_means, '时间维度', '空间维度')
        self._plot_time_space_mean_sorted_version('en', [self.en_labels.get(label, label) for label in self.labels],
                                                  'Dynamic Semantic Features of Tuples (Descending by Time)',
                                                  'Dynamic Semantics Value', self.time_means, self.space_means, 'Time', 'Space')

    def _plot_time_space_mean_sorted_version(self, lang, labels, title, ylabel, time_means, space_means, time_label, space_label):
        """
        绘制时间和空间文本占比平均值排序图。

        :param lang: 语言版本 ('中文' 或 '英文')
        :param labels: 标签列表
        :param title: 图表标题
        :param ylabel: y 轴标签
        :param time_means: 时间文本占比平均值
        :param space_means: 空间文本占比平均值
        :param time_label: 时间维度标签
        :param space_label: 空间维度标签
        """
        sorted_indices = np.argsort(time_means)[::-1]
        sorted_labels = [labels[i] for i in sorted_indices]
        sorted_time_means = time_means[sorted_indices]
        sorted_space_means = space_means[sorted_indices]

        x = np.arange(len(sorted_labels))  # 标签位置
        width = 0.35  # 柱状图的宽度

        plt.figure(figsize=(13, 13))
        plt.bar(x - width / 2, sorted_time_means, width, label=time_label, color='#D95319', alpha=0.7)
        plt.bar(x + width / 2, sorted_space_means, width, label=space_label, color='#EDB120', alpha=0.7)

        plt.ylabel(ylabel)
        plt.ylim(0, 1.2)
        plt.gca().yaxis.set_major_locator(MultipleLocator(0.1))
        plt.title(title)
        plt.xticks(x, sorted_labels, rotation=90)
        plt.legend()
        plt.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5, color='lightgray', alpha=0.8)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'time_space_mean_sorted_{lang}.png'))
        # plt.show()

    @staticmethod
    def add_labels(bars):
        """
        为柱状图添加数据标签。

        :param bars: 柱状图对象
        """
        for bar in bars:
            height = bar.get_height()
            plt.annotate(f'{height:.2f}',
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),  # 3 points vertical offset
                         textcoords="offset points",
                         ha='center', va='bottom')


# if __name__ == '__main__':
#     dynfile = 'DynSemantic_new.json'
#     inputfile = config_loader.get_value('resultpath', 'stc_dynsemantic_path')
#     outputfolder = config_loader.get_value('resultpath', 'stc_DynSemanticPlot_path')
#     visualizer = DataVisualizer(input_dir=inputfile, output_dir=outputfolder, dynfilename=dynfile)
#     visualizer.plot_time_space_mean_sorted()
