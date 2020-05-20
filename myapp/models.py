from django.db import models

# -*- coding: utf-8 -*-
import nltk
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
from rake_nltk import Rake
from nltk.stem import WordNetLemmatizer

class QuestionPrediction:
    """
    问题预测: 采用NB进行多分类
    数据集：template_train.csv
    """

    def __init__(self):
        # 训练模板数据
        self.train_file = r'C:\Users\chend\Desktop\SAP_ITSM\model\question.csv'
        # 读取训练数据
        self.train_x, self.train_y = self.read_train_data(self.train_file)
        # 训练模型
        self.model = self.train_model_NB()

    # 获取训练数据
    def read_train_data(self, template_train_file):
        """
        可改写为读取一个文件
        """
        train_x = []
        train_y = []
        train_data = pd.read_csv(template_train_file)
        train_x = train_data["text"].apply(lambda x: " ".join(list(nltk.word_tokenize(str(x))))).tolist()
        train_y = train_data["label"].tolist()
        return train_x, train_y

    def train_model_NB(self):
        """
        采用NB训练模板数据，用于问题分类到某个模板
        """
        x_train, y_train = self.train_x, self.train_y
        self.tv = TfidfVectorizer()

        train_data = self.tv.fit_transform(x_train).toarray()
        clf = MultinomialNB(alpha=0.01)
        clf.fit(train_data, y_train)
        return clf

    def predict(self, question):
        """
        问题预测，返回结果为label
        """
        question = [" ".join(list(nltk.word_tokenize(question)))]
        print("question:", question)
        test_data = self.tv.transform(question).toarray()
        y_pred = self.model.predict(test_data)[0]
        return y_pred


def get_relation(quest):
    relation = {0: "next", 1: "has_detail", 2: "prev", 3: "has_scenario", 4: "has_step", 5: "has_question",
                6: "has_purpose", 7: "when", 8: "has_level", 9: "has_definition", 10: "has_cause", 11: "has_effect"}

    question_model = QuestionPrediction()

    # while 1:
    # 输入问题
    # quest = input("\n请输入待训练语句：")
    # if quest == "-1":
    #     print("----------ByeBye----------")
    #     break
    # print("你输入的是：", quest)

    # 开始训练
    pre_key = question_model.predict(quest)
    pre_val = relation[pre_key]
    print("训练结果为：", pre_key, ":", pre_val)
    return pre_val


def get_entity(question):
    ext = EntityExtraction()
    return ext.getEntity(question)


def nlpChange(question):
    # 分词
    tokens = nltk.word_tokenize(question)
    print("tokens:", tokens)
    # 加词性
    tagged = nltk.pos_tag(tokens)
    print("tagged:", tagged)
    # 仅对动词进行词性还原
    newSentence = ''
    newWord = ''
    lemmatizer = WordNetLemmatizer()
    for word, tag in tagged:
        newWord = word
        if tag.startswith('VB'):
            newWord = lemmatizer.lemmatize(word, pos='v')
        newSentence += newWord + ' '
    print("changed tag:", newSentence)
    return newSentence


def extractKeyword(sentence):
    usualList = ['want', 'show', 'way', 'method']

    r = Rake()
    r.extract_keywords_from_text(sentence)
    rankedList = r.get_ranked_phrases()
    print("ranked_list:", rankedList)

    # 删除usualList中的词
    newList = [i for i in rankedList if i not in usualList]
    return newList


class EntityExtraction:
    def __init__(self):
        pass

    def getEntity(self, question):
        newSentence = nlpChange(question)
        newList = extractKeyword(newSentence)
        return newList
