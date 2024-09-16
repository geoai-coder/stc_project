import os
from ctgucode.tools.SetGlobalVariables import pmresultPath
from ctgucode.tools.Tool_Method import find_values_in_column
from typing import List
import ast

class STCEvaluator:
    def __init__(self,model, pmresultPath, timestamp, endlen):
        self.model = model
        self.result_folder_path_m = os.path.join(pmresultPath, f'{timestamp}_{endlen}')
        self.header = "model,pattern,precision,recall,f1,predictions,labels\n"

    def perform_stc_test(self, pattern):
        """执行少样本或零样本测试并返回评估结果"""
        search_content = [self.model, pattern]

        stclabel = find_values_in_column(os.path.join(self.result_folder_path_m,"test_results_STC1.csv"), search_content, 6)
        sttuple_pred = find_values_in_column(os.path.join(self.result_folder_path_m,"test_results_STtuple1.csv"), search_content, 5)
        sttuple_label = find_values_in_column(os.path.join(self.result_folder_path_m,"test_results_STtuple1.csv"), search_content, 6)
        print(search_content,type(stclabel),len(stclabel),stclabel)
        # print(stclabel)
        assert len(sttuple_pred)==len(sttuple_label)
        filtered_tuples = self.filter_tuples_based_on_stc(
            stclabel, sttuple_pred, sttuple_label
        )
        evaluation_results = {}
        for key, (predictions, true_labels) in filtered_tuples.items():
            evaluation_results[key] = self._evaluate_sklearn(pattern, (predictions, true_labels))
        return evaluation_results

    def filter_tuples_based_on_stc(self, STC_true_labels, tuple_predictions, tuple_true_labels):
        """
        筛选STC预测与真实标签匹配的位置，并获取相应的tuple预测和真实标签。

        参数:
        - STC_predictions (list): STC预测标签列表，格式为["{weak}-{strong}", ...]
        - STC_true_labels (list): STC真实标签列表，格式为["{weak}-{strong}", ...]
        - tuple_predictions (list): tuple预测标签列表
        - tuple_true_labels (list): tuple真实标签列表

        返回:
        - dict: 包含每种标签组合的tuple预测和真实标签的字典
        """
        filtered_tuples = {
            'Weak': ([], []),
            'Weak_Medium': ([], []),
            'Weak_Strong': ([], []),
            'Medium': ([], []),
            'Medium_Strong': ([], []),
            'Strong': ([], []),
        }
        for stc_true, tuple_pred, tuple_true in zip(STC_true_labels, tuple_predictions, tuple_true_labels):
            stc_set = sorted(list(set(stc_true.split('_'))), reverse=True)
            stc_comb = '_'.join(stc_set)
            if stc_comb in filtered_tuples:
                print(stc_comb,tuple_pred,tuple_true)
                filtered_tuples[stc_comb][0].append(tuple_pred)
                filtered_tuples[stc_comb][1].append(tuple_true)
        return filtered_tuples

    def precision_recall_f1(self, predictions: List[str], labels: List[str]):
        # 将 predictions 和 labels 转换为集合，便于计算交集
        predictions_set = set(predictions)
        labels_set = set(labels)

        # 计算真阳性 (True Positives)
        true_positives = predictions_set.intersection(labels_set)

        # Precision: 真阳性 / 预测为正的总数
        precision = round(len(true_positives) / len(predictions_set) if predictions_set else 0, 3)

        # Recall: 真阳性 / 实际为正的总数
        recall = round(len(true_positives) / len(labels_set) if labels_set else 0, 3)

        # F1 score: Precision 和 Recall 的调和平均数
        if precision + recall == 0:
            f1_score = 0
        else:
            f1_score = round(2 * (precision * recall) / (precision + recall), 3)

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


    def get_file_paths(self):
        """生成各标签组合的结果文件路径"""
        return {
            'Weak': os.path.join(self.result_folder_path_m,self.model, 'test_results_Weak.csv'),
            'Weak_Medium': os.path.join(self.result_folder_path_m,self.model, 'test_results_Weak_Medium.csv'),
            'Weak_Strong': os.path.join(self.result_folder_path_m,self.model, 'test_results_Weak_Strong.csv'),
            'Medium': os.path.join(self.result_folder_path_m,self.model, 'test_results_Medium.csv'),
            'Medium_Strong': os.path.join(self.result_folder_path_m,self.model, 'test_results_Medium_Strong.csv'),
            'Strong': os.path.join(self.result_folder_path_m,self.model, 'test_results_Strong.csv')
        }

    def open_files_with_headers(self):
        """打开文件并写入表头"""
        file_paths = self.get_file_paths()
        files = {key: open(path, 'w', encoding='utf-8') for key, path in file_paths.items()}
        for file in files.values():
            file.write(self.header)
        return files

    def write_evaluation_results(self, evaluation_results, files):
        """将评估结果写入相应的文件"""
        for key, (pattern, precision, recall, f1, pred, label) in evaluation_results.items():
            if key in files:
                result_file = files[key]
                result_file.write(f"{self.model},{pattern},{precision},{recall},{f1},{pred},{label}\n")


# 使用示例

def stc_run(model, timestamp, endlen):
    # 少样本评估
    evaluator = STCEvaluator(model, pmresultPath, timestamp, endlen)
    files = evaluator.open_files_with_headers()
    ContextualLearning = ['zero_shot','few_shot-3','few_shot-6']
    for cl in ContextualLearning:
        evaluation_few_allstc = evaluator.perform_stc_test(cl)
        evaluator.write_evaluation_results(evaluation_few_allstc, files)

if __name__ == '__main__':
    stc_run('gpt-4o-2024-08-06','20240902',-1)