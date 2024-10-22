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
import random,json,pickle
import zipfile,shutil


def setup() -> tuple[webdriver.Chrome, action_chains.ActionChains]:
    """
    To start the required browser and the defined actions.

    Returns:
        tuple[webdriver.Chrome, action_chains.ActionChains]: The browser and the actions.
    """
    options=webdriver.ChromeOptions()
    if not os.path.exists('./data'):
        os.mkdir('data')
    
    path=os.getcwd()
    prefs={
        'download.default_directory':fr'{path}\data',
        'User-Agent':  r'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0  Safari/537.36',
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
    browser.set_window_size(500,1000)
    actions=action_chains.ActionChains(browser)
    return browser,actions


def login(browser: webdriver.Chrome, i:int) -> None:
    """
        log in the browser.
    Args:
        browser (webdriver.Chrome): The browser need to use.
        i (int): the account that I want to use.
    """
    # 打开登录模块并且手动登录
    browser.get('https://sketchfab.com/login')
    time.sleep(3)
    # 确定保留session级别的cookie，然后授权登录。
    accept_cookie=browser.find_element(By.ID, 'onetrust-accept-btn-handler')
    accept_cookie.click()
    emails=[
        "2915021338@qq.com",
        '1369700255@qq.com',
        '1913477858@sjtu.edu.cn',
        'zifengli@sjtu.edu.cn',
        'da1sypetals.iota@gmail.com'
    ]
    passwords=[
        "QwErTyUiOp",
        'yangziyue999',
        'wuke123456789',
        'nbb1234567',
        '123qwer321'
    ]
    # 判断是否出现会话级别cookie，判断登录是否成功。
    while len(browser.get_cookies()) <= 4:
        
        # 寻找email并且输入。
        email=browser.find_element(By.XPATH,'/html/body/main/div/div[2]/div[1]/form/div/div[2]/div[1]/input')
        email_address=emails[i]
        # email_address='1160770960@qq.com'
        for char in email_address:
                email.send_keys(char)
                time.sleep(random.randrange(1,5)/10.)
        time.sleep(random.randrange(1,10)/10.)
        # 寻找passowrd并且输入。
        password=browser.find_element(By.XPATH,'/html/body/main/div/div[2]/div[1]/form/div/div[2]/div[2]/div/div/input')
        # password_txt='kingqueen123'
        password_txt=passwords[i]
        for char in password_txt:
            password.send_keys(char)
            time.sleep(random.randrange(1,5)/10.)
        time.sleep(random.randrange(1,10)/10.)
        
        input("输入账号密码点击登录按钮后按任意键继续...")
        time.sleep(random.randrange(10,30)/10.)
        if len(browser.get_cookies()) <= 4:
            time.sleep(random.randrange(10,20)/10.)
            browser.refresh()


def check_downloaded(item: WebElement, downloaded: list[str], actions: action_chains.ActionChains) -> bool:
    """
    Check whether previously download.

    Args:
        browser (webdriver.Chrome): chrome
        downloaded (list[dir]): downloaded item.

    Returns:
        bool: True means downloaded. False means not download.
    """
    actions.scroll_to_element(item).perform()
    time.sleep(0.5)
    object_download=item.find_element(By.CLASS_NAME,'model-name__label')
    object_name=object_download.text.lower()
    file_name=object_name.replace(' ','_').replace('(','').replace(')','').replace(':','')
    file_name="".join(ch for ch in file_name if ch.isalnum() or ch=='-' or ch=='_')
    
    
    file_name+='.glb'
    return os.path.exists('./data/'+file_name)
    

def loading_pages(url: str, count: int) -> WebElement:
    """
    Loading the pages of downloading.

    Args:
        url (str): the download page.
        count (int): the current progress.

    Returns:
        WebElement: None represents not able to download.
    """
    browser.get(url)
    wait=WebDriverWait(browser,5.)
    try:
        # 一级检测：是否存在下载按钮？
        download_button=wait.until(EC.presence_of_element_located((By.CLASS_NAME,'button.btn-textified.btn-medium.c-model-actions__button.--download')))
        wait=WebDriverWait(browser,10.)
        download_button = None
        # 二级检测：尝试点击按钮进入下载页面。
        while download_button==None:
            try:
                download_button=wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'button.btn-textified.btn-medium.c-model-actions__button.--download')))
            except exceptions.TimeoutException:
                print(f"无法点击该下载链接。按任意键重试。")
                input()
                download_button = None
        return download_button
    
    except exceptions.TimeoutException:
        print(f"第{count}个文件不存在下载链接，跳过。")
        return None


def generate_descriptions(browser: webdriver.Chrome, actions: action_chains.ActionChains) -> str:
    """
    generate the descriptive text document in data.
    Args:
        browser (webdriver.Chrome): The browser window.
        actions (action_chains.ActionChains): The action chain.

    Returns:
        str: The descriptive strings of the downloaded item.
    """
    popup_container=browser.find_element(By.CLASS_NAME,'main')
    label=popup_container.find_element(By.CLASS_NAME,'model-name__label')
    object_name=label.text.lower()
    file_name=object_name.replace(' ','_').replace('(','').replace(')','').replace(':','')
    file_name="".join(ch for ch in file_name if ch.isalnum() or ch=='-' or ch=='_')
    file_name+='.txt'
    
    
    wait=WebDriverWait(popup_container,10.)
    
    
    try:
        meta_data=wait.until(EC.presence_of_element_located((By.CLASS_NAME,'c-model-metadata')))
    except Exception as e:
        print(e)
        input('Exceptions happend when generate descriptions. Press any key to restart.')
    
    actions.scroll_to_element(meta_data).perform()
    description=meta_data.find_element(By.ID,"descriptionContent")
    description=description.text
    
    tag_description='\n\n\ntags:\n'
    try:
        tags=wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,'item.tag-item')))
    except Exception as e:
        print(e)
        tags=None
    if tags==None:
        print("No tags found.")
    else:
        for tag in tags:
            tag_description+=tag.text
            tag_description+='\n'
    
    download_url:str = "\n\ndownload_link: " + browser.current_url + '\n'
    
    if not os.path.exists('./data/'+file_name):
        with open('./data/'+file_name,'a+') as f:
            f.write(description)
            f.write(tag_description)
            f.write(download_url)
        f.close()
    
    return object_name.replace(' ','_')
    
    
def wait_download(file: str, count: int) -> None:
    """
    waiting until the file completely downloaded.
    
    Args:
        file (str): The file name.
    """
    file_name="".join(ch for ch in file if ch.isalnum() or ch=='-' or ch=='_')
    print(f"等待下载第{count}个文件:{file_name}.glb")
    
    while not os.path.exists('./data/'+file_name+'.glb'):
        time.sleep(2)
        # 可以修改成替换文件描述名
        newfileName = max(os.listdir('./data'), key=lambda f: os.path.getctime(os.path.join('./data', f)))
        newfileBaseName,attribute_name = os.path.splitext(newfileName)[0],os.path.splitext(newfileName)[1]

        # 检测到glb文件，下载完成。
        if attribute_name=='.glb':
            os.rename('./data/'+file_name+'.txt','./data/'+newfileBaseName+'.txt')
            print(f"进行了名字替换。原名字:{file_name}.txt--->新名字:{newfileBaseName}.txt")
            break

        # 检测到压缩包，提取文件后下载完成。
        elif attribute_name=='.zip':
            zip_file=zipfile.ZipFile('./data/'+newfileName,'r')
            filelist=zip_file.namelist()
            zip_file.extract(filelist[0],'./data')
            os.remove('./data/'+newfileName)
            shutil.move('./data/'+filelist[0],'./data')
            os.removedirs('./data/source')
            newfileName = max(os.listdir('./data'), key=lambda f: os.path.getctime(os.path.join('./data', f)))
            newfileBaseName,attribute_name = os.path.splitext(newfileName)[0],os.path.splitext(newfileName)[1]
            os.rename('./data/'+file_name+'.txt','./data/'+newfileBaseName+'.txt')
            print(f"进行了名字替换。原名字:{file_name}.txt--->新名字:{newfileBaseName}.txt")
            break
        
        else:
            continue

    print(f"下载完成。")


# TODO
def try_downloading(button: WebElement, browser: webdriver.Chrome, count: int, actions: action_chains.ActionChains) -> None:
    """
    Try download item one by one. Also provide a simple recovery object.

    Args:
        button (WebElement): The current page download button.
        browser (webdriver.Chrome): The browser.
        count (int): Counting numbers of downloaded index.
        actions (action_chains.ActionChains): The chain of performing actions.
    """
    
    # generate description file.
    file_downloading=generate_descriptions(browser,actions)
    
    # click the download button.
    wait=WebDriverWait(browser,10.)
    button=wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'button.btn-textified.btn-medium.c-model-actions__button.--download')))
    column=wait.until(EC.presence_of_element_located((By.CLASS_NAME,'owner-wrapper')))
    actions.scroll_to_element(column).perform()
    button.click()
    time.sleep(2)
    
    # graded finding the glb document.
    wait=WebDriverWait(browser,10.)
    download_columns=wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,'AUfL6oST')))
    # Find the first proper item.
    i=0
    for col in download_columns:
        wait=WebDriverWait(col,5.)
        format=wait.until(EC.presence_of_element_located((By.CLASS_NAME,'H6stunQl'))).text
        if format[:4]=='.glb' and i!=0:
            column_selected=col
            break
        i+=1
    
    print(f"文件大小和格式:{format}")
    actions.scroll_to_element(column_selected).perform()
    wait=WebDriverWait(column_selected,10.)
    button=wait.until(EC.presence_of_element_located((By.TAG_NAME,'button')))
    button.click()
    wait_download(file_downloading,count)


def read_progress() -> tuple[int,list[str]] :
    """
    Get the current progress of download url and progress.

    Returns:
        tuple[int,list[str]]: the download progress and stored url.
    """
    if not os.path.exists('./progress'):
        os.makedirs('./progress')
    
    index_path = os.path.join('./progress','download_index.json')
    url_path = os.path.join('./progress','download_url.pkl')
    
    with open(index_path,'r') as f:
        download_index=json.load(f)
    f.close()
    
    try:
        with open(url_path,'rb') as f:
            download_url=pickle.load(f)
        f.close()
    
    except EOFError:
        download_url=None
    
    return download_index,download_url    
   
    
def save_progress(download_index: int) -> None:
    """
    To save the current progress into json.

    Args:
        download_index (int): The download index.
    """
    with open('./progress/download_index.json','w') as f:
        json.dump(download_index,f)
    f.close()


def download(browser: webdriver.Chrome, actions: action_chains.ActionChains):
    """
    The main download function handle for scrolling and item_download.

    Args:
        browser (webdriver.Chrome): browser
        actions (action_chains.ActionChains): action chains.
    """
    download_index,download_url=read_progress()
    while 1:
        download_index,download_url=read_progress()
        # Try to get downloaded. quit when all url are used.
        while download_index < len(download_url):
            try:
                for i in range(download_index+1,len(download_url)):
                    download_button = loading_pages(download_url[i],i)
                    if download_button==None: continue
                    try_downloading(download_button,browser,i,actions)
                    download_index=i
                    save_progress(download_index)
                    if len(os.listdir('./data')) >= 1000:
                        input('Downloaded 500.')
                    time.sleep(random.randint(0,15)/10)
            except Exception as e:
                print(e)
                save_progress(download_index)
                input("Exceptions happened when download. Press any key to restart.")
                
   

if __name__=='__main__':
    browser,actions=setup()
    i=int(input('Please input the account you want to use.\n'))
    login(browser,i)
    ## TODO: Specialize category download.
    download(browser,actions)