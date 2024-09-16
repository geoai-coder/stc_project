from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import paired_cosine_distances
import torch
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity

"""
原始
"""
model = SentenceTransformer('../../Model/bert-base-chinese')
sentences = ['上海的GDP总计是1000万美元', '上海的GDP总计是900万美元']
sentence_embeddings = model.encode(sentences)
# print(sentence_embeddings)
cosine_score = 1 - paired_cosine_distances([sentence_embeddings[0]],[sentence_embeddings[1]])
print("0",cosine_score)

# 初始化 tokenizer 和 BERT 模型
tokenizer = BertTokenizer.from_pretrained('../../Model/bert-base-chinese')
model = BertModel.from_pretrained('../../Model/bert-base-chinese')


def get_sentence_embedding(sentence, tokenizer, model):
    tokens = tokenizer.tokenize(sentence)
    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    input_ids = torch.tensor(token_ids).unsqueeze(0)  # 增加一个维度以适应模型输入格式

    with torch.no_grad():
        outputs = model(input_ids)

    # 使用 [CLS] token 的嵌入
    cls_embedding = outputs.last_hidden_state[0, 0].numpy()

    return cls_embedding


# 输入句子
sentence1 = "上海的GDP总计是1000万美元 [TAIL] 1000万美元"
sentence2 = "上海的GDP总计是900万美元 [TAIL] 900万美元"

# 获取句子的嵌入向量
embedding1 = get_sentence_embedding(sentence1, tokenizer, model)
embedding2 = get_sentence_embedding(sentence2, tokenizer, model)

# 计算余弦相似度
similarity = cosine_similarity([embedding1], [embedding2])[0][0]

print("Cosine similarity1:", similarity)

def get_keyword_embedding(sentence, keywords, tokenizer, model):
    tokens = tokenizer.tokenize(sentence)
    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    input_ids = torch.tensor(token_ids).unsqueeze(0)  # 增加一个维度以适应模型输入格式

    with torch.no_grad():
        outputs = model(input_ids)

    hidden_states = outputs.last_hidden_state.squeeze(0)

    # 找到关键字的位置并提取其嵌入
    keyword_embeddings = []
    for keyword in keywords:
        keyword_tokens = tokenizer.tokenize(keyword)
        keyword_token_ids = tokenizer.convert_tokens_to_ids(keyword_tokens)
        keyword_length = len(keyword_token_ids)

        # 找到关键字 token 的起始位置
        for i in range(len(token_ids) - keyword_length + 1):
            if token_ids[i:i + keyword_length] == keyword_token_ids:
                keyword_embeddings.append(hidden_states[i:i + keyword_length].mean(dim=0))
                break

    # 将关键字嵌入平均化以获取最终的句子嵌入
    sentence_embedding = torch.stack(keyword_embeddings).mean(dim=0).numpy()

    return sentence_embedding


# 输入句子
sentence1 = "上海的GDP总计是1000万美元"
sentence2 = "上海的GDP总计是900万美元"

# 关键字
keywords1 = ["1000万美元"]
keywords2 = ["900万美元"]

# 获取句子的嵌入向量
embedding1 = get_keyword_embedding(sentence1, keywords1, tokenizer, model)
embedding2 = get_keyword_embedding(sentence2, keywords2, tokenizer, model)

# 计算余弦相似度
similarity = cosine_similarity([embedding1], [embedding2])[0][0]

print("Cosine similarity:", similarity)


def get_weighted_mean_pooling_embedding(sentence, keywords, tokenizer, model):
    tokens = tokenizer.tokenize(sentence)
    token_ids = tokenizer.convert_tokens_to_ids(tokens)
    input_ids = torch.tensor(token_ids).unsqueeze(0)  # 增加一个维度以适应模型输入格式

    with torch.no_grad():
        outputs = model(input_ids)

    hidden_states = outputs.last_hidden_state.squeeze(0)

    # 定义权重向量，与 tokens 长度相同
    weights = torch.ones(hidden_states.size(0))

    # 根据关键字调整权重
    for keyword in keywords:
        keyword_tokens = tokenizer.tokenize(keyword)
        keyword_token_ids = tokenizer.convert_tokens_to_ids(keyword_tokens)

        # 找到关键字在 tokens 中的位置
        for i in range(len(token_ids) - len(keyword_token_ids) + 1):
            if token_ids[i:i + len(keyword_token_ids)] == keyword_token_ids:
                # 赋予更大的权重，例如乘以2
                weights[i:i + len(keyword_token_ids)] *= 2.0

    # 加权平均
    weighted_mean_embedding = torch.sum(hidden_states * weights.unsqueeze(1), dim=0) / torch.sum(weights).item()

    return weighted_mean_embedding.numpy()


# 输入句子
sentence1 = "2024年，上海的GDP总计是1000万美元"
sentence2 = "2023年，上海的GDP总计是900万美元"

# 关键字，包括时间和金额
keywords1 = ["1000万美元"]
keywords2 = ["900万美元"]

# 获取句子的嵌入向量
embedding1 = get_weighted_mean_pooling_embedding(sentence1, keywords1, tokenizer, model)
embedding2 = get_weighted_mean_pooling_embedding(sentence2, keywords2, tokenizer, model)

# 计算余弦相似度
similarity = cosine_similarity([embedding1], [embedding2])[0][0]

print("Cosine similarity3:", similarity)
"""
第一次修改
"""
# 定义自定义的预处理函数
def preprocess(sentence):
    # 使用特殊标记来突出时间和数值信息
    amount = sentence.split('是')[1]
    return f"[TAILTAGS] {amount} {sentence}"

# 初始化模型
model = SentenceTransformer('../../Model/bert-base-chinese')

# 原始句子
sentences = ['上海的GDP总计是1000万美元', '上海的GDP总计是900万美元']

# 预处理句子
preprocessed_sentences = [preprocess(sentence) for sentence in sentences]

# 句子向量化
sentence_embeddings = model.encode(preprocessed_sentences)

# 打印向量
# print(sentence_embeddings)

# 计算余弦相似度
cosine_score = 1 - paired_cosine_distances([sentence_embeddings[0]], [sentence_embeddings[1]])
print("1",cosine_score)

"""
第三次修改
"""
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import paired_cosine_distances
import numpy as np

# 定义自定义的预处理函数
def preprocess(sentence):
    # 使用多次重复标记来突出时间和数值信息
    amount = sentence.split('是')[1]
    return f"{sentence} [AMOUNT] {amount}"

# 初始化模型
modelpath = '../../Model/sbert-base-chinese-nli'
model = SentenceTransformer(modelpath)

# 原始句子
sentences = ['上海的GDP总计是1000万美元', '上海的GDP总计是900万美元']

# 预处理句子
preprocessed_sentences = [preprocess(sentence) for sentence in sentences]

# 句子向量化
sentence_embeddings = model.encode(preprocessed_sentences)

# 添加时间和数值信息到向量中
def add_info_embedding(sentence, embedding):
    amount = int(sentence.split('是')[1].replace('万美元', ''))
    # 对时间和数值进行标准化处理
    amount_norm = amount / 1000
    # 将标准化的时间和数值信息添加到向量的末尾
    return np.append(embedding, [amount_norm])

enhanced_embeddings = [add_info_embedding(sentences[i], sentence_embeddings[i]) for i in range(len(sentences))]

# 打印增强后的向量
# print(enhanced_embeddings)

# 计算余弦相似度
cosine_score = 1 - paired_cosine_distances([enhanced_embeddings[0]], [enhanced_embeddings[1]])
print("2",cosine_score)

"""
第四次修改
"""
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import paired_cosine_distances

# 定义自定义的预处理函数
def preprocess(sentence):
    amount = sentence.split('是')[1]
    # 添加描述性上下文
    return f"GDP为{amount}。原文：{sentence}"

# 初始化模型
model = SentenceTransformer('../../Model/bert-base-chinese')

# 原始句子
sentences = ['上海的GDP总计是1000万美元', '上海的GDP总计是900万美元']

# 预处理句子
preprocessed_sentences = [preprocess(sentence) for sentence in sentences]

# 句子向量化
sentence_embeddings = model.encode(preprocessed_sentences)

# 计算余弦相似度
cosine_score = 1 - paired_cosine_distances([sentence_embeddings[0]], [sentence_embeddings[1]])
print("3",cosine_score)


"""
第五次
"""
from sentence_transformers import SentenceTransformer, models
from sklearn.metrics.pairwise import paired_cosine_distances
import numpy as np

# 定义自定义的预处理函数
def preprocess(sentence):
    # 使用特殊标记来突出时间和数值信息
    amount = sentence.split('是')[1]
    return f"[AMOUNT] {amount} {sentence}"

# 提取时间和数值特征
def extract_features(sentence):
    year = int(sentence.split('年')[0])
    amount = int(sentence.split('是')[1].replace('万美元', '').replace(',', ''))
    return np.array([year, amount])

# 初始化模型
model = SentenceTransformer('../../Model/bert-base-chinese')

# 原始句子
sentences = ['2024年，上海的GDP总计是1000万美元', '2023年，上海的GDP总计是900万美元']

# 预处理句子
preprocessed_sentences = [preprocess(sentence) for sentence in sentences]

# 句子向量化
sentence_embeddings = model.encode(preprocessed_sentences)

# 提取额外特征
extra_features = np.array([extract_features(sentence) for sentence in sentences])

# 合并向量和额外特征
combined_embeddings = np.hstack((sentence_embeddings, extra_features))

# 打印向量
# print(combined_embeddings)

# 计算余弦相似度
cosine_score = 1 - paired_cosine_distances([combined_embeddings[0]], [combined_embeddings[1]])
print("5",cosine_score)

"""
第6词修改
"""
