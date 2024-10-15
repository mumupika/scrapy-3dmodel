from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common import action_chains
from selenium.common import exceptions
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
import random


def Windows_setup(web ='https://sketchfab.com/login',data = 'data') -> tuple[webdriver.Chrome, action_chains.ActionChains]:
    """
    To start the required browser and the defined actions.
    Input:
        string: the name of this setup
    
    Returns:
        tuple[webdriver.Chrome, action_chains.ActionChains]: The browser and the actions.
    """
    options=webdriver.ChromeOptions()
    if not os.path.exists(f'./{data}'):
        os.mkdir(f'{data}')
    
    path=os.getcwd()
    prefs={
        'download.default_directory':fr'{path}\{data}',
        'User-Agent':  r'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0  Safari/537.36',
        #"profile.managed_default_content_settings.images": 2,
        'permissions.default.stylesheet':2,
        'blink-settings':'imagesEnabled=false',
        'disable-media-session-api':'true',
        'headless':'new',
        'download_restrictions': 0,
        'safebrowsing.enabled': False,
    }
    
    options.add_argument('--disable-gpu')
    options.add_experimental_option('prefs',prefs) 
    browser=webdriver.Chrome(options=options)
    browser.set_window_size(500,800)
    actions=action_chains.ActionChains(browser)
    
    browser.get(web)
    time.sleep(2)
    while len(browser.get_cookies()) <= 4:
        input("输入账号密码点击登录按钮后按任意键继续...")
        if len(browser.get_cookies()) <= 4:
            time.sleep(2)
            browser.refresh()
    
    return browser,actions


def prepare_download_urls(browser: webdriver.Chrome, actions:action_chains.ActionChains) -> list[str]:
    """
    获得需要进入的下载页面的全部下载地址。

    Args:
        browser (webdriver.Chrome): 浏览器视窗界面。
        actions (action_chains.ActionChains)
    Returns:
        list[str]: 需要下载的有关url界面。
    """

    try:
        wait=WebDriverWait(browser,5)
        page = wait.until(EC.presence_of_element_located((By.CLASS_NAME,'search-results')))
        all_urls=list()
        cont = page.find_elements(By.TAG_NAME,'li')
        urls=[con.find_element(By.TAG_NAME,'a').get_attribute('href') for con in cont]
        for url in urls:
            all_urls.append(url)
        return all_urls
    except Exception as e:
        print(e)
        

def generate_descriptions(browser: webdriver.Chrome) -> str:
    """
    生成模型描述性文本。
    Args:
        browser (webdriver.Chrome): 浏览器视窗。

    Returns:
        str: 描述性文本,未来写入到文件中。
    """
    browser_text = browser.find_element(By.ID, 'edanDetails')
    
    description="Description:\n"
    try:
        describe_section=browser_text.find_element(By.CLASS_NAME,'field-freetextnotes').text
    except exceptions.NoSuchElementException:
        describe_section="\n"
    description+=describe_section
    
    description+="\n\n"
    try:
        cname=browser_text.find_element(By.CLASS_NAME,'field-freetexttaxonomicname').text
    except exceptions.NoSuchElementException:
        cname="\n"
    description+=cname
    
    description+="\n\n"
    try:
        classification=browser_text.find_element(By.CLASS_NAME,'field-freetexttopic').text
    except exceptions.NoSuchElementException:
        classification="\n"
    description+=classification
    
    description+="\n\n"
    try:
        source=browser_text.find_element(By.CLASS_NAME,'field-freetextdatasource').text
    except exceptions.NoSuchElementException:
        source="\n"
    description+=source
    
    return description


def wait_download(href, browser:webdriver.Chrome, count:int, description:str, data_path:str) -> None:
    """
    下载并生成描述性文件。
    
    Args:
        href
        browser (webdriver.Chrome): 浏览器视窗
        count (int): 下载序号
        description (str): 描述性文本
        data_path
    """
    

    filename:str = href.split('/')[-1]
    if os.path.exists(f"./{data_path}/{filename}"):
        print(f"已下载过第{count+1}个文件{filename}.")
        return
    
    fileBaseName = os.path.splitext(filename)[0]
    with open(f'./{data_path}/{fileBaseName}.txt','a+') as f:
        f.write(description)
    f.close()
    
    browser.get(href)
    print(f"开始下载第{count+1}个文件:{filename}")
    while not os.path.exists(f"./{data_path}/{filename}"):
        time.sleep(1)
    print('下载完成')
        

def download_items(links:list[str], browser:webdriver.Chrome, actions:action_chains.ActionChains,data_path:str) -> None:
    """
    下载所有的物品。
    
    Args:
        links (list[str]): 下载的url。
        browser (webdriver.Chrome): 浏览器视窗。
        actions (action_chains.ActionChains): 动作链条类型。
        data_path
    """
    count=0
    while count < len(links):
        try:
            browser.get(links[count])
            # 生成描述性文本。
            description=generate_descriptions(browser)

            # 准备下载。
            wait=WebDriverWait(browser,5)
            button=wait.until(EC.element_to_be_clickable((By.ID,'heading-tab-download')))
            actions.scroll_to_element(button).perform()
            button.click()
            time.sleep(0.5)

            id = button.get_attribute('aria-describedby')
            x1 = browser.find_element(By.ID, id)
            x2 = x1.find_elements(By.TAG_NAME,'a')
            for x3 in x2:
                href = x3.get_attribute('href')
                if href.endswith('.glb'):
                    # 开始下载
                    wait_download(href,browser,count,description,data_path)
                    break
            count+=1
            
        except Exception as e:
            print(e)
            input("press any key to continue...")



if __name__ == 'main':
    web =[
        'https://3d.si.edu/collections/future-of-orchids',
        'https://3d.si.edu/collections/freshwater-mussels',
        'https://3d.si.edu/corals'
        
    ]
    data_path = '3d_data_shell'
    browser,actions=Windows_setup(web[1], data_path)
    download_links=prepare_download_urls(browser,actions)
    download_items(download_links,browser,actions,data_path)