'''
remove_punctuation:去除分词列表中的标点符号及对应的词性
'''

from ctgucode.tools.SetGlobalVariables import stoplist

def remove_punctuation(tokens, pos_tags):
    """
    去停用词
    参数：
    - tokens: 分词列表
    - pos_tags: 词性列表
    返回：
    一个元组，包含去除标点符号后的分词列表和相应的词性列表
    """
    clean_tokens, clean_pos_tags = [],[]

    for token, pos_tag in zip(tokens, pos_tags):
        if token not in stoplist:
            clean_tokens.append(token)
            clean_pos_tags.append(pos_tag)
    assert len(clean_tokens) == len(clean_pos_tags)
    return clean_tokens, clean_pos_tags


