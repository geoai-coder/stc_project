from typing import List
import os.path
import random
import re
import ast
import time
import openai
import json
from sklearn.metrics import precision_recall_fscore_support    #用于关联度评估，多分类评估；用于表达模型相同与不同的二分类（同：1，不同：0）
import logging
from tqdm import tqdm
from ctgucode.tools.SetGlobalVariables import gptfilePath,gptloggerPath, stcschemaPath, pmresultPath, wordsynonyms_reversePath,wordsynonymsPath
import random
from ctgucode.tools.Tool_Method import read_json, write_json

class KnowledgeModel:
    def __init__(self, api_key,model,loggertxt, stcPath = stcschemaPath):
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.loggertxt = loggertxt
        self.relation_same,self.relation_same_rev = self.get_synonyms()
        self.STC, self.spoType = self.get_keys_from_json(stcPath)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_synonyms(self):
        # 假设你的 JSON 文件名为 'data.json'
        with open(wordsynonymsPath, 'r', encoding='utf-8') as file:
            Reltion_same = json.load(file)
        with open(wordsynonyms_reversePath, 'r', encoding='utf-8') as file:
            Reltion_same_rev = json.load(file)
        return Reltion_same,Reltion_same_rev

    def get_chat_messages(self, prompt_text, max_tokens=2000, temperature=0.5):
        """调用ChatGPT生成对话回复"""
        openai.api_base = "https://ai-yyds.com/v1"  #
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=prompt_text,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def get_keys_from_json(self, file_path):
        """读取JSON文件并返回键列表"""
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data,list(data.keys())

    def read_data_from_file(self, file_path):
        """从文件中读取数据"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                data.append(json.loads(line.strip()))
        return data

    def precision_recall_f1(self, predictions: List[str], labels: List[str]):
        # 将 predictions 和 labels 转换为集合，便于计算交集
        predictions_set = set(predictions)
        labels_set = set(labels)

        # 计算真阳性 (True Positives)
        true_positives = predictions_set.intersection(labels_set)

        # Precision: 真阳性 / 预测为正的总数
        precision = len(true_positives) / len(predictions_set) if predictions_set else 0

        # Recall: 真阳性 / 实际为正的总数
        recall = len(true_positives) / len(labels_set) if labels_set else 0

        # F1 score: Precision 和 Recall 的调和平均数
        if precision + recall == 0:
            f1_score = 0
        else:
            f1_score = 2 * (precision * recall) / (precision + recall)

        return precision, recall, f1_score

    def _evaluate_sklearn(self, pattern, results):
        """
        辅助函数，用于评估结果
        参数:
        pattern (str): 评估模式（如"zero_shot", "few_shot"）
        results (tuple): 包含预测和真实标签的元组

        返回:
        list: 评估结果列表
        """
        precision, recall, f1 = self.precision_recall_f1(results[0], results[1])  # 不支持多类别多输出的情况，将其转为字符串
        return [pattern, precision, recall, f1, results[0], results[1]]

    def perform_zero_shot_test(self, test_data):
        """零样本测试"""
        result_stc, result_sttuple = self._make_predictions(test_data)
        evaluate_stc = self._evaluate_sklearn("zero_shot", result_stc)
        evaluate_sttuple = self._evaluate_sklearn("zero_shot", result_sttuple)
        return evaluate_stc, evaluate_sttuple

    def perform_few_shot_test(self, train_data, test_data, lenfew=None):
        """少样本测试"""
        result_stc, result_sttuple = self._make_predictions(test_data, status='few_shot', traindata=train_data, lenfew = lenfew)
        evaluate_stc = self._evaluate_sklearn(f"few_shot-{lenfew}", result_stc)
        evaluate_sttuple = self._evaluate_sklearn(f"few_shot-{lenfew}", result_sttuple)
        return evaluate_stc, evaluate_sttuple

    def Pattern_matching(self, spo_list, spo_type_list):
        spolist, spoTypelist, spotypeSTClist = [], [], []
        for spo, spotype in zip(spo_list, spo_type_list):
            spotype = '(' + spotype + ')'
            if spotype in self.spoType:
                spotypeSTClist.append(self.STC[spotype])
                spolist.append(spo)
                spoTypelist.append(spotype)
            else:
                continue
        return spolist, spoTypelist, spotypeSTClist

    def _make_predictions(self, data, status="zero_shot",traindata=None, lenfew=None):
        """生成预测"""
        def parse_response(response):
            def clean_response_string(response):                # 使用正则表达式匹配冒号前的无关字符
                cleaned_response = re.sub(r'\s*[\*\-\s]+(?=\S*:\s*)', '', response)
                return cleaned_response
            def clean_quotes(text):                # 去掉每个字符串前后的引号
                return text.strip("'\"‘’“”")
            spo_list, spoType_list, spoTypeSTC_list, T_list, S_list = [], [], [], [], []            # 初始化空列表
            patterns = {            # 使用正则表达式提取 spo, spoType, spoTypeSTC 和 T
                'spo': re.compile(r'spo\d*:\s*[\(\[]([^,\]\)]+),\s*([^,\]\)]+),\s*([^\)\]]+)[\)\]]'),
                'spoType': re.compile(r'spoType\d*:\s*[\(\[]([^,\]\)]+),\s*([^,\]\)]+),\s*([^\)\]]+)[\)\]]'),
                'spoTypeSTC': re.compile(r'spoTypeSTC\d*:\s*\{([^}]*?)\}'),  # 捕获大括号中的内容
                'T': re.compile(r'T\d*:\s*([^;,. \n]+(?:\s+[^;,.。 \n]+)*)'),
                'S': re.compile(r'L\d*:\s*([^;,. \n]+(?:\s+[^;,.。 \n]+)*)')
            }
            lines = response.split('\n')            # 按行拆分响应字符串
            for line in lines:            # 逐行匹配
                clean_line = clean_response_string(line)
                for key, pattern in patterns.items():
                    match = pattern.search(clean_line)
                    if match:
                        if key == 'spo' or key == 'spoType':
                            result = ', '.join(clean_quotes(group) for group in match.groups())      # 合并元组中的元素，清楚其他元组
                        elif key == 'spoTypeSTC':                            # 处理字典格式的内容
                            result = ', '.join(f"{kv.split(':')[0].strip()}: {kv.split(':')[1].strip()}"
                                               for kv in match.group(1).split(','))
                        else:                            # 对 T 和 S 直接添加
                            result = match.group(1).strip()
                        locals()[f'{key}_list'].append(result)
            return spo_list, spoType_list, spoTypeSTC_list, T_list, S_list

        def get_sample_prompts(few_shot_1, few_shot_2, traindata, dataspo, lenfew):
            target_value = dataspo[1]                # 提取 dataspo[1] 作为目标值
            filtered_data = [entry for entry in traindata if entry['spo'][1] == target_value]                # 筛选出 spo 列表中第二个元素为 target_value 的数据
            sample_size = min(len(filtered_data), lenfew)                # 计算样本数量，最小值为 len(filtered_data) 和 4 之间的较小者
            sample_prompts = random.sample(filtered_data, sample_size)                # 随机选择 sample_size 个样本
            # 打印或处理选中的数据
            few_shot_1 += '以下是文本中实体关系三元组及其类型的示例:\n'
            few_shot_2 += '以下是文本中元组的时空关联及其时空信息示例:\n'
            for i, prompt in enumerate(sample_prompts):
                few_shot_1 += f'{i}. 文本“{prompt["text"]}”抽取得到:spo: {prompt["spo"]}; spoType: {prompt["spoType"]};\n'
                few_shot_2 += f'{i}. 文本“{prompt["text"]}”抽取得到:spo: {prompt["spo"]}; spoType: {prompt["spoType"]}; spoTypeSTC: {prompt["STC"]}; T: {prompt["T"]}; L: {prompt["L"]};\n'
            return few_shot_1, few_shot_2

        tuple_predictions, tuple_true_labels = [], []
        STC_predictions, STC_true_labels = [], []
        for i,sample in tqdm(enumerate(data)):
            datatext, dataspo, dataSTTuple, dataSTC, data_T, data_L = sample["text"], sample["spo"], sample["STTuple"], sample["STC"], sample["T"], sample["L"]
            sub_true_labels, rel_true_labels, obj_true_labels = dataspo
            dataspo_str = sub_true_labels + ', ' + rel_true_labels + ', ' + obj_true_labels
            few_shot_1, few_shot_2 = '', ''
            if status == 'few_shot':
                few_shot_1, few_shot_2 = get_sample_prompts(few_shot_1, few_shot_2,traindata, dataspo, lenfew)     #少样本
                            # 步骤1：确定元组类型
            prompt1 = f"现在我有一个实体关系三元组类型表 spoTypeTable: {self.spoType}\n" \
                      f"{few_shot_1}" \
                      f"spo 是一种用来表示知识的数据结构，通常用 (S, P, O) 表示，其中 S 和 O 是实体对象，P 表示它们之间的关系，例如 (中国, 首都, 北京)。\n" \
                      f"spoType 指三元组中元素所属的类别或概念。例如，(中国, 首都, 北京) 的类型是 (国家, 首都, 城市)。\n" \
                      f"请你判断文本“{datatext}”中包含spoTypeTable表中哪些元组类型，并从中抽取出对应的实体关系三元组。严格按照格式输出："
            assistant1 = "\t1. spo: (上海, GDP总计, 20101.33亿元); spoType: (地点, GDP总计, 数值)\n" \
                         "\t2. spo: ...; spoType: ...\n" \
                         "\t3. ..."
            step1_prompt = [
                {"role": "system", "content": "你是实体关系三元组抽取和实体关系三元组类型匹配方面的专家。"},
                {"role": "user", "content": prompt1},
                {"role": "assistant", "content": assistant1}
            ]
            step1_response = self.get_chat_messages(step1_prompt)
            if 'spo' not in step1_response and "spoType" not in step1_response:
                continue

            # # 步骤2：匹配时空关联度
            spo_list1, spo_type_list1,_,_,_ = parse_response(step1_response)
            # 使用 any() 检查 spotype_1 是否在 spotype 中  -  使用 any() 检查 spo_type_1[1] 是否是字典的键
            # if not any(spo_type_1[1] in self.relation_same_rev for spo_type_1 in spo_type_list1) and\
            #         not any(spotype_1 in spotype for spotype in self.spoType for spotype_1 in spo_type_list1):
            #     continue

            spolist1, spoTypelist1, spotypeSTClist1 = self.Pattern_matching(spo_list1, spo_type_list1)
            if len(spolist1) == 0:
                # 只选取 spo 为 "str" 的字符串
                filtered_list = [(spo, spo_type, spo_stc) for (spo, spo_type, spo_stc) in zip(spolist1, spoTypelist1, spotypeSTClist1) if spo in dataspo_str]
                combined_string = "\n".join(
                    f"{i + 1}. spo: {spo}, spoType: {spo_type}, spoTypeSTC: {spo_stc}" for i, (spo, spo_type, spo_stc)
                    in enumerate(filtered_list)
                )
                response1 = f"因此我们对上述抽取结果，进行时空关联度模式匹配，结果如下:\n" \
                            f"{combined_string}\n\t"
            else:
                response1 = f"然后对上述抽取结果:\n" \
                            f"{step1_response}\n" \
                            f"进行时空关联度模式匹配，其中时空关联度模式如下STC:\n\t {self.STC}\n\t"

            # 步骤3：构建时空知识表达模型
            prompt2 = (
                f"首先，定义时空关联度指知识（元组）与时间和空间信息的紧密程度，分为三种：Weak、Medium和Strong。\n"
                f"{response1}"
                f"其中，spo表示文本中抽取的三元组；spoType表示三元组的元组类型；spoTypeSTC表示元组类型对应的时空关联度（STC_T表示时间关联度，STC_S表示空间关联度）。\n"
                f"1. 若关联度为Strong或Medium，则抽取相关时间或空间信息；\n"
                f"2. 若关联度为Weak，则不抽取时间或空间信息；\n"
                f"注意：若未抽取到时间或空间信息，则以None代替。\n"
                f"{few_shot_2}"
                f"现在需要你根据文本”{datatext}“中抽取的spo及其spoTypeSTC匹配结果，进行相应时空信息的抽取（T表示时间，L表示空间）并严格按照格式输出。"
            )
            assistant2 = (
                "\t1. spo: (上海, GDP总计, 20101.33亿元); spoType: (地点, GDP总计, 数值); spoTypeSTC: {'STC_T': 'Strong', 'STC_S': 'Strong'}; T: 2012年; L: 上海\n"
                "\t2. spo: ...; spoType: ...; spoTypeSTC: ...; T: ...; L: ...\n"
                "\t3. ..."
            )
            step2_prompt = [
                {"role": "system", "content": "你是时空关联度模式匹配和时空知识元组表示表达模型构建方面的专家。"},
                {"role": "user", "content": prompt2},
                {"role": "assistant", "content": assistant2}
            ]
            step2_response = self.get_chat_messages(step2_prompt)
            if 'spo' not in step2_response and "spoType" not in step2_response and "spoTypeSTC" not in step2_response:
                continue
            spo_list2,spo_type_list2,spoSTC_list2, T_list2,S_list2 = parse_response(step2_response)

            #时空知识表达模型构建
            st_tuple, st_tuple_stc = 'error_tuple', 'error_stc'  # 对于匹配错误时的标签
            for index, (spo_value, spo_type_value, spo_STC_value, T, L) in enumerate(
                    zip(spo_list2, spo_type_list2, spoSTC_list2, T_list2, S_list2), start=1):
                spo_tuple = spo_value.split(', ')
                try:
                    sub_predictions, rel_predictions, obj_predictions = spo_tuple
                except ValueError:
                    continue
                spo_STC_value = '{' + spo_STC_value.strip('"') + '}'
                stc_info = ast.literal_eval(spo_STC_value)  # 使用 ast.literal_eval 将字符串转换为字典
                stc_t, stc_s = stc_info.get('STC_T', ''), stc_info.get('STC_S', '')
                st_tuple_stc = f"{stc_t}_{stc_s}"
                if (sub_predictions in sub_true_labels or sub_true_labels in sub_predictions)\
                        and (obj_predictions in obj_true_labels or obj_true_labels in obj_predictions):
                # 用百分之75%
                    rel_same_list = self.relation_same.get(rel_true_labels, [])
                    if rel_predictions in rel_same_list:
                        print(data_T,data_L)
                        if data_T == None or data_T in [sub_true_labels, sub_predictions] or data_T in rel_predictions or data_T in T or T in data_T:
                            T = data_T
                        if data_L == None or data_L in [sub_true_labels, sub_predictions] or data_L in L or L in data_L:
                            L = data_L
                        flag_t = {'Strong': 0, 'Medium': 1}.get(stc_t, -1)  # 根据STC_T和STC_S确定flag和初始st_tuple
                        st_tuple = f'({sub_true_labels}, {rel_true_labels}, {obj_true_labels}'
                        if flag_t == 0:  # 添加时间信息
                            st_tuple += f', {T}'
                        elif flag_t == 1:
                            st_tuple += f'), {{{T}'
                        if stc_s == 'Strong':  # 添加空间信息
                            if flag_t in [0, -1]:
                                st_tuple += f', {L})'
                            else:  # flag_t == 1
                                st_tuple = f'({sub_true_labels}, {rel_true_labels}, {obj_true_labels}, {L}), {{{T}}}'
                        elif stc_s == 'Medium':
                            if flag_t == 1:
                                st_tuple += f', {L}}}'
                            else:
                                st_tuple += f'), {{{L}}}'
                        else:
                            st_tuple += f')' if flag_t != 1 else '})'
                        break
            tuple_predictions.append(st_tuple)
            STC_predictions.append(st_tuple_stc)
            tuple_true_labels.append(dataSTTuple)
            STC_true_labels.append(f"{dataSTC['STC_T']}_{dataSTC['STC_S']}")

            # 将内容写入日志文件
            self.loggertxt.write(
                f'\n\n{"*" * 50}-{i}-{lenfew}-{self.model}-{status}-{"*" * 50}\n'
                f'【Prompt{i}-1】: \n{prompt1}\n\n'
                f'【ChatGPT{i}-1】: \n{step1_response}\n\n'
                f'【Reslut{i}-1】:\n'
                f'\t1、spo: {spo_list1}\t\n'
                f'\t2、spoType: {spo_type_list1}\n\n'
                f"【Prompt{i}-2】: \n{prompt2}\n\n"
                f"【ChatGPT{i}-2】:\n{step2_response}\n\n"
                f"【Result{i}-2】:\n"
                f"\t1、spo: {spo_list2}\n"
                f"\t2、spoType: {spo_type_list2}\n"
                f"\t3、spoTypeSTC: {spoSTC_list2}\n"
                f"\t4、T_list: {T_list2}\n"
                f"\t5、S_list: {S_list2}\n\n"
                f'【Prediction】:\n{st_tuple};{st_tuple_stc}\n\n'
                f'【TrueLabel】:\n{dataSTTuple};{dataSTC["STC_T"]}_{dataSTC["STC_S"]}\n\n'
            )
            if i % 15 == 0:
                print(f"{i} ，暂停 15 秒钟...")
                time.sleep(1 * 15)  # 暂停 30 分钟（30 分钟 * 60 秒/分钟）
        self.loggertxt.write(f"【{self.model}-STTuple-预测结果】: \n{len(tuple_predictions)}-{tuple_predictions}\n"
                             f"【{self.model}-STTuple-正确标签】: \n{len(tuple_true_labels)}-{tuple_true_labels}\n"
                             f"【{self.model}-STC-预测结果】: \n{len(tuple_predictions)}-{tuple_predictions}\n"
                             f"【{self.model}-STC-正确标签】: \n{len(tuple_true_labels)}-{tuple_true_labels}\n")
        assert len(STC_predictions) == len(STC_true_labels), "STC_predictions 和 STC_true_labels 的长度不一致"
        assert len(tuple_predictions) == len(tuple_true_labels), "tuple_predictions 和 tuple_true_labels 的长度不一致"

        return [STC_predictions,STC_true_labels],[tuple_predictions, tuple_true_labels]

def gpt_exper_run(models, endlen):
    # 替换为你的实际API密钥
    # 获取当前时间，格式为 '年-月-日_时-分-秒'
    timestamp = time.strftime("%Y%m%d")
    result_folder_path_m = os.path.join(pmresultPath, f'{timestamp}_{endlen}')
    if not os.path.exists(result_folder_path_m):
        os.makedirs(result_folder_path_m)
        print(f"文件夹 '{result_folder_path_m}' 已成功创建。")
    else:
        print(f"文件夹 '{result_folder_path_m}' 已经存在。")
    API_KEY = "sk-gfcaGbEnb9Cr9W5o464fA4BeA6B14d60B9A2383fD5Ec8596"
    result_file_stc = os.path.join(result_folder_path_m, 'test_results_STC.csv')  # 结果文件路径
    result_file_sttuple = os.path.join(result_folder_path_m, 'test_results_STtuple.csv')  # 结果文件路径
    model_loger_path = os.path.join(result_folder_path_m, 'model_logger.json')

    result_file_time = os.path.join(result_folder_path_m,'time_duration.csv')  # 结果文件路径
    #结果
    result_stc = open(result_file_stc, 'a+', encoding='utf-8')
    result_sttuple = open(result_file_sttuple, 'a+', encoding='utf-8')
    result_time = open(result_file_time, 'a+', encoding='utf-8')
    model_loger_json = read_json(model_loger_path)
    # 打开文件对象并写入表头

    result_sttuple.seek(0)
    if result_sttuple.read() == '':
        print('文件为空，添加表头')
        header = "model,pattern,precision,recall,f1,predictions,labels\n"  # 写入表头
        result_content_time = "model,pattern,time\n"  # 写入表头
        result_stc.write(header)
        result_sttuple.write(header)
        result_time.write(result_content_time)



    for model in models:
        shotlist = model_loger_json[model]
        modelloggertxt = open(os.path.join(gptloggerPath,f'{model}_Logger.txt'),'w',encoding='utf-8')    #用于记录写入的标签
        # 创建知识模型对象
        knowledge_model = KnowledgeModel(API_KEY, model, modelloggertxt)

        # 文件路径
        test_data_file = os.path.join(gptfilePath,'testdatalist.txt')
        train_data_file = os.path.join(gptfilePath,'traindatalist.txt')
        # 读取测试数据和训练数据
        testdata = knowledge_model.read_data_from_file(test_data_file)
        traindata = knowledge_model.read_data_from_file(train_data_file)    #用于少样本
        random.shuffle(testdata)
        testdata = list(testdata)

        # 零样本测试
        if 'zero_shot' not in shotlist:
            knowledge_model.logger.info(f"{model}-开始零样本测试...")
            start_time_zero = time.time()
            evaluation_zero_stc, evaluation_zero_sttuple = knowledge_model.perform_zero_shot_test(
                testdata[:endlen])
            end_time_zero = time.time()
            zero_shot_duration = end_time_zero - start_time_zero
            knowledge_model.logger.info(f"{model}-零样本测试完成，耗时: {zero_shot_duration:.2f} 秒")
            result_stc.write(f"{model},{','.join(map(str, evaluation_zero_stc))}\n")        # 将零样本测试结果写入文件
            result_sttuple.write(f"{model},{','.join(map(str, evaluation_zero_sttuple))}\n")

            result_time.write(f'{model},zero_shot,{zero_shot_duration}\n')
            model_loger_json[model].append('zero_shot')
            print(model_loger_json)
            write_json(model_loger_path,model_loger_json)
        else:
            print(f'{model}-zero：已处理')

        # 少样本测试-
        lenfewlist = [3,6]
        for lenfew in lenfewlist:
            if f'few_shot-{lenfew}' in shotlist:
                print(f'{model}-{lenfew}：已处理')
                continue
            knowledge_model.logger.info(f"{model}-开始少样本-{lenfew}-测试...")
            start_time_few = time.time()
            evaluation_few_stc, evaluation_few_sttuple = knowledge_model.perform_few_shot_test(
                traindata, testdata[:endlen],lenfew=lenfew)
            end_time_few = time.time()
            few_shot_duration = end_time_few - start_time_few
            knowledge_model.logger.info(f"{model}-少样本测试-{lenfew}完成，耗时: {few_shot_duration:.2f} 秒")
            result_stc.write(f"{model},{','.join(map(str, evaluation_few_stc))}\n")        # 将少样本测试结果写入文件
            result_sttuple.write(f"{model},{','.join(map(str, evaluation_few_sttuple))}\n")

            result_time.write(f'{model},few_shot-{lenfew},{few_shot_duration}\n')
            model_loger_json[model].append(f'few_shot-{lenfew}')
            print(model_loger_json)
            write_json(model_loger_path,model_loger_json)



