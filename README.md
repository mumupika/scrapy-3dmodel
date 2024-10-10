Turorial
===

# Requirements
using python==3.12.5.

```bash=
pip install -r requirements.txt
```

## Part 1 ChromeDriver
用谷歌chrome访问[这里](https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json)寻找对应版本/系统的谷歌驱动。

![alt text](<./1.png>)

注意勾选pretty-print。
安装完成后记得将其加入你的命令行中。（windows 添加环境变量），直到在powershell/cmd中输入chromedriver可以有输出为止。

![alt text](<./2.png>)
![alt text](<./3.png>)
![alt text](<./4.png>)
![alt text](<./5.png>)

## Part 2 爬虫

过程中请不要随意改变窗口大小，会导致页面布局和抓取元素错误QAQ

要注意登陆后等待控制台输出“请确认登录状态，按任意键继续。”后再输入密码，登录。登录完成后按任意键。

## TODO:
    Recovery from StaleElementRefrence at any time.
    Bad Network Connection.
    Store in Json.
    
