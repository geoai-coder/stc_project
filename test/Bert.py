import torch
from transformers import BertTokenizer, BertModel
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re

# 加载BERT模型和tokenizer
model_name = '../../Model/bert-base-chinese'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

def encode_sentence(sentence, tokenizer, model):
    inputs = tokenizer(sentence, return_tensors='pt', padding=True, truncation=True, max_length=64)
    with torch.no_grad():
        outputs = model(**inputs)
    # 获取[CLS] token的输出表示
    sentence_embedding = outputs.last_hidden_state[:, 0, :].numpy()
    return sentence_embedding

def extract_features(sentence):
    # 提取年份和金额信息
    year = re.findall(r'\d{4}年', sentence)
    amount = re.findall(r'\d+万美元', sentence)
    year = int(year[0][:-1]) if year else 0
    amount = int(amount[0][:-3]) if amount else 0
    return np.array([year, amount])

def combine_embeddings(bert_embedding, features):
    # 将BERT嵌入和额外特征结合
    combined = np.concatenate([bert_embedding, features.reshape(1, -1)], axis=1)
    return combined

# 句子列表
sentences = ['2024年，上海的GDP总计是1000万美元', '2023年，上海的GDP总计是900万美元']

# 编码句子并提取特征
embeddings = []
for sentence in sentences:
    bert_embedding = encode_sentence(sentence, tokenizer, model)
    features = extract_features(sentence)
    combined_embedding = combine_embeddings(bert_embedding, features)
    embeddings.append(combined_embedding)

# 计算相似度
similarity = cosine_similarity(embeddings[0], embeddings[1])
print(f'相似度: {similarity[0][0]}')
