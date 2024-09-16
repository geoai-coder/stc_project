from ctgucode.tools.SetGlobalVariables import ltp_instance, lexiconlist
import torch
from ctgucode.tools.WordlistProcess import remove_punctuation  # 常用函数: 处理分词列表
from ctgucode.tools.CommonFun_re import replace_spaces_with_comma


class LTP_:
    def __init__(self, text):
        self.ltp_instance=ltp_instance
        self.text = replace_spaces_with_comma(text).strip()
        if torch.cuda.is_available():
            self.ltp_instance.to('cuda')
        self.ltp_instance.add_words(lexiconlist)  # 添加自定义词典

    def ltpCommonFunction(self, disrecord=None, Record=False):
        """
        调用LTP工具进行句子处理
        :param disrecord: 记录结果的文件对象（可选）
        :param Record: 是否记录结果（布尔值）
        :return: 分词、词性、依存分析、语义角色标注结果
        """
        hidden = self.ltp_instance.pipeline([self.text], tasks=['cws', 'pos', 'srl', 'dep', 'sdp'])
        text_seg = [element.strip() for element in hidden.cws[0]]  # 分词
        text_pos = hidden.pos[0]  # 词性
        text_dep = hidden.dep[0]  # 依存句法分析
        text_srl = hidden.srl[0]  # 语义角色标注

        result = (f'\n\n###文本：{self.text}'
                  f'\n###分词词性：{[(seg, pos) for seg, pos in zip(text_seg, text_pos)]}'
                  f'\n###依存分析：{text_dep}'
                  f'\n###语义角色：{text_srl}')

        if Record:
            disrecord.write(result)
        print(result)

        return text_seg, text_pos, text_dep, text_srl

    def ltpToStopwords(self, disrecord=None, Record=False):
        """
        调用LTP工具进行句子处理，并去掉停用词
        :param disrecord: 记录结果的文件对象（可选）
        :param Record: 是否记录结果（布尔值）
        :return: 去掉停用词的分词列表和词性列表
        """
        hidden = self.ltp_instance.pipeline([self.text], tasks=['cws', 'pos'])
        text_seg1 = hidden.cws[0]  # 分词
        text_pos1 = hidden.pos[0]  # 词性
        text_seg, text_pos = remove_punctuation(text_seg1, text_pos1)

        result = (f'\n\n###文本：{self.text}'
                  f'\n###原分词词性：{[(seg, pos) for seg, pos in zip(text_seg1, text_pos1)]}'
                  f'\n###分词词性：{[(seg, pos) for seg, pos in zip(text_seg, text_pos)]}')

        if Record:
            disrecord.write(result)

        return (text_seg1,text_pos1),(text_seg, text_pos)

    def ltpToNER(self):
        """
        调用LTP工具进行命名实体识别
        :return: 命名实体识别结果
        """
        hidden = self.ltp_instance.pipeline([self.text], tasks=['cws', 'ner'])
        return hidden.ner[0]  # 命名实体识别

    def ltpTowords(self, disrecord=None, Record=False):
        """
        调用LTP工具进行句子处理
        :param disrecord: 记录结果的文件对象（可选）
        :param Record: 是否记录结果（布尔值）
        :return: 分词和词性列表
        """
        try:
            hidden = self.ltp_instance.pipeline([self.text], tasks=['cws', 'pos'])
            text_seg = [element.strip() for element in hidden.cws[0]]  # 分词
            text_pos = hidden.pos[0]  # 词性

            result = (f'\n\n###文本：{self.text}'
                      f'\n###分词词性：{[(seg, pos) for seg, pos in zip(text_seg, text_pos)]}')

            if Record:
                disrecord.write(result)

            return text_seg, text_pos

        except KeyError:
            return False, False
