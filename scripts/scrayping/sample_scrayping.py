from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_binary

# headlessモード
option = Options()
option.add_argument('--headless')
driver = webdriver.Chrome(options=option)

# Googleのトップページにアクセスしてbs4でパース
url = "https://google.com"
driver.get(url)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# 出力
ll = filter(lambda x: len(x) > 0, soup.text.split(" "))
for elem in ll:
    print(elem)
