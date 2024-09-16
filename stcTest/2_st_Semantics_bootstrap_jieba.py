# 时空信息依赖特征统计结果
import os
import json
import random
from scipy import stats
import numpy as np
from tqdm import tqdm, trange
import jieba.posseg as pseg

folder_path = 'reldatafile/add_Text_dbpedia'
target_file_name = 'filtered_output_select2.txt'

def process_file(file_path,m,k):
    print(f'正在统计文件{file_path}')
    all_lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line != '\n':
                all_lines.append(line.strip())

    time_ratios, space_ratios = [],[]
    text_lengths, words_num = [], []

    for _ in trange(m):
        sample_lines = random.choices(all_lines, k=min(k, len(all_lines)))
        time_count, space_count = 0, 0
        total_words = 0
        for line in sample_lines:
            # 使用结巴进行分词和词性标注
            words_and_parts = pseg.cut(line.strip())
            # 使用列表推导式分别提取分词和词性
            words, pos = zip(*[(word, flag) for word, flag in words_and_parts])
            # 如果需要将它们转换回列表
            linepos,lineword = list(pos), list(words)
            text_lengths.append(len(line.strip()))
            words_num.append(len(lineword))
            total_words += 1
            if 't' in linepos:
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
        "空间文本占比置信区间差": space_confidence_interval[1]-space_confidence_interval[0],
        "文本均长": text_mean,
        "分词均长": words_mean
    }
    return result

def read_files_in_subfolders(folder, target_file_name):
    k_m = [
        [500, 500],
        [1000, 500],
        [1500, 500],
        [2000, 500],
        [2500, 500],
        [3000, 500],
        [3500, 500],
    ]
    # k_m = [
    #     [5, 5],
    #     [10, 5],
    #     [15, 5],
    #     [20, 5],
    #     [25, 5],
    #     [30, 5],
    #     [35, 5],
    # ]
    for m,k in k_m:
        try:
            with open(f'bootstrapAnalyse_jieba/GeoRelAnalyseBootstrap_{m}_{k}.json', 'r', encoding='utf-8') as file:
                geodict = json.load(file)
        except FileNotFoundError:
            # 如果文件不存在，则创建一个空字典
            geodict = {}

        for item in tqdm(os.listdir(folder)):  # 跳过前3、6个文件
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):
                target_file_path = os.path.join(item_path, target_file_name)
                if os.path.isfile(target_file_path):
                    result = process_file(target_file_path,m,k)
                    geodict[item_path.replace(r'reldatafile/add_Text_dbpedia\\','')] = result

                    # 每次处理完一个文件后将结果写入JSON文件
                    with open(f'bootstrapAnalyse_jieba/GeoRelAnalyseBootstrap_{m}_{k}.json', 'w', encoding='utf-8') as file:
                        json.dump(geodict, file, ensure_ascii=False, indent=4)


# 调用函数以读取指定文件夹下的所有子文件夹及其中的文件
read_files_in_subfolders(folder_path, target_file_name)
