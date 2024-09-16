import os
import json
from tqdm import tqdm
import jieba
from ctgucode.tools.SetGlobalVariables import config_loader

def load_config():
    return {
        'folder_path': config_loader.get_value('dataset', 'geo_path'),
        'target_file_name': 'filtered_output_select.txt',
        'output_file': os.path.join(config_loader.get_value('resultpath', 'stc_allanalysis_path'), 'AllDataAnalysis.json')
    }

def analyze_files(config):
    folder_path = config['folder_path']
    target_file_name = config['target_file_name']
    output_file = config['output_file']

    geodict = {}
    all_text_lengths = []
    all_word_lengths = []
    relationship_data_counts = []
    relationlist = []
    relationlist_maxtext, relationlist_mintext = [], []
    greater_than_avg, less_than_avg = 0, 0
    greater_than_avg_half, less_than_avg_half = 0, 0
    greater_elements, lesser_elements = [], []
    greater_elements_half, lesser_elements_half = [], []
    count_greater_than_1000, count_less_than_50 = [], []  # 初始化计数器
    folderlist = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]

    for item in tqdm(folderlist, desc="0 - Analyzing text files: "):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            target_file_path = os.path.join(item_path, target_file_name)
            if os.path.isfile(target_file_path):
                process_file(target_file_path, item, geodict, all_text_lengths, all_word_lengths, relationship_data_counts, relationlist, relationlist_maxtext, relationlist_mintext, count_greater_than_1000, count_less_than_50)
            else:
                print(f"{target_file_path} does not exist.")
        else:
            print(f"{item_path} is a file, not a directory.")

    calculate_summary(geodict, all_text_lengths, all_word_lengths, relationship_data_counts, relationlist, relationlist_maxtext, relationlist_mintext, greater_than_avg, less_than_avg, greater_than_avg_half, less_than_avg_half, greater_elements, lesser_elements, greater_elements_half, lesser_elements_half, count_greater_than_1000, count_less_than_50)
    save_results(geodict, output_file)

def process_file(file_path, item, geodict, all_text_lengths, all_word_lengths, relationship_data_counts, relationlist, relationlist_maxtext, relationlist_mintext, count_greater_than_1000, count_less_than_50):
    text_lengths, words_num = [], []
    relationlist.append(item)
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                line_length = len(line.strip())
                lineword = jieba.lcut(line.strip())
                text_lengths.append(line_length)
                words_num.append(len(lineword))

                # 判断文本长度
                if line_length > 500:
                    count_greater_than_1000.append(1)
                elif line_length < 20:
                    count_less_than_50.append(1)

            except Exception as e:
                print("分词出错:", e)

    if text_lengths:
        total_texts = len(text_lengths)
        max_text = max(text_lengths)
        min_text = min(text_lengths)
        average_length = sum(text_lengths) / total_texts
        average_wordnum = sum(words_num) / total_texts

        all_text_lengths.extend(text_lengths)
        all_word_lengths.extend(words_num)
        relationship_data_counts.append(total_texts)
    else:
        total_texts = max_text = min_text = average_length = average_wordnum = 0

    relationlist_maxtext.append(max_text)
    relationlist_mintext.append(min_text)
    geodict[item] = {
        "文本数量": total_texts,
        "最长文本长度": max_text,
        "最短文本长度": min_text,
        "平均文本长度": average_length,
        "平均分词长度": average_wordnum
    }

def calculate_summary(geodict, all_text_lengths, all_word_lengths, relationship_data_counts, relationlist, relationlist_maxtext, relationlist_mintext, greater_than_avg, less_than_avg, greater_than_avg_half, less_than_avg_half, greater_elements, lesser_elements, greater_elements_half, lesser_elements_half, count_greater_than_1000, count_less_than_50):
    total_texts = len(all_text_lengths)
    if total_texts > 0:
        max_text_length = max(all_text_lengths)
        min_text_length = min(all_text_lengths)
        avg_text_length = sum(all_text_lengths) / total_texts
        max_word_length = max(all_word_lengths)
        min_word_length = min(all_word_lengths)
        avg_word_length = sum(all_word_lengths) / total_texts
        avg_relmax_length = sum(relationlist_maxtext) / len(relationlist_maxtext)
        avg_relmin_length = sum(relationlist_mintext) / len(relationlist_mintext)
    else:
        max_text_length = min_text_length = avg_text_length = max_word_length = min_word_length = avg_word_length = avg_relmax_length = avg_relmin_length = 0

    if relationship_data_counts:
        max_data_count = max(relationship_data_counts)
        min_data_count = min(relationship_data_counts)
        avg_data_count = sum(relationship_data_counts) / len(relationship_data_counts)
    else:
        max_data_count = min_data_count = avg_data_count = 0

    for idx, count in enumerate(relationship_data_counts):
        if count > avg_data_count:
            greater_than_avg += 1
            greater_elements.append(relationlist[idx])
        elif count < avg_data_count:
            less_than_avg += 1
            lesser_elements.append(relationlist[idx])

    for idx, count in enumerate(relationship_data_counts):
        if count > (avg_data_count / 2):
            greater_than_avg_half += 1
            greater_elements_half.append(relationlist[idx])
        else:
            less_than_avg_half += 1
            lesser_elements_half.append(relationlist[idx])

    geodict["汇总"] = {
        "总文本数量": total_texts,
        "文本长度大于500的数量": len(count_greater_than_1000),  # 汇总大于1000的文本数量
        "文本长度小于20的数量": len(count_less_than_50),  # 汇总小于50的文本数量ngth,
        "最长文本长度": max_text_length,
        "最短文本长度": min_text_length,
        "每个关系的平均最长文本长度": avg_relmax_length,
        "每个关系的平均最短文本长度": avg_relmin_length,
        "平均文本长度": round(avg_text_length, 2),
        "最长分词长度": max_word_length,
        "最短分词长度": min_word_length,
        "平均分词长度": round(avg_word_length, 2),
        "每类关系最大数据集数量": max_data_count,
        "每类关系最小数据集数量": min_data_count,
        "每类关系平均数据集数量": round(avg_data_count, 2),
        "大于平均数据集数量": round(greater_than_avg, 2),
        "大于平均数据集数量的关系": greater_elements,
        "小于平均数据集数量": round(less_than_avg, 2),
        "小于平均数据集数量的关系": lesser_elements,
        "大于平均数据集数量一半": round(greater_than_avg_half, 2),
        "大于平均数据集数量一半的关系": greater_elements_half,
        "小于平均数据集数量一半": round(less_than_avg_half, 2),
        "小于平均数据集数量一半的关系": lesser_elements_half
    }

def save_results(geodict, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(geodict, json_file, ensure_ascii=False, indent=4)
    print(f"结果已写入 {output_file}")
    print(geodict)

def all_data_analysis_run():
    config = load_config()      #加载参数
    analyze_files(config)

# 主程序入口
if __name__ == "__main__":
    all_data_analysis_run()
