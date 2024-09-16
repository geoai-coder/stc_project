from ltp import LTP
import json

from ctgucode.tools.config_loader import ConfigLoader
import csv

try:
    config_loader = ConfigLoader('../static/config.json')
except FileNotFoundError:
    try:
        config_loader = ConfigLoader('static/config.json')
    except FileNotFoundError:
        config_loader = ConfigLoader(r'F:\4-2022-2025\论文and实验\Li1_2023.12\ctgucode\static\config.json')

stoppath = config_loader.get_value("static","stop_path")
lexiconpath = config_loader.get_value("static","lexicon_path")
ltpPath = config_loader.get_value('modelpath', 'ltp_path')              #FOLDER: ltp\base
spotypePath = config_loader.get_value('static','spotype_path')          #FILE: spoType.csv
wordsynonymsPath = config_loader.get_value('static','relation_synonyms_path')          #FILE: spoType.csv
wordsynonyms_reversePath = config_loader.get_value('static','relation_synonyms_reverse_path')          #FILE: spoType.csv
allgeofilePath = config_loader.get_value('dataset','geo_path')          #FOLDER: add_Text
gptfilePath = config_loader.get_value('dataset','gpt_path')             #FOLDER: GptDatas
stcschemaPath = config_loader.get_value('static','stc_schema_path')     #FILE: spotype_STC.json
gptloggerPath = config_loader.get_value('loggerpath','logger_path')     #FOLDER: logger
pmresultPath = config_loader.get_value('resultpath','pattern_matching_path')    #FOLDER: results_pm

#停用词
stoplist = [stop.strip() for stop in open(stoppath,'r',encoding='utf-8').readlines()]

#自定义词典
lexiconlist = [lex.strip() for lex in open(lexiconpath,'r',encoding='utf-8').readlines()]

Special_words = '经纬度'
Special_symbols = ['度','°']

#获取元组类型
def getspoType():
    mapping,spolist = {},[]    # 创建一个字典来存储映射关系
    with open(spotypePath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            chinese_type, english_type = row['元组类型(中文)'], row['元组类型(英文)']            # 提取中文和英文元组类型
            chinese_tuple, english_tuple = chinese_type.strip("()").split(", "), \
                                           english_type.strip("()").split(", ")            # 提取元组中的关系
            relationship = chinese_tuple[1]            # 获取关系名
            mapping[relationship] = {            # 构建字典
                'english': english_tuple[1],
                'spo_chinese': chinese_type,
                'spo_english': english_type
            }
            spolist.append(chinese_type)
    return mapping,spolist
RelLabel, spoType = getspoType()

def load_json(file_path: str) -> dict:
    """从 JSON 文件中加载数据"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


ltp_instance = LTP(ltpPath)  # 类属性，存储LTP实例

