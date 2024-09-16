#动态语义分析
import json
import os
from collections import defaultdict
import torch
from tqdm import tqdm
from transformers import BertTokenizer, BertModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt

# 加载预训练的BERT模型和分词器
tokenizer = BertTokenizer.from_pretrained('../../Model/bert-base-chinese')
model = BertModel.from_pretrained('../../Model/bert-base-chinese')
model.eval()

def DividDimen(text_spo_dict,dime):
    """
    分维度计算
    :param text_spo_dict:   字典列表
    :param dime:    维度：时间和空间
    :return: 每个维度下不同值的元组
    {
    "T1": [spo1,spo2,...],
    "T2": [spo1,spo2,...]
    }
    """
    grouped_data = defaultdict(list)    # 创建一个默认字典来存储分组结果
    for item in text_spo_dict:    # 遍历列表，将相同T值的spo键的内容合并
        value = item[dime]
        spo_value = item['spo']
        spotext = spo_value[0] + '的' + spo_value[1] + '是' + spo_value[2]  # 将词转换为WordPiece tokens
        CLStext = f'{spotext} [TAIL] {spo_value[2]}'
        grouped_data[value].append(CLStext)
    result = dict(grouped_data)    # 将默认字典转换为普通字典
    return result

def dime_spo_vector(dimekey,dimeSpoList,dime,i):
    """
    将对应维度下的，某一实例对应的元组列表进行向量化，并对其进行降维用于聚类
    :param datalist:
    :return:
    """
    EmbeddingList,dimelist = [],[]
    # 预处理句子
    for sentence in dimeSpoList:
        tokens = tokenizer.tokenize(sentence)
        # 获取WordPiece tokens的ID
        token_ids = tokenizer.convert_tokens_to_ids(tokens)
        # 将token_ids转换为张量
        input_ids = torch.tensor(token_ids).unsqueeze(0)  # 增加一个维度以适应模型输入格式
        # 使用BERT模型获取嵌入
        with torch.no_grad():
            outputs = model(input_ids)
        # 获取WordPiece嵌入
        sentence_embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()  # 取平均值作为词向量
        EmbeddingList.append({f"{dimekey},{sentence}":sentence_embeddings})
        dimelist.append(f'{dime}dim{i}')
    return EmbeddingList,dimelist

def classify_semantic_similarity(embedding_list):
    def semantic_similarity(embedding1, embedding2):
        # 计算余弦相似度
        similarity = cosine_similarity([embedding1], [embedding2])
        return similarity[0, 0]  # 返回相似度值
    size = len(embedding_list)
    similarity_matrix = np.zeros((size, size))
    for i in range(size):
        similarity_matrix[i, i] = 0  # 自身相似度为1
        for j in range(i + 1, size):
            key1, embedding1 = list(embedding_list[i].items())[0]
            key2, embedding2 = list(embedding_list[j].items())[0]
            # 计算语义相似度
            similarity_score = semantic_similarity(embedding1, embedding2)
            if similarity_score == 1:
                similarity_score = 1
            else:
                similarity_score = 0
            similarity_matrix[i, j] = similarity_score
            similarity_matrix[j, i] = similarity_score
    return similarity_matrix

def plot_similarity_matrix(similarity_matrix,dimeVectorlist, savepath):
    fig, ax = plt.subplots()
    cax = ax.matshow(similarity_matrix, cmap='YlGnBu')  # 使用'YlGnBu'颜色映射

    for (i, j), val in np.ndenumerate(similarity_matrix):
        ax.text(j, i, f'{int(val)}', ha='center', va='center', color='white')  # 使用白色文本

    plt.colorbar(cax)
    plt.title('Semantic Similarity Matrix')
    plt.xlabel('Sentences')
    plt.ylabel('Sentences')

    ax.set_xticks(np.arange(len(similarity_matrix)))
    ax.set_yticks(np.arange(len(similarity_matrix)))

    ax.set_xticklabels(dimeVectorlist)
    ax.set_yticklabels(dimeVectorlist)

    plt.xticks(rotation=45)  # 旋转横轴标签以防止重叠

    ax.grid(which='both', color='black', linestyle='-', linewidth=0.5)
    plt.tight_layout()  # 调整布局以适应旋转的标签
    plt.savefig(savepath)
    plt.show()

if __name__=='__main__':
    input_folder_path = 'reldatafile/add_Text_dbpedia'
    output_folder_path = 'DynSemanticData'
    file_spojson = 'spo.json'
    for dime in ['L','T']:
        for item in tqdm(os.listdir(input_folder_path)):  # 跳过前3、6个文件
            print(item)
            item_path = os.path.join(input_folder_path, item)
            if os.path.isdir(item_path):
                spojson = os.path.join(item_path, file_spojson)
                outputfile = os.path.join(output_folder_path, item)
                if os.path.isfile(spojson):     #去读动态语义spo文件
                    if not os.path.exists(outputfile):  # 如果文件夹不存在，则创建文件夹
                        os.makedirs(outputfile)
                        print(f"文件夹 '{outputfile}' 已创建。")
                    filelist_Tail_Dynamics = []     #动态语义值列表
                    try:
                        print(f'----正在处理:{item}.json')
                        with open(spojson, 'r', encoding='utf-8') as file:      # 打开并读取JSON文件
                            jsondata = json.load(file)
                    except:
                        continue
                    for sub,text_spo in jsondata.items():
                        dimeVectorlist,i = [],0
                        dimedict = DividDimen(text_spo,dime)    #分维度获取元组
                        for spodimekey,spodimevalue in dimedict.items():
                            dimeVector,dimelist = dime_spo_vector(spodimekey,spodimevalue,dime,i)   #获取尾实体
                            dimeVectorlist+=dimelist
                            filelist_Tail_Dynamics += dimeVector    #将所有列表合并
                            i+=1
                        save_path = os.path.join(outputfile, f'{item}_散点图_{dime}_{sub}.png')    # 设置保存路径
                        similarity_matrix = classify_semantic_similarity(filelist_Tail_Dynamics)
                        plot_similarity_matrix(similarity_matrix,dimeVectorlist,save_path)                        # 可视化相似性矩阵
                    # try:
                    #     print(f'#语义特征取值：{sum(filelist_Tail_Dynamics) / len(filelist_Tail_Dynamics)}')
                    # except ZeroDivisionError:
                    #     continue


