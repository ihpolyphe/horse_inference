#2022年分
import requests
from bs4 import BeautifulSoup
import time
import tqdm
import pandas as pd
import os
from scrayping_class import Results, HorseResults, Peds, jockeyResults

"""
指定したpage idにおけるレースごとの馬情報をスクレイピングする。(horse name と同じidを設定すること)
以下のURLにおけるidを指定する。下二けたはレース番号のため、省略してassume_idに設定する。
"""
assume_id = "2024060508"


def get_horse_info(column,assume_url,index):
    # dynamic = False
    # if dynamic:
    #     print("start dynamic scrayping")
    #     # Chromeのオプションを設定
    #     chrome_options = webdriver.ChromeOptions()
    #     chrome_options.add_argument("--headless")  # ヘッドレスモード
    #     chrome_options.add_argument("--no-sandbox")
    #     # chrome_options.add_argument("--disable-dev-shm-usage")
    #     # chrome_options.add_argument("--disable-gpu")
    #     # chrome_options.add_argument("--remote-debugging-port=9222")
    #     # chrome_options.binary_location = "/mnt/c/Users/hayat/Downloads/chromedriver-linux64/chromedriver"
    #     # chrome_options.binary_location = '/usr/bin/chromium-browser'
    #     # SeleniumのWebDriverを設定
    #     # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    #     driver = webdriver.Chrome(options=chrome_options)
    #     # タイムアウトを設定
    #     # driver.set_page_load_timeout(120)

    #     try:
    #         # 目的のURLにアクセス
    #         driver.get(assume_url)

    #         # ページが完全に読み込まれるまで待機
    #         import time
    #         time.sleep(5)
    #         print(driver)
    #         # オッズ情報を取得
    #         odds_elements = driver.find_elements(By.CSS_SELECTOR, ".Txt_R.Popular span")
    #         odds = [element.text for element in odds_elements]

    #         # 結果を表示
    #         for i, odd in enumerate(odds):
    #             print(f"オッズ {i+1}: {odd}")

    #     finally:
    #         # ブラウザを閉じる
    #         driver.quit()
    #     print("end dynamic scrayping")



    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    r=requests.get(assume_url,headers=headers)
    soup = BeautifulSoup(r.content.decode("euc-jp", "ignore"), "html.parser")#バグ対策でdecode
    soup_span = soup.find_all("span")
    allnum=(len(soup_span)-6)/3#馬の数
    allnum=int(allnum)
    horse = []
    horse_name_list = []
    # レースごとに同じ情報
    data1=soup.find_all("div",class_='RaceData01')[0].contents[2].contents[0] #芝かダートか障害物か
    condition = data1[1:2]
    distance=int(data1[2:(len(data1)-1)])  # strから抽出　距離
    #<h1 class="RaceName">2歳未勝利から2歳未勝利をclass_に取得
    class_=soup.find_all("h1",class_='RaceName')[0].contents[0]
    # class_の改行コードを削除する
    class_ = class_.replace("\n", "")
    # print(soup.find_all("div",class_='RaceData02')[0])
    # class_=soup.find_all("div",class_='RaceData02')[0].contents[9].contents[0] #未勝利か、2歳か、G1か
    number_of_horse_str=soup.find_all("div",class_='RaceData02')[0].contents[15].contents[0] # 頭数
    number_of_horse_=int(number_of_horse_str[:(len(number_of_horse_str)-1)])

    #以下の情報を取得して、4回中京２日目をplaceに格納する
    # <div class="RaceData02">  
    # <span>4回</span>
    # <span>中京</span>
    # <span>2日目</span>
    place = soup.find_all("div", class_='RaceData02')[0].contents[3].contents[0] + soup.find_all("div", class_='RaceData02')[0].contents[5].contents[0]

    race_data_list = []
    count = 0
    for n in range(allnum): #:馬番号
        soup_txt_l = 0
        horse_weight = 0
        #馬の情報
        try:
            horse_name=soup.find_all("span",class_='HorseName')[n].contents[0].contents[0]
            count+=1
        except AttributeError:
            print("馬名取得失敗 AttributeError continue")
            continue
        except IndexError:
            print("馬名取得失敗 IndexError continue")
            continue
        # 馬のIDを取得する
        try:
            horse_id = soup.find("span", class_="HorseName").find("a")['href'].split('/')[-1]
        except AttributeError:
            print("馬ID取得失敗 AttributeError continue")
            continue
        except IndexError:
            print("馬ID取得失敗 IndexError continue")
            continue

        try:
            yaer_sex = soup.find_all("td", class_='Barei Txt_C')[n - 1].contents[0]
            year = int(yaer_sex[1:])
        except IndexError:
            print(f"年齢と性別の取得失敗 IndexError: n={n} continue")
            continue
        try:
            weight=float(soup.select('td[class="Txt_C"]')[n-1].contents[0])
        except ValueError:
            weight = None
        try:
            jokey=soup.select('td[class="Jockey"]')[n-1].contents[1].contents[0]
        except IndexError:  
            print("騎手取得失敗 IndexError continue")
            jokey = "騎手不明"
        # 騎手IDを取得する
        try:
            jokey_id = soup.select('td[class="Jockey"]')[n-1].contents[1].get('href')
            jokey_id = jokey_id.split("/")[-2]
        except AttributeError:
            print("騎手ID取得失敗 AttributeError continue")
            continue
        except IndexError:
            print("騎手ID取得失敗 IndexError continue")
            continue

        # 以下の情報からジョッキーの体重を取得する
        # <td class="Barei Txt_C">牡2</td>
        # <td class="Txt_C">54.0</td>
        # <td class="Jockey">
        # <a  href="https://db.netkeiba.com/jockey/result/recent/01187/" target="_blank" title="永島">◇永島</a>
        jokey_weight = soup.select('td[class="Txt_C"]')[n-1].contents[0]

        # horse_weight_str=soup.select('td[class="Weight"]')[n-1].contents[0]  #馬体重は記載されていないので固定値500
        # horse_weight = int(horse_weight_str.strip())
        # horse_weight=soup.find_all("td",class_='Weight')[n].contents[0]
        horse_weight = 500
        # horse_weight_change=soup.select('td[class="Weight"]')[n-1].contents[1].contents[0]
        # horse_weight_change = horse_weight_change.lstrip("(")
        # horse_weight_change = horse_weight_change.rstrip(")")
        # horse_weight_change_data = int(horse_weight_change,10)
        horse_weight_change_data = 6
        sex_ = yaer_sex[:1]



        odds_list_in_race = None
        # horse_list = [horse_name,n,year,sex_,horse_weight,horse_weight_change_data,weight,class_,number_of_horse_,distance,condition,jokey,win_rate,rentairitu,hukusyouritu]
        # horse.append(horse_list)
        # horse_name_list.append(horse_name)

        race_data = [horse_name, 
                    count,
                     year,
                     sex_,
                     horse_weight,
                    horse_weight_change_data,
                    jokey_weight,
                    jokey,
                    horse_id,
                    jokey_id,
                    None,  # odds
                    None, ## goal_number
        ]
    
        race_common_data = [
                str(None) ,
                str(class_),
                str(place),
                class_,
                number_of_horse_,
                distance ,
                condition,
        ]
        race_common_data += race_data
        race_data_list.append(race_common_data)


    # columnを作成
    column_list = []
    race_comon_column = [
                        "date",
                        "race_name",
                        "place",
                        "class_list_in_race",
                        "number_of_horses",
                        "distance",
                        "condition"
                        ]
    column = ["horse_name", "umaban", "horse_age", "horse_sex","horse_weight",
                    "weight_change","handi",
                    "jocky","horse_id","jokey_id","odds","goal_number"]
    column_list = race_comon_column + column 
    # print(len(column_list))
    # print(column_list)
    # print(len(race_common_data))
    # race_common_dataを2次元リストに変換
    # race_common_data = [race_common_data]
    one_race_horse_data = pd.DataFrame(race_data_list, columns=column_list)

    # horse_idのリストを入力にHorseResultsクラスから馬情報をスクレイピングする
    horse_id_list = one_race_horse_data["horse_id"].values
    print(horse_id_list)
    horse_results = HorseResults()
    horse_results_df = horse_results.scrayping(horse_id_list)

    # jokey_idのリストを入力にjockeyResultsクラスから騎手情報をスクレイピングする
    jokey_id_list = one_race_horse_data["jokey_id"].values
    print(jokey_id_list)
    jockey_results = jockeyResults()
    jockey_results_df = jockey_results.scrayping(jokey_id_list)

    # データフレームを結合する
    one_race_horse_data = pd.concat(one_race_horse_data, horse_results_df, jockey_results_df)

    # データフレームをCSVに書き出し
    one_race_horse_data.to_csv(path+"/inference_data_"+str(assume_id)+str(index) +".csv")



def isint(s):  # 整数値を表しているかどうかを判定
    try:
        int(s, 10)  # 文字列を実際にint関数で変換してみる
    except ValueError:
        return False  # 例外が発生＝変換できないのでFalseを返す
    else:
        return True

#取得するデータ
#馬番、年齢、性、体重、体重増減、斤量、クラス、出走馬数、距離、芝・ダ

# HorseInfo td HorseInfoベースでスクレイピングするのが得策そう？
column=["horse_name","horse_number", "horse_age", "horse_sex","horse_weight","horse_weight_change","weight","class_","total_number",
        "distance","condition","jokey","win_rate","連対率","複勝率"]

# https://race.netkeiba.com/race/shutuba.html?race_id=202205040102　で推論したい日付を選択して12レース分の馬名を取得

houseInfo = []

# vscode 使う-> true
debag_mode =False
is_denso = True
if debag_mode:
    path = os.path.join('/Users/hayat/Desktop/horse_inference/inference/',str(assume_id))
else:
    path = os.path.join('/home/hayato/horse_inference/inference/',str(assume_id))
if is_denso:
    path = os.path.join(path, '/home/denso/horse_inference/inference/',str(assume_id))
if not os.path.exists(path):
    os.makedirs(path)

for i in tqdm.tqdm(range(1,13,1)):
    if len(assume_id) ==12:
        assume_url = "https://race.netkeiba.com/race/shutuba.html?race_id="+ str(assume_id)
    else:
        if i < 10:
            index = "0" +  str(i)
        else:
            index = i
        assume_url = "https://race.netkeiba.com/race/shutuba.html?race_id="+ str(assume_id)+ str(index)
    print(assume_url)
    get_horse_info(column,assume_url, i)
    
    # 馬IDと騎手IDに基づいて情報を取得する

    # assume_id が12桁の場合レース番号まで指定しているので終了する
    if len(assume_id) ==12:
        break

# https://race.netkeiba.com/race/shutuba.html?race_id=202408060511


