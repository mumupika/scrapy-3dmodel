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
    if not os.path.exists('./data'):
        os.mkdir('data')
    
    path=os.getcwd()
    prefs={
        'download.default_directory':path+r'/data',
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
    browser.set_window_size(500,867)
    actions=action_chains.ActionChains(browser)
    return browser,actions






def login(browser: webdriver.Chrome) -> None:
    """
        log in the browser.
    Args:
        browser (webdriver.Chrome): The browser need to use.
    """
    # 打开登录模块并且手动登录
    browser.get('https://sketchfab.com/login')
    time.sleep(3)
    # 确定保留session级别的cookie，然后授权登录。
    accept_cookie=browser.find_element(By.ID, 'onetrust-accept-btn-handler')
    accept_cookie.click()
    # 判断是否出现会话级别cookie，判断登录是否成功。
    while len(browser.get_cookies()) <= 4:
        
        # # 寻找email并且输入。
        # email=browser.find_element(By.XPATH,'/html/body/main/div/div[2]/div[1]/form/div/div[2]/div[1]/input')
        # email_address='the.bird@sjtu.edu.cn'
        # for char in email_address:
        #         email.send_keys(char)
        #         time.sleep(random.randrange(1,5)/10.)
        # time.sleep(random.randrange(1,10)/10.)
        # # 寻找passowrd并且输入。
        # password=browser.find_element(By.XPATH,'/html/body/main/div/div[2]/div[1]/form/div/div[2]/div[2]/div/div/input')
        # password_txt='open771013'
        # for char in password_txt:
        #     password.send_keys(char)
        #     time.sleep(random.randrange(1,5)/10.)
        # time.sleep(random.randrange(1,10)/10.)
        
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
    
    





def scroll_to_bottom(browser: webdriver.Chrome,actions: action_chains.ActionChains, scrolling: float) -> float:
    """
    scroll to the bottom of the page.
    
    Args:
        browser (webdriver.Chrome): browser.
        actions (action_chains.ActionChains): action chain class.
        scrolling (float): current scrolling distance.
    
    return:
        scrolling-2000 (float): The last scrolling height.
    """
    height=float(browser.execute_script(("return document.body.scrollHeight")))
    while scrolling < height:
        height=browser.execute_script(("return document.body.scrollHeight"))
        browser.execute_script(f"window.scrollBy(0,2500)")  
        scrolling += 2500
        time.sleep(1.5)
    return height-2000




# TODO
def get_contents(browser: webdriver.Chrome,actions: action_chains.ActionChains, scrolling: float) -> tuple[WebElement,list[WebElement],float]:
    """
    To get the load_more button and the items.
    
    Args:
        browser (webdriver.Chrome): chrome window.
        actions (action_chains.ActionChains): action_chain.

    Returns:
        tuple[WebElement,list]: WebElement for the load more button, list for download items.
    """
    contents=browser.find_element(By.CLASS_NAME,'content')
    scrolling=scroll_to_bottom(browser,actions,scrolling)
    # 增加显式等待。
    wait = WebDriverWait(contents,10.)
    button_block=wait.until(EC.presence_of_element_located((By.XPATH,'div[3]/div/div/div/div[2]')))
    items = wait.until(EC.presence_of_element_located((By.XPATH,'div[3]/div/div/div/div[1]')))
    item_list=items.find_elements(By.CLASS_NAME,"c-grid__item.item")
    return button_block,item_list,scrolling





def loading_pages(item: WebElement, count: int) -> WebElement:
    """
    Loading the pages of downloading.

    Args:
        item (WebElement): _description_
        count (int): _description_

    Returns:
        WebElement: _description_
    """
    wait=WebDriverWait(item,5.)
    try:
        download_page=wait.until(EC.presence_of_element_located((By.CLASS_NAME,'help.card-model__feature.--downloads')))
    except exceptions.TimeoutException as e:
        time.sleep(3)
        try:
            item.find_element(By.CLASS_NAME,'help.card-model__feature.--downloads')
        except exceptions.NoSuchElementException:
            print(f"第{count}个文件页面不存在下载链接，跳过。")
            return None
    
    return download_page





# TODO: generate the descriptive text document in data.
def generate_descriptions(browser: webdriver.Chrome, actions: action_chains.ActionChains) -> str:
    """
    generate the descriptive text document in data.
    Args:
        browser (webdriver.Chrome): The browser window.
        actions (action_chains.ActionChains): The action chain.

    Returns:
        str: The descriptive strings of the downloaded item.
    """
    popup_container=browser.find_element(By.CLASS_NAME,'popup-container')
    label=popup_container.find_element(By.CLASS_NAME,'model-name__label')
    object_name=label.text.lower()
    file_name=object_name.replace(' ','_').replace('(','').replace(')','').replace(':','')
    file_name="".join(ch for ch in file_name if ch.isalnum() or ch=='-' or ch=='_')
    
    
    file_name+='.txt'
    
    wait=WebDriverWait(popup_container,10.)
    mata_data=None
    
    
    try:
        meta_data=wait.until(EC.presence_of_element_located((By.CLASS_NAME,'c-model-metadata')))
    except Exception as e:
        print(e)
        input('Exceptions happend. Press any key to restart.')
    
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
    
    if not os.path.exists('./data/'+file_name):
        with open('./data/'+file_name,'a+') as f:
            f.write(description)
            f.write(tag_description)
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
    waiting_time=0
    while not os.path.exists('./data/'+file_name+'.glb'):
        time.sleep(1)
        waiting_time+=1
        if waiting_time>=60:
            # 可以修改成替换文件描述名
            newfileName = max(os.listdir('./data'), key=lambda f: os.path.getctime(os.path.join('./data', f)))
            newfileBaseName = os.path.splitext(newfileName)[0]
            os.rename('./data/'+file_name+'.txt','./data/'+newfileBaseName+'.txt')
            print(f"进行了名字替换。原名字:{file_name}.txt--->新名字:{newfileBaseName}.txt")
            file_name=newfileBaseName
            if os.path.exists('./data/'+file_name+'.glb'): break
    print(f"下载完成。")

      
def try_downloading(page: WebElement, browser: webdriver.Chrome, count: int, actions: action_chains.ActionChains) -> None:
    """
    Try download item one by one. Also provide a simple recovery object.

    Args:
        page (WebElement): The current page.
        browser (webdriver.Chrome): The browser.
        count (int): Counting numbers of downloaded index.
        actions (action_chains.ActionChains): The chain of performing actions.
    """
    actions.scroll_to_element(page).perform()
    page.click()
    time.sleep(3)
    wait=WebDriverWait(browser,15.)
    close=wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'c-popup__close')))
    close.click()
    time.sleep(3)
    
    try:
        download_button=wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'button.btn-textified.btn-medium.c-model-actions__button.--download')))
    except exceptions.NoSuchElementException:
        print(f"第{count}个元素不存在下载链接，跳过...")
        return
    
    # generate description file.
    file_downloading=generate_descriptions(browser,actions)
    
    # click the download button.
    actions.scroll_to_element(download_button).perform()
    download_button.click()
    time.sleep(3)
    
    # find all download links.
    wait=WebDriverWait(browser,10)
    glb_col=wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,'AUfL6oST')))
    actions.scroll_to_element(glb_col[3]).perform()
    time.sleep(1)
    
    # find the first downloadable glb file.
    wait=WebDriverWait(glb_col[3],10)
    button_glb=wait.until(EC.element_to_be_clickable((By.TAG_NAME,'button')))
    actions.scroll_to_element(button_glb).perform()
    button_glb.click()
    
    # find the pop-up close button.
    wait_download(file_downloading,count)
    wait=WebDriverWait(browser,10.)
    close=wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'c-popup__close')))
    close.click()
    time.sleep(1)
    
    # return to the former page.
    wait=WebDriverWait(browser,10)
    close=wait.until(EC.element_to_be_clickable((By.CLASS_NAME,'c-model-page-popup__close.fa-regular.fa-times')))
    close.click()
    time.sleep(1)
            

def download(browser: webdriver.Chrome, actions: action_chains.ActionChains):
    """
    The main download function handle for scrolling and item_download.

    Args:
        browser (webdriver.Chrome): browser
        actions (action_chains.ActionChains): action chains.
    """
    item_downloaded_list=os.listdir('./data')
    browser.get("https://sketchfab.com/3d-models/categories/animals-pets?features=downloadable&sort_by=-likeCount")
    scrolling=0.
    item_downloaded_index=1352
    # 1070
    while len(item_downloaded_list)//2 < 10000:
        try:
            load_more_button,item_list,scrolling=get_contents(browser,actions,scrolling)
            
            for i in range(item_downloaded_index+1,len(item_list)):
                if check_downloaded(item_list[i],item_downloaded_list,actions): continue
                download_page=loading_pages(item_list[i],i)
                if download_page==None: continue    # 不存在链接，跳过。
                try_downloading(download_page,browser,i,actions)
                item_downloaded_index=i
                
            
            actions.scroll_to_element(load_more_button).perform()
            load_more_button.click()
            time.sleep(1)
        except Exception as e:
            print(e)
            input("Exceptions happened. Press any key to restart.")
            browser.get("https://sketchfab.com/3d-models/categories/animals-pets?features=downloadable&sort_by=-likeCount")
            scrolling=0.



if __name__=='__main__':
    browser,actions=setup()
    login(browser)
    ## TODO: Specialize category download.
    download(browser,actions)