import os
# filelist=os.listdir('/Volumes/资料宗卷 1/data')
filelist=os.listdir('./data')
for i in range(len(filelist)):
    file=filelist[i]
    fileBaseName,attributeName=os.path.splitext(file)
    if not (os.path.exists('./data/'+fileBaseName+'.txt') and os.path.exists('./data/'+fileBaseName+'.glb')):
        print(f"delete {file}")
        os.remove('./data/'+file)