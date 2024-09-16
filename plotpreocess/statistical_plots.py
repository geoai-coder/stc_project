import json
import matplotlib.pyplot as plt
import numpy as np
import os
from matplotlib.ticker import MultipleLocator
import matplotlib.font_manager as fm
from ctgucode.tools.SetGlobalVariables import config_loader, RelLabel

class StaDataVisualizer:
    def __init__(self, input_dir,input_m, filenum, output_dir):
        """
        初始化 DataVisualizer 实例。

        参数:
        filenum (str): 文件编号。
        input_dir (str): 输入文件目录。
        output_dir (str): 输出图表目录。
        """
        self.filenum = filenum
        self.input_path = os.path.join(input_dir,input_m, f'GeoRelAnalyseBootstrap_{filenum}.json')
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.data = self._load_data()
        self.labels, self.time_means, self.time_std, self.space_means, self.space_std = self._extract_data()
        self._configure_plot()
        self.en_labels = self._generate_english_labels()  # 生成英文标签

    def _load_data(self):
        """
        从 JSON 文件中加载数据。

        返回:
        dict: 加载的 JSON 数据。
        """
        with open(self.input_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _extract_data(self):
        """
        提取需要的数据。

        返回:
        tuple: 包含标签、时间占比平均值、时间占比标准差、空间占比平均值、空间占比标准差的元组。
        """
        labels = []
        time_means = []
        time_std = []
        space_means = []
        space_std = []

        for key, value in self.data.items():
            labels.append(key)
            time_means.append(value["时间文本占比平均值"])
            time_std.append(value["时间文本占比标准差"])
            space_means.append(value["空间文本占比平均值"])
            space_std.append(value["空间文本占比标准差"])

        return labels, np.array(time_means), np.array(time_std), np.array(space_means), np.array(space_std)

    def _generate_english_labels(self):
        """
        从 RelLabel 生成英文标签映射。

        返回:
        dict: 原标签到英文标签的映射。
        """
        en_labels = {chinese_label: details['english'] for chinese_label, details in RelLabel.items()}
        print(en_labels)
        return en_labels

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

    def _sort_data(self, means, lang_labels):
        """
        对数据进行降序排序。

        参数:
        means (np.array): 要排序的平均值数组。

        返回:
        tuple: 包含排序后的标签、平均值和索引的元组。
        """
        sorted_indices = np.argsort(means)[::-1]
        sorted_labels = [lang_labels[i] for i in sorted_indices]
        sorted_means = means[sorted_indices]
        return sorted_labels, sorted_means, sorted_indices

    def plot_time_space_mean_sorted(self):
        """
        绘制时间和空间占比平均值排序图（按时间排序），中文和英文版本。
        """
        self._plot_time_space_mean_sorted_version('cn', self.labels, '时间和空间文本占比平均值排序图（按时间降序）',
                                                  '文本占比平均值', self.time_means, self.time_std, self.space_means,
                                                  self.space_std, '时间文本占比', '空间文本占比')
        self._plot_time_space_mean_sorted_version('en', [self.en_labels.get(label, label) for label in self.labels],
                                                  'Spatio-Temporal Information Dependency (Descending by Time)',
                                                  'Spatio-Temporal Dependency Value', self.time_means, self.time_std,
                                                  self.space_means, self.space_std, 'Time',
                                                  'Space')

    def _plot_time_space_mean_sorted_version(self, lang, labels, title, ylabel, time_means, time_std, space_means,
                                             space_std, time_label, space_label):
        """
        绘制时间和空间占比平均值排序图。

        参数:
        lang (str): 语言版本 ('中文' 或 '英文')。
        labels (list): 标签列表。
        title (str): 图表标题。
        ylabel (str): y 轴标签。
        time_means (np.array): 时间文本占比平均值。
        time_std (np.array): 时间文本占比标准差。
        space_means (np.array): 空间文本占比平均值。
        space_std (np.array): 空间文本占比标准差。
        time_label (str): 时间文本占比标签。
        space_label (str): 空间文本占比标签。
        """
        sorted_labels, sorted_time_means, sorted_indices = self._sort_data(time_means, labels)
        sorted_time_std = time_std[sorted_indices]
        sorted_space_means = space_means[sorted_indices]
        sorted_space_std = space_std[sorted_indices]

        x = np.arange(len(sorted_labels))
        width = 0.35

        plt.figure(figsize=(13, 13))
        plt.bar(x - width / 2, sorted_time_means, width, label=time_label, color='skyblue', alpha=0.7, edgecolor='None')
        plt.bar(x + width / 2, sorted_space_means, width, label=space_label, color='lightgreen', alpha=0.7,
                edgecolor='None')

        plt.errorbar(x - width / 2, sorted_time_means, yerr=sorted_time_std, fmt='none', ecolor='lightgray', capsize=5)
        plt.errorbar(x + width / 2, sorted_space_means, yerr=sorted_space_std, fmt='none', ecolor='lightgray',
                     capsize=5)

        plt.ylabel(ylabel)
        plt.ylim(0, 1.2)
        plt.gca().yaxis.set_major_locator(MultipleLocator(0.1))
        plt.title(title)
        plt.xticks(x, sorted_labels, rotation=90)
        plt.legend(loc='upper right', bbox_to_anchor=(1, 1))
        plt.subplots_adjust(right=0.85)
        plt.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5, color='lightgray', alpha=0.8)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f'{self.filenum}_{lang}_time_space_mean_sorted.png'))
        # plt.show()

    def _add_labels(self, bars):
        """
        在柱状图上添加数据标签。

        参数:
        bars (BarContainer): 柱状图的容器对象。
        """
        for bar in bars:
            height = bar.get_height()
            plt.annotate(f'{height:.2f}',
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 3),  # 3 points vertical offset
                         textcoords="offset points",
                         ha='center', va='bottom')


# if __name__ == '__main__':
#     # 使用示例
#     inputfolder = config_loader.get_value('resultpath', 'stc_bootstrapAnalyse_path')
#     outputfolder = config_loader.get_value('resultpath', 'stc_StatisticalPlot_path')
#     filenum = 'new_10_10'
#     visualizer = DataVisualizer(input_dir=inputfolder, filenum=filenum, output_dir=outputfolder)
#     visualizer.plot_time_space_mean_sorted()
