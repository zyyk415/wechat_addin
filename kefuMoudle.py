import jieba
from gensim import corpora, models, similarities
import pickle
import xlrd
import xlsxwriter
import os
import logging

try:
    #取得当前文件的目录
    pathFloder = os.path.dirname(__file__)
    excelFilePath = os.path.join(pathFloder,"维尔客服自动回复.xlsx")
    #打开目标处理xlsx
    ExcelFile=xlrd.open_workbook(excelFilePath) 
    #定位到索引为0的工作表，即第一个工作表
    sheet=ExcelFile.sheet_by_index(0)
    #取问题与回答的数据
    q=sheet.col_values(1)
    a=sheet.col_values(2)
    
    '''
    q = ["你好，在吗？",
         "注册照片为空",
         "读取物理卡失败"
         ]
    a = ["在的，亲，欢迎您光临维尔计时设备机器人系统",
         "1.请同步信息\n2.请重新采集模板",
         "请更换IC卡，或采用无卡签退"
         ]
    '''
    qcut = []
    for i in q:
        data1 = ""
        this_data = jieba.cut(i)
        for item in this_data:
            data1 += item + " "
        qcut.append(data1)
    
    docs = qcut
    
    # w1_list = []
    # for doc in docs:
    #      for w1 in doc.split():
    #           print(w1)
    #      w1_list.append([w1 for w1 in doc.split()])
    
    tall = [[w1 for w1 in doc.split()] for doc in docs]
    
    # corpora.Dictionary()
    # 将二维数组转为字典
    dictionary = corpora.Dictionary(tall)
    # print(dictionary)
    # for dic in dictionary:
    #      print(dictionary[dic])
    
    # gensim的doc2bow实现词袋模型
    corpus = [dictionary.doc2bow(text) for text in tall]
    # print(corpus)
    
    # corpus是一个返回bow向量的迭代器。下面代码将完成对corpus中出现的每一个特征的IDF值的统计工作
    tfidf = models.TfidfModel(corpus)
    print(tfidf)
    
    # 通过token2id得到特征数
    num = len(dictionary.token2id.keys())
    #稀疏矩阵相似度，从而建立索引
    index = similarities.SparseMatrixSimilarity(tfidf[corpus], num_features=num)
    
    '''
    pickle提供了一个简单的持久化功能。可以将对象以文件的形式存放在磁盘上。
    pickle模块只能在python中使用，python中几乎所有的数据类型（列表，字典，集合，类等）都可以用pickle来序列化，
    pickle序列化后的数据，可读性差，人一般无法识别。
    pickle.dump(obj, file, protocol)
    序列化对象，并将结果数据流写入到文件对象中。参数protocol是序列化模式，默认值为0，表示以文本的形式序列化。protocol的值还可以是1或2，表示以二进制的形式序列化。
    pickle.load(file)
    反序列化对象。将文件中的数据解析为一个Python对象。
    '''
    
    fh = open("dictionary.pk", "wb")
    pickle.dump(dictionary, fh)
    fh.close()
    
    fh = open("tfidf.pk", "wb")
    pickle.dump(tfidf, fh)
    fh.close()
    
    fh = open("index.pk", "wb")
    pickle.dump(index, fh)
    fh.close()
    
    fh = open("a.pk", "wb")
    pickle.dump(a, fh)
    fh.close()

    print ("train OK")
except Exception as e:
        logging.exception(e)