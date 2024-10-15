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

filelist=os.listdir('/Volumes/资料宗卷 1/data')
for i in range(len(filelist)):
    file=filelist[i]
    fileBaseName,attributeName=os.path.splitext(file)
    if not (os.path.exists('/Volumes/资料宗卷 1/data/'+fileBaseName+'.txt') and os.path.exists('/Volumes/资料宗卷 1/data/'+fileBaseName+'.glb')):
        print(f"delete {file}")
        os.remove('/Volumes/资料宗卷 1/data/'+file)