import os,shutil,zipfile,json

with open('./progress/store_index.json','r') as f:
    store_index=json.load(f)
f.close()


file_list = os.listdir('./data')
file_list.sort(key=lambda f: os.path.getctime(os.path.join('./data', f)))

for i in range(len(file_list)//100*100):
    if i % 100 == 0:
        os.mkdir(f'./data_store/data{(i // 100)}')
        dst = f'./data_store/data{(i // 100)}'
    shutil.move('./data/'+file_list[i],dst)


file_list_store = len(os.listdir('./data_store'))

for i in range(file_list_store):
    zip = zipfile.ZipFile(f'./data_store/data{i+store_index}.zip',"w",zipfile.ZIP_DEFLATED)
    for path, dirnames, filenames in os.walk(f'./data_store/data{i}'):
        fpath = path.replace(f'./data_store/data{i}','')
        for filename in filenames:
            zip.write(os.path.join(path,filename), os.path.join(fpath, filename))
    zip.close()

with open('./progress/store_index.json','w') as f:
    json.dump(store_index + file_list_store,f)
f.close()