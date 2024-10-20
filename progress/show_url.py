import pickle

# 读取 pkl 文件
with open('progress\download_url.pkl', 'rb') as file:
    links = pickle.load(file)

# 输出链接和链接条数
print("链接列表:", links[0])
print("链接条数:", len(links))