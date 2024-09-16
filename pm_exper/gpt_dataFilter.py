#用于ChatGPT实验的数据
import json
import os
import random
from tqdm import tqdm
import jieba
from ctgucode.tools.SetGlobalVariables import RelLabel, allgeofilePath,gptfilePath, stcschemaPath


# 读取第二个文件，获取元组类型及其STC值
def load_stc_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def split_data(itemdatas, train_ratio=0.2):
    """将数据集拆分为训练集和测试集"""
    train_size = max(1, int(len(itemdatas) * train_ratio))
    random.shuffle(itemdatas)
    traindata = itemdatas[:train_size]
    testdata = itemdatas[train_size:]
    return traindata, testdata

def analyze_data(datalist):
    """分析数据集"""
    num_elements = len(datalist)
    words_num,textlenlist = [],[]
    for item in datalist:
        text = item["text"]
        lineword = jieba.lcut(text.strip())
        words_num.append(len(lineword))
        textlenlist.append(len(text))
    avg_length = sum(textlenlist) / num_elements if num_elements > 0 else 0
    vocab_size = sum(words_num) / num_elements if num_elements > 0 else 0
    return {
        "num_elements": num_elements,
        "avg_length": round(avg_length,2),
        "vocab_size": round(vocab_size,2)
    }

def process_folder(input_folder, stc_schemaPath, spo_filename='spo_2.json', train_ratio=0.2):
    """处理文件夹中的所有数据"""
    testdatalist = []
    traindatalist = []
    stc_schema = load_stc_file(stc_schemaPath)
    # 定义 key 映射
    for item in tqdm(os.listdir(input_folder),desc='Split the GPTdataset: '):
        itemdatas = []
        item_path = os.path.join(input_folder, item)
        spo_json = os.path.join(item_path, spo_filename)
        mapped_key = RelLabel.get(item, {}).get("spo_chinese")
        if not os.path.exists(spo_json):
            continue
        json_data = load_stc_file(spo_json)
        for keys, valuelist in json_data.items():
            for value in valuelist:
                value['spoType'] = mapped_key
                spo,spo_type = value.get('spo', []), value.get('spoType', [])
                L, T = value.get('L', ''), value.get('T', '')
                stc_info = stc_schema.get(spo_type, {})
                stc_t, stc_s = stc_info.get('STC_T', ''), stc_info.get('STC_S', '')
                value['STC'] = stc_info

                # 根据STC_T和STC_S确定flag和初始st_tuple
                flag_t = {'Strong': 0, 'Medium': 1}.get(stc_t, -1)
                st_tuple = f'({spo[0]}, {spo[1]}, {spo[2]}'

                # 添加时间信息
                if flag_t == 0:
                    st_tuple += f', {T}'
                elif flag_t == 1:
                    st_tuple += f'), {{{T}'
                # 添加空间信息
                if stc_s == 'Strong':
                    if flag_t in [0, -1]:
                        st_tuple += f', {L})'
                    else:  # flag_t == 1
                        st_tuple = f'({spo[0]}, {spo[1]}, {spo[2]}, {L}), {{{T}}}'
                elif stc_s == 'Medium':
                    if flag_t == 1:
                        st_tuple += f', {L}}}'
                    else:
                        st_tuple += f'), {{{L}}}'
                else:
                    st_tuple += f')' if flag_t != 1 else '})'
                # 添加完成的st_tuple到value中

                value['STTuple'] = st_tuple
                itemdatas.append(value)

        traindata, testdata = split_data(itemdatas, train_ratio)
        testdatalist += testdata
        traindatalist += traindata

    testdata_stats = analyze_data(testdatalist)
    traindata_stats = analyze_data(traindatalist)

    return testdatalist, traindatalist, {
        "testdata_stats": testdata_stats,
        "traindata_stats": traindata_stats
    }

def write_data_to_txt(data, filename):
    """将数据写入txt文件，每行一个字典"""
    with open(filename, 'w', encoding='utf-8') as file:
        for item in data:
            json.dump(item, file, ensure_ascii=False)
            file.write('\n')

def gpt_dataFilter_run(data_stats, traindata, testdata):
    input_folder = allgeofilePath

    output_json = os.path.join(gptfilePath, data_stats)
    output_train_txt = os.path.join(gptfilePath, traindata)
    output_test_txt = os.path.join(gptfilePath, testdata)

    testdatalist, traindatalist, results = process_folder(input_folder,stcschemaPath)

    with open(output_json, 'w', encoding='utf-8') as outfile:
        json.dump(results, outfile, ensure_ascii=False, indent=4)

    write_data_to_txt(traindatalist, output_train_txt)
    write_data_to_txt(testdatalist, output_test_txt)

    print("测试数据统计:", results["testdata_stats"])
    print("训练数据统计:", results["traindata_stats"])

