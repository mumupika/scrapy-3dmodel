import os,shutil
file_list = os.listdir('./data')
file_list.sort(key=lambda f: os.path.getctime(os.path.join('./data', f)))

for i in range(len(file_list)):
    if i % 100 == 0:
        os.mkdir(f'./data_store/data{(i // 100)}')
        dst = f'./data_store/data{(i // 100)}'
    shutil.move('./data/'+file_list[i],dst)

