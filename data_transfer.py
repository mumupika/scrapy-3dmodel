import os,shutil
file_list = os.listdir('./data')
file_list.sort(key=lambda f: os.path.getctime(os.path.join('./data', f)))

for i in range(len(file_list)):
    if i % 100 == 0:
        os.mkdir(f'./data_store/data{(i // 100)}')
        dst = f'./data_store/data{(i // 100)}'
    shutil.move('./data/'+file_list[i],dst)

import os,shutil,zipfile
file_list = os.listdir('./data')
file_list.sort(key=lambda f: os.path.getctime(os.path.join('./data', f)))

for i in range(len(file_list)):
    if i % 100 == 0:
        os.mkdir(f'./data_store/data{(i // 100)}')
        dst = f'./data_store/data{(i // 100)}'
    shutil.move('./data/'+file_list[i],dst)

for i in range(10):
    zip = zipfile.ZipFile(f'./data_store/data{i}.zip',"w",zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(f'./data_store/data_{i}'):
        fpath = path.replace(f'./data_store/data{i}','')
        for filename in filenames:
            zip.write(os.path.join(path,filename), os.path.join(fpath, filename))
    zip.close()