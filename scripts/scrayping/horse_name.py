#2022年分
import requests
from bs4 import BeautifulSoup
import time
import tqdm

# https://race.netkeiba.com/race/shutuba.html?race_id=202205040102　で推論したい日付を選択して12レース分の馬名を取得
assume_id = 2022050402
houseInfo = []

for i in tqdm.tqdm(range(1,13,1)):
    if i < 10:
        index = "0" +  str(i)
    else:
        index = i
    assume_url = "https://race.netkeiba.com/race/shutuba.html?race_id="+ str(assume_id)+ str(index)
    r=requests.get(assume_url)
    soup = BeautifulSoup(r.content.decode("euc-jp", "ignore"), "html.parser")#バグ対策でdecode
    soup_span = soup.find_all("span")
    allnum=(len(soup_span)-6)/3#馬の数
    allnum=int(allnum)
    horse_name = []

    for n in range(allnum):#レース12
        soup_txt_l = 0
        #馬の情報
        try:
            soup_txt_l=soup.find_all("span",class_='HorseName')[n].contents[0].contents[0]
            horse_name.append(str(soup_txt_l))
        except:
            pass

        print(soup_txt_l)
        name=[]#馬の名前
        # for num in range(allnum):
        #     name.append(soup_txt_l[4*num].contents[1].contents[0])
        time.sleep(0.01)#サーバーの負荷を減らすため1秒待機する
    houseInfo.append(horse_name)



import csv
with open('/mnt/c/Users/hayat/Desktop/keiba_analysis/race_horse_name/'+str(assume_id)+'.csv', 'w', newline='',encoding='shift_jis') as f:
    csv.writer(f).writerows(houseInfo)
print("終了")


#pandas.read_csv("2022-09-30-10.csv",encoding='shift_jis',header=None)