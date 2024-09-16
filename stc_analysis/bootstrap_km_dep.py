import os
import json
import random
from scipy import stats
import numpy as np
from ctgucode.tools.Tool_Method import format_number
from tqdm import tqdm
from ctgucode.tools.SetGlobalVariables import config_loader, wordsynonymsPath, Special_words, Special_symbols


def jaccard_similarity(set1, set2):
    """计算两个集合的 Jaccard 相似度"""
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union


def find_best_match(tokens, keyword):
    """在分词列表中找到与关键词 Jaccard 相似度最高的词"""
    keyword_set = set(keyword)

    # 在 tokens 中寻找最相似的 token
    best_match, best_similarity = None, 0
    for token in tokens:
        token_set = set(token)
        similarity = jaccard_similarity(keyword_set, token_set)
        if similarity > best_similarity:
            best_similarity, best_match = similarity, token

    # 如果没有找到合适的匹配，则从 keysame 列表中重新寻找
    if best_match is None:
        with open(wordsynonymsPath, 'r', encoding='utf-8') as file:
            relation_same = json.load(file)

        same_keys = relation_same.get(keyword, [])
        for same_key in same_keys:
            same_key_set = set(same_key)
            for token in tokens:
                token_set = set(token)
                similarity = jaccard_similarity(same_key_set, token_set)
                if similarity > best_similarity:
                    best_similarity, best_match = similarity, token

    # 返回找到的匹配词及其索引，若未找到匹配则返回 None 和 -1
    return best_match, tokens.index(best_match) if best_match else -1


def extract_window_around_keyword_jaccard(tokenized_word, tokenized_pos, keyword, win):
    best_match, keyword_index = find_best_match(tokenized_word, keyword)    # 找到与关键词 Jaccard 相似度最高的词及其索引
    # 计算起始和结束索引
    if keyword_index == -1:
        start_index, end_index = 0, len(tokenized_word)-1
    else:
        start_index = max(0, keyword_index - win)
        end_index = min(len(tokenized_word)-1, keyword_index + win)
    window_tokens = tokenized_word[start_index:end_index]    # 截取窗口内的子字符串
    window_pos = tokenized_pos[start_index:end_index]
    return window_tokens,window_pos

def process_file(itemkey,file_path, word_file, pos_file, m, k):
    # 从源文件中读取原始文本
    with open(file_path, 'r', encoding='utf-8') as file:
        all_lines = [line.strip() for line in file if line.strip()]

    # 从 word.txt 和 pos.txt 文件中读取分词和词性数据
    with open(word_file, 'r', encoding='utf-8') as word_f:
        word_lines = [line.strip() for line in word_f if line.strip()]

    with open(pos_file, 'r', encoding='utf-8') as pos_f:
        pos_lines = [line.strip() for line in pos_f if line.strip()]

    # 断言 word.txt 和 pos.txt 文件的行数相匹配
    assert len(word_lines) == len(pos_lines), "word.txt 和 pos.txt 文件的行数不匹配"

    # 从分词和词性数据中进行随机抽取
    time_ratios, space_ratios = [], []
    text_lengths, words_num = [], []

    for _ in range(m):
        sample_indices = random.sample(range(len(word_lines)), k=min(k, len(word_lines)))
        time_count, space_count = 0, 0
        total_words = 0
        time_all_count, space_all_count = 0, 0

        for idx in sample_indices:
            lineword = word_lines[idx].split(' ')
            linepos = pos_lines[idx].split(' ')
            swordFalg = False
            max_window = len(lineword)
            slide_window = int(max_window/2)
            slide_window_start = int(max_window/8)

            original_text_length = len(all_lines[idx])  # 使用原始文本长度
            text_lengths.append(original_text_length)
            words_num.append(max_window)
            total_words += 1

            if len(linepos) != len(lineword):
                raise ValueError(f"分词与词性标注长度不匹配: {len(lineword)} vs {len(linepos)}")
            slide_words, slide_pos = extract_window_around_keyword_jaccard(lineword, linepos, itemkey, slide_window)
            if itemkey == Special_words:
                if 'nt' in linepos[:slide_window_start]:
                    time_count += 1
                elif 'nt' in slide_pos:
                    for sword in Special_symbols:
                        # print(sword, slide_words[slide_pos.index('nt')])
                        if sword in slide_words[slide_pos.index('nt')]:
                            swordFalg = True
                            break
                    if not swordFalg:
                        # print('加一','\n')
                        time_count += 1
            else:
                if 'nt' in linepos[:slide_window_start] or 'nt' in slide_pos:
                    time_count += 1
            if 'ns' in linepos[:slide_window_start] or 'ns' in slide_pos:
                space_count += 1
            if 'nt' in linepos:
                time_all_count += 1
            if 'ns' in linepos:
                space_all_count += 1
        # print(itemkey, time_all_count / total_words, space_all_count / total_words)
        if time_all_count / total_words >= 0.95:
            time_count = time_all_count
        if space_all_count / total_words >= 0.95:
            space_count = space_all_count

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
        "时间文本占比平均值": format_number(time_mean),
        "时间文本占比标准差": format_number(time_std),
        "时间文本占比方差": format_number(time_var),
        "时间文本占比置信区间": (format_number(time_confidence_interval[0]), format_number(time_confidence_interval[1])),
        "时间文本占比置信区间差": format_number(time_confidence_interval[1] - time_confidence_interval[0]),
        "空间文本占比平均值": format_number(space_mean),
        "空间文本占比标准差": format_number(space_std),
        "空间文本占比方差": format_number(space_var),
        "空间文本占比置信区间": (format_number(space_confidence_interval[0]), format_number(space_confidence_interval[1])),
        "空间文本占比置信区间差": format_number(space_confidence_interval[1] - space_confidence_interval[0]),
        "文本均长": format_number(text_mean),
        "分词均长": format_number(words_mean)
    }
    return result

# 自定义生成列表
# 自定义生成列表，fixed_value 循环为 500, 1000, 1500
def generate_kmlist(start, step, count, fixed_values):
    kmlist = []
    for i in range(count):
        fixed_value = fixed_values[i % len(fixed_values)]
        kmlist.append([fixed_value, start + i * step])
    return kmlist


def read_files_in_subfolders(folder, target_file_name,word_file_name,pos_file_name, result_folder_path,
                             start, step, count, fixed_values):
    """读取子文件夹中的文件并进行处理----[10, 10], [500, 500],"""

    # 使用函数生成列表
    kmlist = generate_kmlist(start, step, count,fixed_values)
    for m, k in kmlist:
        print(f"处理：{m}",m, k)
        # 如果文件夹不存在，则创建它
        result_folder_path_m = os.path.join(result_folder_path, str(m))
        if not os.path.exists(result_folder_path_m):
            os.makedirs(result_folder_path_m)
            print(f"文件夹 '{result_folder_path_m}' 已成功创建。")
        else:
            print(f"文件夹 '{result_folder_path_m}' 已经存在。")
        result_file_m_k = os.path.join(result_folder_path_m, f'GeoRelAnalyseBootstrap_new_dep_stop_{m}_{k}.json')
        try:
            with open(result_file_m_k, 'r', encoding='utf-8') as file:
                geodict = json.load(file)
        except FileNotFoundError:
            geodict = {}
        geokeys = len(geodict.keys())
        folderlist = [name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))]
        print(folderlist)
        for item in tqdm(folderlist[geokeys:], desc=f"1.1 - 22 Tuple Processing (Bootstrap-{m}-{k}): ", total=len(folderlist)-geokeys, unit='folder', unit_scale=True):
            if item == "__pycache__":
                continue
            item_path = os.path.join(folder, item)
            if os.path.isdir(item_path):
                target_path = os.path.join(item_path, target_file_name)
                word_path = os.path.join(item_path, word_file_name)
                pos_path = os.path.join(item_path, pos_file_name)
                if os.path.isfile(target_path) and os.path.isfile(word_path) and os.path.isfile(pos_path):
                    result = process_file(item,target_path,word_path,pos_path, m, k)
                    geodict[item] = result
                    with open(result_file_m_k, 'w', encoding='utf-8') as file:
                        json.dump(geodict, file, ensure_ascii=False, indent=4)
def sta_run(start, step, count, fixed_values):
    """主函数"""
    folder_path = config_loader.get_value('dataset','geo_path')
    result_folder_path = config_loader.get_value('resultpath', 'stc_bootstrapAnalyse_path')
    target_file_name = 'filtered_output_select.txt'
    word_file_name = 'word_tostop.txt'
    pos_file_name = 'pos_tostop.txt'
    read_files_in_subfolders(folder_path, target_file_name,word_file_name,pos_file_name, result_folder_path,
                             start, step, count, fixed_values)
#
#
# if __name__ == "__main__":
#     sta_run()
