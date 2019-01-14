import jieba
import pickle

def answer(question):
    # 加载待计算的问题
    data3 = jieba.cut(question)
    data31 = ""
    for item in data3:
        data31 += item + " "
    new_doc = data31
    new_vec = dictionary.doc2bow(new_doc.split())
    sim = index[tfidf[new_vec]]
    postion = sim.argsort()[-1]
    answer = a[postion]
    
    return answer

# 直接加载训练好的模型
fh = open("dictionary.pk", "rb")
dictionary = pickle.load(fh)
fh.close()

fh = open("index.pk", "rb")
index = pickle.load(fh)
fh.close()

fh = open("tfidf.pk", "rb")
tfidf = pickle.load(fh)
fh.close()

fh = open("a.pk", "rb")
a = pickle.load(fh)
fh.close()

'''
while True:
    question = input("请输入您想问的问题：")
    # 响应信息
    rst= answer(question)
    print(rst)
'''


