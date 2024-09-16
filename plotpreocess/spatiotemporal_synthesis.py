import json
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.font_manager as fm
from matplotlib.ticker import MultipleLocator
from ctgucode.tools.SetGlobalVariables import config_loader, RelLabel


class All_DataVisualizer:
    def __init__(self, input_json_dyn: str,file_m: str, input_dir_sta: str, filenum: str, output_dir_plt: str,
                 mergedata_output_file: str = 'merged_data.json', dynfilename: str = 'DynSemantic.json'):
        self.filenum = filenum
        self.input_path_sta = os.path.join(input_dir_sta,file_m, f'GeoRelAnalyseBootstrap_{filenum}.json')
        self.data_sta = self._load_json(self.input_path_sta)

        self.labels_sta, self.time_means_sta, self.time_std_sta, self.space_means_sta, self.space_std_sta = self._extract_sta_data()

        self.input_json_path = os.path.join(input_json_dyn, dynfilename)
        self.data_dyn = self._load_json(self.input_json_path)
        self.labels_dyn, self.time_means_dyn, self.space_means_dyn = self._extract_dyn_data()

        self.output_dir_plt = output_dir_plt
        self.mergedata_output = os.path.join(output_dir_plt, mergedata_output_file)
        self._configure_plot()
        self.merge_data()
        self.en_labels = self._generate_english_labels()

    def _load_json(self, file_path: str) -> dict:
        """从 JSON 文件中加载数据"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def _generate_english_labels(self) -> dict:
        """从 RelLabel 生成英文标签映射"""
        return {chinese_label: details['english'] for chinese_label, details in RelLabel.items()}

    def _extract_sta_data(self) -> tuple:
        """提取静态数据"""
        labels, time_means, time_std, space_means, space_std = [], [], [], [], []
        for key, value in self.data_sta.items():
            labels.append(key)
            time_means.append(value["时间文本占比平均值"])
            time_std.append(value["时间文本占比标准差"])
            space_means.append(value["空间文本占比平均值"])
            space_std.append(value["空间文本占比标准差"])
        return labels, np.array(time_means), np.array(time_std), np.array(space_means), np.array(space_std)

    def _extract_dyn_data(self) -> tuple:
        """提取动态数据"""
        labels, time_means, space_means = [], [], []
        for key, value in self.data_dyn.items():
            labels.append(key)
            time_means.append(value.get("T", 0))
            space_means.append(value.get("L", 0))
        return labels, np.array(time_means), np.array(space_means)

    def _configure_plot(self) -> None:
        """配置绘图参数以支持中文显示和负号显示"""
        plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.size'] = 22  # 设置全局字体大小
        plt.rcParams['axes.titlesize'] = 24  # 设置标题字体大小
        plt.rcParams['axes.labelsize'] = 22  # 设置 x 和 y 轴标签字体大小
        plt.rcParams['xtick.labelsize'] = 22  # 设置 x 轴刻度标签字体大小
        plt.rcParams['ytick.labelsize'] = 22  # 设置 y 轴刻度标签字体大小
        plt.rcParams['legend.fontsize'] = 22  # 设置图例字体大小

        try:
            times_new_roman = fm.findfont(fm.FontProperties(family='Times New Roman'))
            plt.rcParams['font.family'] = ['sans-serif', 'Times New Roman']
        except Exception as e:
            print(f"Font not found: {e}")
            plt.rcParams['font.family'] = 'sans-serif'

    def _sort_data(self, means: np.ndarray, labels: list) -> tuple:
        """对数据进行降序排序"""
        sorted_indices = np.argsort(means)[::-1]
        sorted_labels = [labels[i] for i in sorted_indices]
        sorted_means = means[sorted_indices]
        return sorted_labels, sorted_means, sorted_indices

    def _plot_sorted(self, means_sta: np.ndarray, means_dyn: np.ndarray, std_sta: np.ndarray, labels: list,
                     ylabel_cn: str, ylabel_en: str, title_cn: str, title_en: str,
                     filename_cn: str, filename_en: str,
                     legend_label_sta_cn: str, legend_label_dyn_cn: str,
                     legend_label_sta_en: str, legend_label_dyn_en: str,
                     color_sta: str, color_dyn: str) -> None:
        """绘制排序图，包含中文和英文版本"""
        # 根据动态数据排序
        sorted_labels, sorted_means_dyn, sorted_indices = self._sort_data(means_dyn, labels)
        sorted_std_sta = std_sta[sorted_indices]

        # 修改这里，确保 sorted_means_sta 和 sorted_labels 一致
        sorted_means_sta = np.array([means_sta[self.labels_sta.index(label)]
                                     if label in self.labels_sta else 0 for label in sorted_labels])

        x = np.arange(len(sorted_labels))
        width = 0.35

        def plot_chart(labels, ylabel, title, filename, legend_label_sta, legend_label_dyn):
            plt.figure(figsize=(13, 13))
            plt.bar(x - width / 2, sorted_means_sta, width, label=legend_label_sta, color=color_sta, alpha=0.7)
            plt.bar(x + width / 2, sorted_means_dyn, width, label=legend_label_dyn, color=color_dyn, alpha=0.7)
            plt.errorbar(x - width / 2, sorted_means_sta, yerr=sorted_std_sta, fmt='none', ecolor='lightgray',
                         capsize=5)
            plt.ylabel(ylabel)
            plt.ylim(0, 1.2)
            plt.gca().yaxis.set_major_locator(MultipleLocator(0.1))
            plt.title(title)
            plt.xticks(x, labels, rotation=90)
            plt.legend()
            plt.grid(True, which='both', axis='both', linestyle='--', linewidth=0.5, color='lightgray', alpha=0.8)
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir_plt, filename))
            # plt.show()

        # 中文版本
        plot_chart(sorted_labels, ylabel_cn, title_cn, filename_cn, legend_label_sta_cn, legend_label_dyn_cn)
        # 英文版本
        sorted_labels_en = [self.en_labels.get(label, label) for label in sorted_labels]
        plot_chart(sorted_labels_en, ylabel_en, title_en, filename_en, legend_label_sta_en, legend_label_dyn_en)

    def plot_time_sorted(self) -> None:
        """绘制时间占比平均值排序图"""
        self._plot_sorted(self.time_means_sta, self.time_means_dyn, self.time_std_sta, self.labels_dyn,
                          '时间文本占比平均值', 'Value',
                          '时间文本占比平均值排序图（按动态时间降序）', 'Dependency Values and Dynamic Semantic Values in the Time Dimension',
                          f'{self.filenum}_time_mean_sorted_cn.png', f'{self.filenum}_time_mean_sorted_en.png',
                          '元组依赖性', '元组动态语义',
                          'Spatio-Temporal Dependency', 'Dynamic Semantics',
                          'skyblue','#D95319')

    def plot_space_sorted(self) -> None:
        """绘制空间占比平均值排序图"""
        self._plot_sorted(self.space_means_sta, self.space_means_dyn, self.space_std_sta, self.labels_dyn,
                          '空间文本占比平均值', 'Value',
                          '空间文本占比平均值排序图（按动态空间降序）', 'Dependency Values and Dynamic Semantic Values in the Space Dimension',
                          f'{self.filenum}_space_mean_sorted_cn.png', f'{self.filenum}_space_mean_sorted_en.png',
                          '元组依赖性', '元组动态语义',
                          'Spatio-Temporal Dependency', 'Dynamic Semantics',
                          'lightgreen','#EDB120')

    def merge_data(self) -> None:
        """合并静态和动态数据，写入 JSON 文件"""
        def format_percentage(value: float) -> str:
            """将值转换为百分比格式"""
            return f"{value * 100:.2f}%" if value is not None else None

        merged_data = {}
        for key, value in self.data_sta.items():
            merged_data.setdefault(key, {})['sta_time'] = format_percentage(value.get('时间文本占比平均值', None))
            merged_data[key]['sta_space'] = format_percentage(value.get('空间文本占比平均值', None))

        for key, value in self.data_dyn.items():
            merged_data.setdefault(key, {})['dyn_time'] = format_percentage(value.get('T', None))
            merged_data[key]['dyn_space'] = format_percentage(value.get('L', None))

        with open(self.mergedata_output, 'w', encoding='utf-8') as file:
            json.dump(merged_data, file, ensure_ascii=False, indent=4)


# if __name__ == '__main__':
#     filenum = '10_10'
#     dynfile = 'DynSemantic_new.json'
#     input_json_dyn = config_loader.get_value('resultpath', 'stc_dynsemantic_path')
#     input_dir_sta = config_loader.get_value('resultpath', 'stc_bootstrapAnalyse_path')
#     output_dir_plt = config_loader.get_value('resultpath', 'stc_allanalysis_path')
#     visualizer = DataVisualizer(input_json_dyn=input_json_dyn, dynfilename=dynfile, input_dir_sta=input_dir_sta,
#                                 filenum=filenum, output_dir_plt=output_dir_plt)
#     visualizer.plot_time_sorted()
#     visualizer.plot_space_sorted()
