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

def get_contents(browser: webdriver.Chrome, actions: action_chains.ActionChains, download_url:list[str], needed:int) -> list[str]:
    """
    To get the load_more button and get the download url.
    
    Args:
        browser (webdriver.Chrome): chrome window.
        actions (action_chains.ActionChains): action_chain.

    Returns:
        list[str]: The download_urls.
    """
    scrolling = 0.
    while len(download_url) < needed:
        # scroll to the bottom of the page.
        try:
            download_url=[]
            height=float(browser.execute_script(("return document.body.scrollHeight")))
            while scrolling < height:
                height=browser.execute_script(("return document.body.scrollHeight"))
                browser.execute_script(f"window.scrollBy(0,2500)")  
                scrolling += 2500
                time.sleep(2)

            # Get the contents of all the download page url.
            contents = browser.find_element(By.CLASS_NAME,'content')
            # wait explicitly.
            wait=WebDriverWait(contents,10.)
            items = wait.until(EC.presence_of_element_located((By.XPATH,'div[3]/div/div/div/div[1]')))
            item_list=items.find_elements(By.CLASS_NAME,"c-grid__item.item")
            # extract the url from the item.
            for i in item_list:
                url=i.find_element(By.CLASS_NAME,'card.card-model.pw_M_MRp').find_element(By.CLASS_NAME,'card__main.card-model__thumbnail').find_element(By.TAG_NAME,'a').get_attribute('href')
                download_url.append(url)
            
            button_block=wait.until(EC.presence_of_element_located((By.CLASS_NAME,'c-grid__button.--next')))
            wait=WebDriverWait(button_block,10.)
            button=wait.until(EC.element_to_be_clickable((By.TAG_NAME,'button')))
            actions.scroll_to_element(button).perform()
            scrolling = height
            button.click()
            time.sleep(2)
            
            
        except Exception as e:
            print(e)
            input("Get contents error. press key to restart.")
    
    # save the urls into the pkl document.
    with open('./progress/download_url.pkl','wb') as f:
        pickle.dump(download_url,f)
    f.close()
    print(f"The url fetched:{len(download_url)}")
    return download_url

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
        
        # 寻找email并且输入。
        email=browser.find_element(By.XPATH,'/html/body/main/div/div[2]/div[1]/form/div/div[2]/div[1]/input')
        email_address='the.bird@sjtu.edu.cn'
        for char in email_address:
                email.send_keys(char)
                time.sleep(random.randrange(1,5)/10.)
        time.sleep(random.randrange(1,10)/10.)
        # 寻找passowrd并且输入。
        password=browser.find_element(By.XPATH,'/html/body/main/div/div[2]/div[1]/form/div/div[2]/div[2]/div/div/input')
        password_txt='open771013'
        for char in password_txt:
            password.send_keys(char)
            time.sleep(random.randrange(1,5)/10.)
        time.sleep(random.randrange(1,10)/10.)
        
        input("输入账号密码点击登录按钮后按任意键继续...")
        time.sleep(random.randrange(10,30)/10.)
        if len(browser.get_cookies()) <= 4:
            time.sleep(random.randrange(10,20)/10.)
            browser.refresh()

def preparation_check(needed: int) -> tuple[list[str],bool]:
    """
    Check whether preparation needed.

    Args:
        needed (int): The number of url to fetch.

    Returns:
        tuple[list[str],bool]: return the download url and the bool flag.
    """
    if not os.path.exists('./progress'):
        os.makedirs('./progress')
        url_path = os.path.join('./progress','download_url.pkl')
        download_url=['a']
        with open(url_path,'wb') as f:
            pickle.dump(download_url,f)
        f.close()
        return None,False
    
    elif not os.path.exists('./progress/download_url.pkl'):
        url_path = os.path.join('./progress','download_url.pkl')
        download_url=['a']
        with open(url_path,'wb') as f:
            pickle.dump(download_url,f)
        f.close()
        return None,False

    else:
        url_path = os.path.join('./progress','download_url.pkl')
        with open(url_path,'rb') as f:
            download_url=pickle.load(f)
        f.close()
        if len(download_url) <= needed:
            return download_url,False
        else:
            return download_url,True

def clear_history() -> None:
    """
        To clear the historical download_url data.
    """
    download_url=[]
    with open('./progress/download_url.pkl','wb') as f:
        pickle.dump(download_url,f)
    f.close()
    print("History cleared.")
    
if __name__=='__main__':
    browser,actions=setup()
    login(browser)
    ## TODO: Specialize category download.
    url=str(input('Please paste the sketchfab site that you want to scrap.\n'))
    browser.get(url=url)
    needed=int(input('Please input the value you want to scrap.(They may not be all avalable)\n'))
    download_url,flag=preparation_check(needed)
    if not flag:
        download_url=get_contents(browser,actions,download_url,needed)
    else:
        choice=int(input("If you want to scrap new site, press 0 to reload the download_url.\n"))
        if choice==0:
            url=str(input('Please paste the sketchfab site that you want to scrap.\n'))
            browser.get(url=url)
            needed=int(input('Please input the value you want to scrap.(They may not be all avalable)\n'))
            clear_history()
            download_url=[]
            download_url=get_contents(browser,actions,download_url,needed)