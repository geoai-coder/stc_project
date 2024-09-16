"""
语义动态性
"""
import json
import os
from collections import defaultdict
import numpy as np
import torch
from tqdm import tqdm
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
from ctgucode.tools.SetGlobalVariables import config_loader,load_json

class DynamicSemanticAnalyzer:
    def __init__(self, bootresult,model_path, input_folder, output_folder,
                 dynfilename = 'DynSemantic.json', spo_filename='spo.json'):
        self.tokenizer = BertTokenizer.from_pretrained(model_path)
        self.model = BertModel.from_pretrained(model_path)
        self.model.eval()
        self.input_folder = input_folder
        self.spo_filename = spo_filename
        self.output_jsonfile = os.path.join(output_folder, dynfilename)
        self.output_json = dict()
        self.bootjson = load_json(bootresult)

    def divide_dimension(self, text_spo_dict, dimension):
        """
        按维度将数据分组
        :param text_spo_dict: 字典列表
        :param dimension: 维度：时间和空间
        :return: 每个维度下不同值的元组
        """
        grouped_data = defaultdict(list)
        for item in text_spo_dict:
            value = item[dimension]
            spo_value = item['spo']
            spo_text = f"{spo_value[0]}的{spo_value[1]}是{spo_value[2]}"
            cls_text = f'{spo_text} [TAIL] {spo_value[2]}'
            grouped_data[value].append(cls_text)
        return dict(grouped_data)

    def spo_vectorize(self, dimension_key, spo_list):
        """
        将对应维度下的某一实例的元组列表向量化
        :param dimension_key: 维度键
        :param spo_list: SPO列表
        :return: 向量化的嵌入列表
        """
        embedding_list = []
        for sentence in spo_list:
            tokens = self.tokenizer.tokenize(sentence)
            token_ids = self.tokenizer.convert_tokens_to_ids(tokens)
            input_ids = torch.tensor(token_ids).unsqueeze(0)  # 增加一个维度以适应模型输入格式
            with torch.no_grad():
                outputs = self.model(input_ids)
            sentence_embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            embedding_list.append(sentence_embeddings)
        return embedding_list

    def calculate_semantic_similarity(self, embedding1, embedding2):
        """
        计算两个嵌入向量之间的余弦相似度
        :param embedding1: 嵌入向量1
        :param embedding2: 嵌入向量2
        :return: 余弦相似度值
        """
        similarity = cosine_similarity([embedding1], [embedding2])
        return round(similarity[0, 0],4)

    def classify_semantics(self, vector_dict):
        """
        分类语义相似性
        :param vector_dict: 向量字典
        :return: 相似性矩阵
        """
        keys_list = list(vector_dict.keys())
        similarity_matrix_overall = []
        lenDim = len(keys_list)

        if lenDim == 1 and (None in keys_list or None not in keys_list):
            similarity_matrix_overall.append(0)
        elif lenDim == 2 and None in keys_list:
            similarity_matrix = []
            non_null_keys = [k for k in keys_list if k is not None]
            null_key_values = vector_dict[None]
            non_null_key_values = vector_dict[non_null_keys[0]]     #除了null的另一个时空维度
            for value1 in non_null_key_values:
                value1_sim_list = [self.calculate_semantic_similarity(value1, value2) for value2 in null_key_values]
                if 1 in value1_sim_list:
                    similarity_matrix.append(0)
                else:
                    similarity_matrix.append(1)
            similarity_matrix_overall.append(sum(similarity_matrix) / len(similarity_matrix))
        else:
            for key1, valuelist1 in vector_dict.items():
                if key1 is None:
                    continue
                similarity_matrix = []
                other_keys = [k for k in keys_list if k != key1]      #其他维度
                for value1 in valuelist1:
                    valuedimlist =[]
                    for key2 in other_keys:
                        valuelist2 = vector_dict[key2]      #该维度下的元组
                        value1_sim_list = [self.calculate_semantic_similarity(value1, value2) for value2 in valuelist2]
                        if 1 in value1_sim_list:
                            valuedimlist.append(0)
                        else:
                            valuedimlist.append(1)
                    similarity_matrix.append(sum(valuedimlist) / len(valuedimlist))
                similarity_matrix_overall.append(sum(similarity_matrix) / len(similarity_matrix))
        return similarity_matrix_overall

    def bootstrap_mean(self, data, num_samples=1000):
        """
        使用Bootstrap方法计算均值
        :param data: 原始数据列表
        :param num_samples: 生成的样本数量
        :return: Bootstrap均值的数组
        """
        n = len(data)
        bootstrap_means = np.empty(num_samples)

        for i in range(num_samples):
            # 有放回地抽取样本
            sample = np.random.choice(data, size=n, replace=True)
            # 计算样本的均值
            bootstrap_means[i] = self.truncated_mean(sample)

        return bootstrap_means

    def truncated_mean(self,data):
        """
        去掉最大值和最小值后计算剩余数据的平均值
        :param data: 原始数据列表
        :return: 修剪后的平均值
        """
        if len(data) <= 2:
            return sum(data)/len(data)
        sorted_data = np.sort(data)
        trimmed_data = sorted_data[1:-1]  # 去掉最大值和最小值
        return np.mean(trimmed_data)
    def process_files(self):
        """
        处理输入文件夹中的文件，计算动态语义相似度
        """
        folderlist = [name for name in os.listdir(self.input_folder) if os.path.isdir(os.path.join(self.input_folder, name))]
        for dimension in ['L', 'T']:
            for item in tqdm(folderlist, desc="Processing items"):
                if item == "__pycache__":
                    continue
                dyn_semantic = []
                if item not in self.output_json:
                    self.output_json[item] = {}
                item_path = os.path.join(self.input_folder, item)
                boot_T = self.bootjson.get(item)['时间文本占比平均值']
                boot_L = self.bootjson.get(item)['空间文本占比平均值']
                if dimension in "boot_T" and 1 == round(boot_T,1):
                    self.output_json[item][dimension] = 1.0
                    continue
                if dimension in "boot_L" and 1 == round(boot_L,1):
                    self.output_json[item][dimension] = 1.0
                    continue
                if os.path.isdir(item_path):
                    spo_json = os.path.join(item_path, self.spo_filename)
                    if os.path.isfile(spo_json):
                        try:
                            with open(spo_json, 'r', encoding='utf-8') as file:
                                json_data = json.load(file)
                        except Exception as e:
                            print(f"Error reading {spo_json}: {e}")
                            continue
                        for sub, text_spo in json_data.items():
                            vector_dict = {}
                            dimension_dict = self.divide_dimension(text_spo, dimension)
                            for dim_key, dim_values in dimension_dict.items():
                                vector_dict[dim_key] = self.spo_vectorize(dim_key, dim_values)
                            similarity_matrix = self.classify_semantics(vector_dict)
                            dynmeans = sum(similarity_matrix)/len(similarity_matrix)
                            dyn_semantic.append(dynmeans)
                try:
                    bootstrap_mean = self.bootstrap_mean(dyn_semantic)
                    dyn_semantic_value = self.truncated_mean(bootstrap_mean)
                except ZeroDivisionError:
                    continue
                self.output_json[item][dimension] = dyn_semantic_value

        with open(self.output_jsonfile, 'w', encoding='utf-8') as jsonfile:
            json.dump(self.output_json, jsonfile, ensure_ascii=False, indent=4)

# if __name__ == '__main__':
#     model_path = config_loader.get_value('modelpath','bert_path')
#     input_folder_path = config_loader.get_value('dataset','geo_path')
#     output_folder_path = config_loader.get_value('resultpath','stc_dynsemantic_path')
#     bootresultpath = config_loader.get_value('resultpath','stc_bootstrapAnalyse_path')
#     bootreultfile = 'GeoRelAnalyseBootstrap_new_10_10.json'
#     bootresult = os.path.join(bootresultpath,bootreultfile)
#     dynfilename = 'DynSemantic_new.json'
#     analyzer = DynamicSemanticAnalyzer(bootresult,model_path=model_path, input_folder=input_folder_path,
#                                        output_folder=output_folder_path, dynfilename = dynfilename,)
#     analyzer.process_files()
