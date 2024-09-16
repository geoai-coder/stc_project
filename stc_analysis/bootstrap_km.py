import os
import json
import random
from scipy import stats
import jieba
import numpy as np
from tqdm import tqdm
from ctgucode.tools.LTP_ import LTP_
from ctgucode.tools.SetGlobalVariables import config_loader


def process_file(file_path, m, k):
    """处理单个文件并计算时间和空间文本的统计数据"""
    print(f'正在统计文件 {file_path}')
    all_lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # 使用 line.strip() 来去除行尾的换行符
                all_lines.append(line.strip())

    time_ratios, space_ratios = [], []
    text_lengths, words_num = [], []

    for _ in range(m):
        sample_lines = random.choices(all_lines, k=min(k, len(all_lines) * 2))
        time_count, space_count = 0, 0
        total_words = 0
        for line in sample_lines:
            lineltp = LTP_(line)
            _, linepos = lineltp.ltpTowords()
            lineword = jieba.lcut(line.strip())
            text_lengths.append(len(line.strip()))
            words_num.append(len(lineword))
            total_words += 1
            if not linepos:
                continue
            if 'nt' in linepos:
                time_count += 1
            if 'ns' in linepos:
                space_count += 1
        if total_words > 0:
            time_ratios.append(time_count / total_words)
            space_ratios.append(space_count / total_words)

    # 计算平均值和标准差
    time_mean = np.mean(time_ratios)
    space_mean = np.mean(space_ratios)
    text_mean = np.mean(text_lengths)
    words_mean = np.mean(words_num)
    time_std = np.std(time_ratios)
    time_var = np.var(time_ratios)
    space_std = np.std(space_ratios)
    space_var = np.var(space_ratios)

    # 计算置信区间
    confidence_level = 0.95
    z_value = stats.norm.ppf(1 - (1 - confidence_level) / 2)

    def compute_confidence_interval(data):
        sample_mean = np.mean(data)
        standard_error = np.std(data) / np.sqrt(len(data))
        margin_of_error = z_value * standard_error
        return sample_mean - margin_of_error, sample_mean + margin_of_error

    time_confidence_interval = compute_confidence_interval(time_ratios)
    space_confidence_interval = compute_confidence_interval(space_ratios)

    result = {
        "时间文本占比平均值": time_mean,
        "时间文本占比标准差": time_std,
        "时间文本占比方差": time_var,
        "时间文本占比置信区间": time_confidence_interval,
        "时间文本占比置信区间差": time_confidence_interval[1] - time_confidence_interval[0],
        "空间文本占比平均值": space_mean,
        "空间文本占比标准差": space_std,
        "空间文本占比方差": space_var,
        "空间文本占比置信区间": space_confidence_interval,
        "空间文本占比置信区间差": space_confidence_interval[1] - space_confidence_interval[0],
        "文本均长": text_mean,
        "分词均长": words_mean
    }
    return result


def read_files_in_subfolders(folder, target_file_name, result_folder_path):
    """读取子文件夹中的文件并进行处理----[10, 10], [500, 500],"""
    kmlist = [
        [1000, 500], [1000, 700], [1000, 900], [1000, 1100], [1000, 1300],
        [1000, 1500], [1000, 1700], [1000, 1900], [1000, 2100], [1000, 2300],
        [1000, 2400], [1000, 2600], [1000, 2800], [1000, 3000]
    ]
    for m, k in kmlist:
        print("处理：", k)
        try:
            with open(os.path.join(result_folder_path, f'GeoRelAnalyseBootstrap_new_{m}_{k}.json'), 'r',
                      encoding='utf-8') as file:
                geodict = json.load(file)
        except FileNotFoundError:
            geodict = {}
        geokeys = len(geodict.keys())
        folderlist = os.listdir(folder)
        print(folderlist)
        for item in tqdm(folderlist[geokeys:], desc=f"1.1 - 22 Tuple Processing (Bootstrap-{m}-{k}): ", total=22-geokeys, unit='folder', unit_scale=True):
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):
                target_file_path = os.path.join(item_path, target_file_name)
                if os.path.isfile(target_file_path):
                    result = process_file(target_file_path, m, k)
                    geodict[item] = result
                    with open(os.path.join(result_folder_path, f'GeoRelAnalyseBootstrap_new_{m}_{k}_.json'), 'w',
                              encoding='utf-8') as file:
                        json.dump(geodict, file, ensure_ascii=False, indent=4)
def sta_run():
    """主函数"""
    folder_path = config_loader.get_value('dataset','geo_path')
    result_folder_path = config_loader.get_value('resultpath', 'stc_bootstrapAnalyse_path')
    target_file_name = 'filtered_output_select.txt'
    read_files_in_subfolders(folder_path, target_file_name, result_folder_path)


if __name__ == "__main__":
    sta_run()
