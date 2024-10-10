from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common import action_chains
from selenium.common import exceptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import random


def setup() -> tuple[webdriver.Chrome, action_chains.ActionChains]:
    """
    To start the required browser and the defined actions.

    Returns:
        tuple[webdriver.Chrome, action_chains.ActionChains]: The browser and the actions.
    """
    options=webdriver.ChromeOptions()
    if not os.path.exists('./data2'):
        os.mkdir('data2')
    
    path=os.getcwd()
    prefs={
        'download.default_directory':path+r'/data2',
        'User-Agent': r'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        "profile.managed_default_content_settings.images": 2,
        'permissions.default.stylesheet':2,
        'blink-settings':'imagesEnabled=false',
        'disable-media-session-api':'true',
        'headless':'new',
        'download_restrictions': 0,
        'safebrowsing.enabled': False,
    }
    options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs',prefs)  # agent and the saving directory.
    browser=webdriver.Chrome(options=options)
    browser.set_window_size(800,867)
    actions=action_chains.ActionChains(browser)
    return browser,actions



def login(browser: webdriver.Chrome) -> None:
    """
    登录模型网站。位于国内的网站呢!
    Args:
        browser (webdriver.Chrome): 当前浏览器界面。
    """
    browser.get("https://login.cgmodel.com/")
    # 直接扫码登录无需进行cookie的允许。
    input('登录完成后按任意键继续。')

def choose_download() -> str:
    """
    进行选择下载。

    Returns:
        str: 返回需要进行下载的url。
    """
    print("输入对应的数字进行下载。\n1-动物obj,2-植物obj,3-动物fbx,4-植物fbx")
    choice=int(input())
    urls=[
        "https://www.cgmodel.com/model/dw/?format=OBJ(.obj/.mtl)&free=1&order=time",
        "https://www.cgmodel.com/model/stzw/?format=OBJ(.obj/.mtl)&free=1&order=time",
        "https://www.cgmodel.com/model/dw/?format=FBX(.fbx)&free=1&order=time",
        "https://www.cgmodel.com/model/stzw/?format=FBX(.fbx)&free=1&order=time"
    ]
    return urls[choice-1]


def prepare_download_urls(url:str, browser: webdriver.Chrome) -> list[str]:
    """
    获得需要进入的下载页面的全部下载地址。

    Args:
        url (str): 选择下载的种类的综述网址。
        browser (webdriver.Chrome): 浏览器视窗界面。

    Returns:
        list[str]: 需要下载的有关url界面。
    """
    browser.get(url)
    
    while 1:
        try:
            wait=WebDriverWait(browser,5)
            page=wait.until(EC.presence_of_element_located((By.CLASS_NAME,"page")))
            wait=WebDriverWait(page,5)
            page=wait.until(EC.presence_of_all_elements_located((By.TAG_NAME,'li')))
            page=len(page)
            all_urls=list()
            for i in range(page):
                browser.get(f"https://www.cgmodel.com/model/dw/?format=OBJ(.obj/.mtl)&free=1&order=time&page={i+1}")
                wait=WebDriverWait(browser,5)
                contents=wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,'model-list-con')))
                urls=[con.find_element(By.CLASS_NAME,'model-list-card').find_element(By.CLASS_NAME,'position-relative').find_element(By.TAG_NAME,'a').get_attribute('href') for con in contents]
                for url in urls:
                    all_urls.append(url)
            return all_urls
        except Exception as e:
            print(e)
            key=input("press any key except d to continue...")
            if key=='d':
                exit(-1)

def generate_descriptions(browser: webdriver.Chrome) -> str:
    """
    生成模型描述性文本。
    Args:
        browser (webdriver.Chrome): 浏览器视窗。

    Returns:
        str: 描述性文本未来写入到文件中。
    """
    description="模型描述:\n"
    
    try:
        describe_section=browser.find_element(By.CLASS_NAME,'model_explain').text
    except exceptions.NoSuchElementException:
        describe_section="无模型描述"
    
    description+=describe_section
    description+="\n\n分类:\n"
    
    try:
        classification=browser.find_element(By.CLASS_NAME,'flex-row.model-label-box.mt10 ').text
    except exceptions.NoSuchElementException:
        classification="无分类信息"
    
    description+=classification
    description+="\n\n关键词:\n"
    
    try:
        label=browser.find_element(By.CLASS_NAME,'model-label-box.mt5  ').find_element(By.CLASS_NAME,'flex-row').find_element(By.CLASS_NAME,'flex-wrap').text
    except exceptions.NoSuchElementException:
        label="无标签信息"
    
    description+=label
    return description

def wait_download(browser:webdriver.Chrome, actions:action_chains.ActionChains, count:int, description:str) -> None:
    """
    下载并生成描述性文件。
    
    Args:
        browser (webdriver.Chrome): 浏览器视窗
        actions (action_chains.ActionChains): 动作链条
        count (int): 下载序号。
        description (str): 描述性文本。
    """
    wait=WebDriverWait(browser,5)
    download_boxes=wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,'download_box.pr')))
    element_selected=None
    for element in download_boxes:
        typeOfObject=element.find_element(By.CLASS_NAME,'zc.word-break').text
        if typeOfObject[:3]=='FBX' or typeOfObject[:3]=='OBJ':
            element_selected:WebElement = element
            break
    if element_selected==None:
        print(f"第{count}没有符合类型的文件，跳过...")
        return
    
    # 选定下载部分。
    wait=WebDriverWait(element_selected,5)
    tick=wait.until(EC.element_to_be_clickable((By.TAG_NAME,'label')))
    tick.click()
    
    # 获取下载文件名字。
    filename:str = tick.get_attribute('data-name')
    if os.path.exists("./data2/"+filename):
        print(f"已下载过第{count+1}个文件{filename}.")
        return
    fileBaseName = os.path.splitext(filename)[0]
    with open('./data2/'+fileBaseName+'.txt','a+') as f:
        f.write(description)
    f.close()
    
    download=browser.find_element(By.CLASS_NAME,'download_tips')
    button=download.find_element(By.TAG_NAME,'input')
    button.click()
    print(f"开始下载第{count+1}个文件:{filename}")
    while not os.path.exists('./data2/'+filename):
        time.sleep(1)
    


def download_items(links:list[str], browser:webdriver.Chrome, actions:action_chains.ActionChains) -> None:
    """
    下载所有的物品。
    
    Args:
        links (list[str]): 下载的url。
        browser (webdriver.Chrome): 浏览器视窗。
        actions (action_chains.ActionChains): 动作链条类型。
    """
    count=0
    while count < len(links):
        try:
            browser.get(links[count])
            # 生成描述性文本。
            description=generate_descriptions(browser)
            # 准备下载。
            wait=WebDriverWait(browser,5)
            button_section=wait.until(EC.presence_of_element_located((By.CLASS_NAME,'align-center.model-purchase-btns')))
            wait=WebDriverWait(button_section,5)
            button=wait.until(EC.element_to_be_clickable((By.TAG_NAME,'button')))
            actions.scroll_to_element(button).perform()
            button.click()
            # 准备开始下载。
            wait_download(browser,actions,count,description)
            count+=1
            
        except Exception as e:
            print(e)
            input("press any key to continue...")
            
if __name__=='__main__':
    browser,actions=setup()
    login(browser)
    url=choose_download()
    download_links=prepare_download_urls(url,browser)
    download_items(download_links,browser,actions)