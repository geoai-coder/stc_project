import csv
import json
import os

from tqdm import tqdm

# from Ctgu.Tools.LTP_ import LTP_


def write_logger_nt_ns(filter_predicates):
    data = {}
    for item in tqdm(filter_predicates):
        # 构建完整路径
        data[f'{item}'] = {"时间": 0, "空间": 0, "文件行数": 0,'时间比值':0.0, '空间比值':0.0}
    with open('dbpediaAnalyse/GeoRelDBpedia_nsnt.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def write_logger(filter_predicates):
    data = {}
    for item in tqdm(filter_predicates):
        # 构建完整路径
        data[f'{item}'] = {"文件行数": 0}
    with open('dbpediaAnalyse/GeoRelDBpedia.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_filter_predicates(csv_file_path):
    """
    读取CSV文件的第一列作为筛选条件（谓词列表）

    :param csv_file_path: CSV文件路径
    :return: 谓词列表
    """
    filter_predicates = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # 跳过表头
        for row in csv_reader:
            if row:  # 确保行不为空
                filter_predicates.append(row[0])
    return filter_predicates


def process_triples_ns_nt(input_file_path, output_folder_path, filter_predicates):
    """
    读取输入文件中的三元组，并根据筛选条件将其写入相应的CSV文件

    :param input_file_path: 输入文件路径
    :param output_folder_path: 输出文件夹路径
    :param filter_predicates: 谓词列表（筛选条件）
    """
    os.makedirs(output_folder_path, exist_ok=True)  # 如果输出文件夹不存在，则创建它
    i = 0
    with open('dbpediaAnalyse/GeoRelDBpedia.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            i+=1
            parts = line.strip().split('\t')
            if len(parts) == 3:
                subject, predicate, obj = parts
                if predicate in filter_predicates:
                    predicatejson = data[f'{predicate}']
                    ntnum, nsnum, linelen = predicatejson['时间'], predicatejson['空间'], predicatejson['文件行数']
                    text = f'{subject}的{predicate}为{obj}'
                    output_file_path = os.path.join(output_folder_path, f'{predicate}.csv')
                    file_exists = os.path.isfile(output_file_path)
                    with open(output_file_path, 'a', newline='', encoding='utf-8') as csv_file:
                        csv_writer = csv.writer(csv_file)
                        if not file_exists:
                            csv_writer.writerow(['subject', 'predicate', 'object'])
                        csv_writer.writerow([subject, predicate, obj])

                    textltp = LTP_(text)
                    try:
                        word, pos = textltp.ltpTowords()
                        linelen += 1
                        if 'nt' in pos:
                            ntnum += 1
                        if 'ns' in pos:
                            nsnum += 1
                        predicatejson['时间'], predicatejson['空间'], predicatejson['文件行数'] = ntnum, nsnum, linelen
                        with open('dbpediaAnalyse/GeoRelDBpedia.json', 'w', encoding='utf-8') as file:
                            json.dump(data, file, ensure_ascii=False, indent=4)
                    except:
                        continue

            print(f'第{i}行')

def process_triples(input_file_path, output_folder_path, filter_predicates):
    """
    读取输入文件中的三元组，并根据筛选条件将其写入相应的CSV文件

    :param input_file_path: 输入文件路径
    :param output_folder_path: 输出文件夹路径
    :param filter_predicates: 谓词列表（筛选条件）
    """
    os.makedirs(output_folder_path, exist_ok=True)  # 如果输出文件夹不存在，则创建它
    i = 0
    with open('dbpediaAnalyse/GeoRelDBpedia.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            i+=1
            if i > 1795450:
                parts = line.strip().split('\t')
                if len(parts) == 3:
                    subject, predicate, obj = parts
                    if predicate in filter_predicates:
                        predicatejson = data[f'{predicate}']
                        linelen = predicatejson['文件行数']
                        output_file_path = os.path.join(output_folder_path, f'{predicate}.csv')
                        output_txt_path = os.path.join(output_folder_path, f'{predicate}_sub.txt')
                        file_exists = os.path.isfile(output_file_path)
                        with open(output_file_path, 'a', newline='', encoding='utf-8') as csv_file ,open(output_txt_path,'a',encoding='utf-8') as txtfile:
                            csv_writer = csv.writer(csv_file)
                            txtfile.write(subject+'\n')
                            if not file_exists:
                                csv_writer.writerow(['subject', 'predicate', 'object'])
                            csv_writer.writerow([subject, predicate, obj])
                            predicatejson['文件行数'] = linelen
                            with open('dbpediaAnalyse/GeoRelDBpedia.json', 'w', encoding='utf-8') as file:
                                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f'第{i}行')



def main():
    filter_predicate_file = 'RelSelect/cnDBpedia_relation_select22.csv'
    input_file_path = '../EncyclopediaData/DBpedia/baike_triples.txt'
    output_folder_path = 'reldatafile/add_Triples_dbpedia'
    filter_predicates = load_filter_predicates(filter_predicate_file)
    print(f"Loaded {len(filter_predicates)} predicates:", filter_predicates)
    write_logger(filter_predicates)
    # process_triples_ns_nt(input_file_path, output_folder_path, filter_predicates)
    process_triples(input_file_path, output_folder_path, filter_predicates)
    print(f"Filtered triples have been written to CSV files in {output_folder_path}")


if __name__ == '__main__':
    main()
