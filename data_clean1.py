import os
import re

item_list=os.listdir('./data')
for item in item_list:
    fileBaseNameNoExtension=item.split(' ')[0].split('.')[0]
    regex=re.compile(fileBaseNameNoExtension+r' \([0-9]+\).glb$')
    if regex.match(item):
        os.remove('./data/'+item)
        print(f"删除重复文件:{item}")
        
    regex2=re.compile(fileBaseNameNoExtension+r' \([0-9]+\).glb.[A-Za-z]+$')
    if regex2.match(item):
        os.remove('./data/'+item)
        print(f"删除重复下载中文件:{item}")
        
    regex3=re.compile(fileBaseNameNoExtension+r' \([0-9]\).glb.crdownload$')
    if regex3.match(item):
        os.remove('./data/'+item)
        print(f"删除重复下载中文件:{item}")
        
    regex=re.compile(fileBaseNameNoExtension+r' \([0-9]+\).txt$')
    if regex.match(item):
        os.remove('./data/'+item)
        print(f"删除重复文件:{item}")
