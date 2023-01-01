#2022年分
import requests
from bs4 import BeautifulSoup
import time
import tqdm
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import lxml.html

# 単勝オッズページを引数に指定して、そのページから馬番・馬名・単勝オッズを取得し、DataFrame形式で返す
def get_win_odds_df(assume_id,index):
    url = "https://race.netkeiba.com/odds/index.html?race_id="+ str(assume_id)+ str(index)
    # Seleniumを用いてクローリング
    # pathの関係でvscodeではできなさそう。ターミナルで実行すること。
    driver = webdriver.PhantomJS()                  # PhamtomJSのWebDriverオブジェクトを作成する。
    driver.get(url)                                 # オッズ表示画面を開く
    root = lxml.html.fromstring(driver.page_source) # 検索結果を表示し、lxmlで解析準備

    # 辞書・リストの初期化
    win_odds_dict       = {}
    horse_number_list   = []
    horse_name_list     = []
    tan_odds_list       = []

    # 馬番・馬名・単勝オッズをスクレイピング
    for horse_number,horse_name,tan_odds in zip(root.cssselect('.umaban'),root.cssselect('.h_name'),root.cssselect('[axis^=oddsDataTan]')):
        horse_number_list.append(horse_number.text)
        horse_name_list.append(horse_name.text)
        tan_odds_list.append(tan_odds.text)

    # スクレイピング結果を辞書からDataFrame形式に変換
    win_odds_dict["horse_number"]   =   horse_number_list
    win_odds_dict["horse_name"]     =   horse_name_list
    win_odds_dict["tan_odds"]       =   tan_odds_list
    win_odds_df                     =   pd.DataFrame(win_odds_dict,columns=['horse_number', 'horse_name', 'tan_odds'])
    print(win_odds_df)
    return win_odds_df

# ファイル名に馬名があると読み出し失敗する。

def isint(s):  # 整数値を表しているかどうかを判定
    try:
        int(s, 10)  # 文字列を実際にint関数で変換してみる
    except ValueError:
        return False  # 例外が発生＝変換できないのでFalseを返す
    else:
        return True


if __name__ == '__main__':
    #取得するデータ(このまま説明変数)
    #馬番、年齢、性、体重、体重増減、斤量、クラス、出走馬数、距離、芝・ダ

    # HorseInfo td HorseInfoベースでスクレイピングするのが得策そう？
    column=["horse_number", "horse_age", "horse_sex","horse_weight","horse_weight_change","weight","class_","total_number",
            "distance","condition","win_rate","連対率","複勝率"]

    # https://race.netkeiba.com/race/shutuba.html?race_id=202205040102　で推論したい日付を選択して12レース分の馬名を取得
    assume_id = 2022090407
    houseInfo = []

    # vscode 使う-> true
    debag_mode =False

    if debag_mode:
        path = os.path.join('/Users/hayat/Desktop/keiba_analysis/',str(assume_id))
    else:
        path = os.path.join('/mnt/c/Users/hayat/Desktop/keiba_analysis/',str(assume_id))
    if not os.path.exists(path):
        os.mkdir(path)

    for i in tqdm.tqdm(range(1,13,1)):
        if i < 10:
            index = "0" +  str(i)
        else:
            index = i
        assume_url = "https://race.netkeiba.com/race/shutuba.html?race_id="+ str(assume_id)+ str(index)
        get_win_odds_df(assume_id,index)

        r=requests.get(assume_url)
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
        class_=soup.find_all("div",class_='RaceData02')[0].contents[9].contents[0] #未勝利か、2歳か、G1か
        number_of_horse_str=soup.find_all("div",class_='RaceData02')[0].contents[15].contents[0] # 頭数
        number_of_horse_=int(number_of_horse_str[:(len(number_of_horse_str)-1)])
        if "障害" in class_:
            class_ in 0
        elif "G1" in class_:
            class_ = 10
        elif "G2" in class_:
            class_ = 9
        elif "G3" in class_:
            class_ = 8
        elif ("(L)" in class_) or ("オープン" in class_):
            class_ = 7
        elif ("３勝" in class_) or ("1600" in class_):
            class_ = 6
        elif ("２勝" in class_) or ("1000" in class_):
            class_ = 5
        elif ("１勝" in class_) or ("500" in class_):
            class_ = 4
        elif "新馬" in class_:
            class_ = 3
        elif "未勝利" in class_:
            class_ = 2
        else:
            print(class_)

        #芝、ダート
        if "芝" in condition:
            condition = 0
        elif "ダ" in condition:
            condition = 1
        elif "障" in condition:
            condition = 2
        else:
            print(condition)

        for n in range(allnum):#レース12
            soup_txt_l = 0
            horse_weight = 0
            #馬の情報
            try:
                horse_name=soup.find_all("span",class_='HorseName')[n].contents[0].contents[0]
                yaer_sex=soup.find_all("td",class_='Barei Txt_C')[n-1].contents[0]
                # jokey=soup.find_all("td",class_='Jockey')[n-1]
                sex = yaer_sex[:1]
                year = int(yaer_sex[1:])
                # weight=soup.find_all("td",class_='Txt_C')[n*3]
                weight=float(soup.select('td[class="Txt_C"]')[n-1].contents[0])
                jokey=soup.select('td[class="Jockey"]')[n-1].contents[1].contents[0]
                # horse_weight_str=soup.select('td[class="Weight"]')[n-1].contents[0]  #馬体重は記載されていないので固定値500
                # horse_weight = int(horse_weight_str.strip())
                # horse_weight=soup.find_all("td",class_='Weight')[n].contents[0]
                horse_weight = 500
                # horse_weight_change=soup.select('td[class="Weight"]')[n-1].contents[1].contents[0]
                # horse_weight_change = horse_weight_change.lstrip("(")
                # horse_weight_change = horse_weight_change.rstrip(")")
                # horse_weight_change_data = int(horse_weight_change,10)
                horse_weight_change_data = 6
                if "牡" == sex:
                    sex_ = 0
                elif "牝" == sex:
                    sex_ = 1
                elif "セ" == sex:
                    sex_ = 2
                else:
                    print(sex)

                if jokey in "川田将雅" :
                    win_rate =0.281
                    rentairitu = 0.462
                    hukusyouritu =0.604
                elif jokey in "戸崎圭太" :
                    win_rate =0.166		
                    rentairitu = 0.304
                    hukusyouritu =0.403
                elif jokey in "横山武史" :
                    win_rate =0.174	
                    rentairitu = 0.311	
                    hukusyouritu =0.429
                elif jokey in "松山弘平" :
                    win_rate =0.148	
                    rentairitu = 0.239	
                    hukusyouritu =0.319
                elif jokey in "	福永祐一" :
                    win_rate =0.177		
                    rentairitu = 0.287	
                    hukusyouritu =0.429
                elif jokey in "	Ｃルメール" :
                    win_rate =0.193	
                    rentairitu = 0.358	
                    hukusyouritu =0.488
                elif jokey in "	岩田望来" :
                    win_rate =0.128	
                    rentairitu = 0.223	
                    hukusyouritu =0.309
                elif jokey in "	坂井瑠星" :
                    win_rate =0.125	
                    rentairitu = 0.243	
                    hukusyouritu =0.331
                elif jokey in "	吉田隼人" :
                    win_rate =0.122	
                    rentairitu = 0.208	
                    hukusyouritu =0.289
                elif jokey in "		鮫島克駿" :
                    win_rate =0.090	
                    rentairitu = 0.174	
                    hukusyouritu =0.280
                elif jokey in "	丹内祐次" :
                    win_rate =0.087	
                    rentairitu = 0.185	
                    hukusyouritu =0.278
                elif jokey in "	菅原明良" :
                    win_rate =0.086	
                    rentairitu = 0.176	
                    hukusyouritu =0.259
                elif jokey in "	武豊" :
                    win_rate =0.124	
                    rentairitu = 0.257	
                    hukusyouritu =0.373
                elif jokey in "	田辺裕信" :
                    win_rate =0.135	
                    rentairitu = 0.258	
                    hukusyouritu =0.361
                elif jokey in "	Ｍデムーロ" :
                    win_rate =0.122	
                    rentairitu = 0.266	
                    hukusyouritu =0.405
                elif jokey in "	西村淳也" :
                    win_rate =0.099	
                    rentairitu = 0.208	
                    hukusyouritu =0.297
                elif jokey in "	池添謙一" :
                    win_rate =0.113	
                    rentairitu = 0.191	
                    hukusyouritu =0.294	
                elif jokey in "	幸英明" :
                    win_rate =0.068	
                    rentairitu = 0.142	
                    hukusyouritu =0.224
                elif jokey in "	三浦皇成" :
                    win_rate =0.092	
                    rentairitu = 0.206	
                    hukusyouritu =0.302
                elif jokey in "和田竜二" :
                    win_rate =0.062	
                    rentairitu = 0.152	
                    hukusyouritu =0.258
                elif jokey in "岡康太" :
                    win_rate =0.083	
                    rentairitu = 0.183	
                    hukusyouritu =0.272
                elif jokey in "今村聖奈" :
                    win_rate =0.096	
                    rentairitu = 0.172	
                    hukusyouritu =0.249
                elif jokey in "菱田裕二" :
                    win_rate =0.082	
                    rentairitu = 0.191	
                    hukusyouritu =0.252
                elif jokey in "藤岡佑介" :
                    win_rate =0.281
                    rentairitu = 0.462
                    hukusyouritu =0.604
                elif jokey in "浜中俊" :
                    win_rate =0.112	
                    rentairitu = 0.195	
                    hukusyouritu =0.305
                elif jokey in "岩田康誠" :
                    win_rate =0.094	
                    rentairitu = 0.169	
                    hukusyouritu =0.246
                elif jokey in "富田暁" :
                    win_rate =0.064	
                    rentairitu = 0.138	
                    hukusyouritu =0.206
                elif jokey in "松若風馬" :
                    win_rate =0.071	
                    rentairitu = 0.147	
                    hukusyouritu =0.202
                elif jokey in "	角田大和" :
                    win_rate =0.069	
                    rentairitu = 0.127	
                    hukusyouritu =0.205
                elif jokey in "	津村明秀" :
                    win_rate =0.065	
                    rentairitu = 0.133	
                    hukusyouritu =0.230
                elif jokey in "	石橋脩" :
                    win_rate =0.084
                    rentairitu = 0.157	
                    hukusyouritu =0.244	
                elif jokey in "	石川裕紀人" :
                    win_rate =0.060	
                    rentairitu = 0.115	
                    hukusyouritu =0.165
                elif jokey in "横山典弘" :
                    win_rate =0.091	
                    rentairitu = 0.220	
                    hukusyouritu =0.289
                elif jokey in "松本大輝" :
                    win_rate =0.058	
                    rentairitu = 0.116
                    hukusyouritu =0.186
                elif jokey in "	横山琉人" :
                    win_rate =0.053	
                    rentairitu = 0.098	
                    hukusyouritu =0.137
                elif jokey in "	斎藤新" :
                    win_rate =0.052	
                    rentairitu = 0.124	
                    hukusyouritu =0.192
                elif jokey in "永野猛蔵" :
                    win_rate =0.046	
                    rentairitu = 0.119	
                    hukusyouritu =0.157
                elif jokey in "小沢大仁" :
                    win_rate =0.050	
                    rentairitu = 0.095	
                    hukusyouritu =0.145
                elif jokey in "団野大成" :
                    win_rate =0.058	
                    rentairitu = 0.145	
                    hukusyouritu =0.208
                elif jokey in "Ｄレーン" :
                    win_rate =0.189	
                    rentairitu = 0.369	
                    hukusyouritu =0.451
                elif jokey in "大野拓弥" :
                    win_rate =0.057	
                    rentairitu = 0.100	
                    hukusyouritu =0.149
                elif jokey in "秋山稔樹" :
                    win_rate =0.049	
                    rentairitu = 0.086	
                    hukusyouritu =0.147
                elif jokey in "	荻野極" :
                    win_rate =0.070	
                    rentairitu = 0.105	
                    hukusyouritu =0.157
                elif jokey in "木幡巧也" :
                    win_rate =0.051	
                    rentairitu = 0.102	
                    hukusyouritu =0.150
                elif jokey in "	内田博幸" :
                    win_rate =0.036	
                    rentairitu = 0.095	
                    hukusyouritu =0.163
                elif jokey in "菊沢一樹" :
                    win_rate =0.042	
                    rentairitu = 0.071	
                    hukusyouritu =0.103
                elif jokey in "古川吉洋" :
                    win_rate =0.050	
                    rentairitu = 0.110	
                    hukusyouritu =0.172
                elif jokey in "秋山真一郎" :
                    win_rate =0.064	
                    rentairitu = 0.104	
                    hukusyouritu =0.172
                elif jokey in "横山和生" :
                    win_rate =0.128	
                    rentairitu = 0.237	
                    hukusyouritu =0.326
                else:# 騎手不明のため下げる
                    win_rate =0.01
                    rentairitu = 0.01	
                    hukusyouritu =0.01
                horse_list = [n,year,sex_,horse_weight,horse_weight_change_data,weight,class_,number_of_horse_,distance,condition,win_rate,rentairitu,hukusyouritu]
                horse.append(horse_list)
                horse_name_list.append(horse_name)
            except:
                pass



        # # データフレームを作成
        df = pd.DataFrame(horse, columns=column)
        df_name =pd.DataFrame(horse_name_list)
        # # CSV ファイル出力
        df.to_csv(path+"/scrayping_"+str(assume_id)+str(i) +".csv")
        df_name.to_csv(path+"/horse_name_"+str(assume_id)+str(i)+'.csv')
        time.sleep(1)#サーバーの負荷を減らすため1秒待機する

