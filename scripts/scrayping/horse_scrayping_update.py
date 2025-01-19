import requests
from bs4 import BeautifulSoup
import time
import csv 
import os
"""
yaerに指定した年の各レースごとの情報をcsvに出力する。
出力したcsvの情報を用いて学習データを作成する。
"""

# 本スクリプトで記録できるデータは以下の通り
# 1. 馬の名前
# 2. 騎手の名前
# 3. 馬番
# 4. 走破時間
# 5. オッズ
# 6. 通過順
# 7. 体重
# 8. 性齢
# 9. 斤量
# 10. 上がり
# 11. 人気
# 12. レース名
# 13. 日付
# 14. 詳細
# 15. クラス
# 16. 場所
# 17. 距離
# 18. ラウンド
# 19. コース
# 20. 天候
# 21. 単勝
# 22. 複勝
# 23. 枠連
# 24. 馬連
# 25. ワイド
# 26. 馬単
# 27. 三連複
# 28. 三連単


year = "2005"#西暦を入力

def appendPayBack1(varSoup):#複勝とワイド以外で使用
    varList = []
    varList.append(varSoup.contents[3].contents[0])
    varList.append(varSoup.contents[5].contents[0])
    payBackInfo.append(varList)

def appendPayBack2(varSoup):#複勝とワイドで使用
    varList = []
    for var in range(3):
        try:#複勝が３個ないときを除く
            varList.append(varSoup.contents[3].contents[2*var])
        except IndexError:
            pass
        try:
            varList.append(varSoup.contents[5].contents[2*var])
        except IndexError:
            pass
    payBackInfo.append(varList)
# 01：札幌、02：函館、03：福島、04：新潟、05：東京、06：中山、07：中京、08：京都、09：阪神、10：小倉
List=[]
l=["01","02","03","04","05","06","07","08","09","10"]#競馬場
for w in range(len(l)):
    z_loop_judge=0
    for z in range(8):#開催、6まで十分だけど保険で7
        y_loop_judge=0
        # if z_loop_judge==2:
        #     break
        for y in range(16):#日、12まで十分だけど保険で14
            # if y_loop_judge==1:
            #     break
            if y < 9:
                url1 = f"https://db.netkeiba.com/race/{year}{l[w]}0{z+1}0{y+1}"
            else:
                url1 = f"https://db.netkeiba.com/race/{year}{l[w]}0{z+1}{y+1}"
            yBreakCounter = 0#yの更新をbreakするためのカウンター
            for x in range(13):#レース12
                if x < 9:
                    url = f"{url1}0{x+1}"
                else:
                    url = f"{url1}{x+1}"
                # リクエストヘッダーを追加
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
                }
                r = requests.get(url, headers=headers)

                soup = BeautifulSoup(r.content.decode("euc-jp", "ignore"), "html.parser")#バグ対策でdecode
                soup_span = soup.find_all("span")
                print(r)
                allnum=(len(soup_span)-6)/3#馬の数
                if allnum < 1:#urlにデータがあるか判定
                    yBreakCounter+=1
                    y_loop_judge=1
                    if y_loop_judge==1:
                        z_loop_judge=2
                        print("break")
                        break
                else:
                    time.sleep(0.2)#サーバーの負荷を減らすため1秒待機する

                allnum=int(allnum)
                #馬の情報
                soup_txt_l=soup.find_all(class_="txt_l")
                name=[]#馬の名前
                for num in range(allnum):
                    try:
                        name.append(soup_txt_l[4*num].contents[1].contents[0])
                    except IndexError:
                        name.append(None)
                jockey=[]#騎手の名前
                for num in range(allnum):
                    try:
                        jockey.append(soup_txt_l[4*num+1].contents[1].contents[0])
                    except IndexError:
                        jockey.append(None)
                soup_txt_r=soup.find_all(class_="txt_r")
                horse_number=[]#馬番
                for num in range(allnum):
                    # print("馬番 : ",soup_txt_r[1+5*num].contents[0])
                    try:
                        horse_number.append(soup_txt_r[1+5*num].contents[0])
                    except IndexError:
                        horse_number.append(None)
                runtime=[]#走破時間
                for num in range(allnum):
                    try:
                        runtime.append(soup_txt_r[2+5*num].contents[0])
                    except IndexError:
                        runtime.append(None)
                
                # 走破時間から着順を取得してリストに追加


                odds=[]#オッズ
                for num in range(allnum):
                    try:
                        odds.append(soup_txt_r[3+5*num].contents[0])
                    except IndexError:
                        odds.append(None)
                soup_nowrap = soup.find_all("td",nowrap="nowrap",class_=None)
                pas = []#通過順
                for num in range(allnum):
                    try:
                        pas.append(soup_nowrap[3*num].contents[0])
                    except:
                        pas.append(None)

                weight = []#体重
                for num in range(allnum):
                    try:
                        weight.append(soup_nowrap[3*num+1].contents[0])
                    except IndexError:
                        weight.append(None)
                soup_tet_c = soup.find_all("td",nowrap="nowrap",class_="txt_c")
                sex_old = []#性齢
                for num in range(allnum):
                    try:
                        sex_old.append(soup_tet_c[6*num].contents[0])
                    except IndexError:
                        sex_old.append(None)
                handi = []#斤量
                for num in range(allnum):
                    try:
                        handi.append(soup_tet_c[6*num+1].contents[0])
                    except IndexError:
                        handi.append(None)
                last = []#上がり
                for num in range(allnum):
                    try:
                        last.append(soup_tet_c[6*num+3].contents[0].contents[0])
                    except IndexError:
                        last.append(None)

                # pop = []#人気
                # for num in range(allnum):
                #     try:
                #         pop.append(soup_span[3*num+11].contents[0])
                #     except IndexError:
                #         pop.append(None)
                #220521から仕様変更？
                pop = []#人気
                for num in range(allnum):
                    try:
                        pop.append(soup_span[3*num+10].contents[0])
                    except IndexError:
                        pop.append(None)
                
                # 馬IDを保存
                horse_links = soup.find_all('a', id=lambda x: x and x.startswith('umalink_'))

                horse_ids = []
                for link in horse_links:
                    try:
                        href = link.get('href')
                        horse_id = href.split('/')[2]  # "/horse/2003106133/" の "2003106133" を抽出
                        horse_ids.append(horse_id)
                    except IndexError:
                        horse_ids.append(None)
                # 騎手IDを保存
                jockey_links = soup.find_all('a', href=lambda x: x and '/jockey/result/recent/' in x)
                jockey_ids = []
                for link in jockey_links:
                    try:
                        href = link.get('href')
                        jockey_id = href.split('/')[4]  # "/jockey/result/recent/01043/" の "01043" を抽出
                        jockey_ids.append(jockey_id)
                    except IndexError:
                        jockey_ids.append(None)
                # オーナーIDを抽出
                owner_links = soup.find_all('a', href=lambda x: x and '/owner/result/recent/' in x)

                owner_ids = []
                for link in owner_links:
                    try:
                        href = link.get('href')
                        owner_id = href.split('/')[4]  # "/owner/result/recent/637006/" の "637006" を抽出
                        owner_ids.append(owner_id)
                    except IndexError:
                        owner_ids.append(None)
                # トレーナーIDを抽出
                trainer_links = soup.find_all('a', href=lambda x: x and '/trainer/result/recent/' in x)

                trainer_ids = []
                for link in trainer_links:
                    try:
                        href = link.get('href')
                        trainer_id = href.split('/')[4]  # "/trainer/result/recent/00339/" の "00339" を抽出
                        trainer_ids.append(trainer_id)
                    except IndexError:
                        trainer_ids.append(None)
                houseInfo = [name,jockey,horse_number,runtime,odds,pas,weight,sex_old,handi,last,pop,horse_ids,jockey_id,owner_ids,trainer_ids]

                #レースの情報
                try:
                    var = soup_span[8]
                    sur=str(var).split("/")[0].split(">")[1][0]
                    rou=str(var).split("/")[0].split(">")[1][1]
                    dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                    con=str(var).split("/")[2].split(":")[1][1]
                    wed=str(var).split("/")[1].split(":")[1][1]
                except IndexError:
                    try:
                        var = soup_span[7]
                        sur=str(var).split("/")[0].split(">")[1][0]
                        rou=str(var).split("/")[0].split(">")[1][1]
                        dis=str(var).split("/")[0].split(">")[1].split("m")[0][-4:]
                        con=str(var).split("/")[2].split(":")[1][1]
                        wed=str(var).split("/")[1].split(":")[1][1]
                    except IndexError:
                        var = soup_span[6]
                        sur=None
                        rou=None
                        dis=None
                        con=None
                        wed=None
                soup_smalltxt = soup.find_all("p",class_="smalltxt")
                print(soup_smalltxt)
                try:
                    detail=str(soup_smalltxt).split(">")[1].split(" ")[1]
                    date=str(soup_smalltxt).split(">")[1].split(" ")[0]
                    clas=str(soup_smalltxt).split(">")[1].split(" ")[2].replace(u'\xa0', u' ').split(" ")[0]
                    title=str(soup.find_all("h1")[1]).split(">")[1].split("<")[0]
                except IndexError:
                    detail=None
                    # detail がNoneの場合のurlをチェック
                    print(url)
                    date=None
                    clas=None
                    title=None
                raceInfo = [[title],[date],[detail],[clas],[sur],[dis],[rou],[con],[wed]]#他と合わせるためにリストの中にリストを入れる
                #払い戻しの情報 -> 学習に用いても推論で用いれないかつスクレイピングできなかったのでコメントアウト



                # payBack = soup.find_all("table",summary='払い戻し')
                # payBackInfo=[]#単勝、複勝、枠連、馬連、ワイド、馬単、三連複、三連単の順番で格納
                # appendPayBack1(payBack[0].contents[1])#単勝
                # try:
                #     payBack[0].contents[5]#これがエラーの時複勝が存在しない
                #     appendPayBack2(payBack[0].contents[3])#複勝
                #     try:
                #         appendPayBack1(payBack[0].contents[7])#馬連
                #     except IndexError:
                #         appendPayBack1(payBack[0].contents[5])#通常は枠連だけど、この時は馬連
                # except IndexError:#この時複勝が存在しない
                #     payBackInfo.append([payBack[0].contents[1].contents[3].contents[0],'110'])#複勝110円で代用
                #     print("複勝なし")
                #     appendPayBack1(payBack[0].contents[3])#馬連
                # appendPayBack2(payBack[1].contents[1])#ワイド
                # appendPayBack1(payBack[1].contents[3])#馬単
                # appendPayBack1(payBack[1].contents[5])#三連複
                # try:
                #     appendPayBack1(payBack[1].contents[7])#三連単
                # except IndexError:
                #     appendPayBack1(payBack[1].contents[5])#三連複を三連単の代わり
                List.append([houseInfo,raceInfo])
                print(str(detail)+str(x+1)+"R")#進捗を表示

            if yBreakCounter == 12:#12レース全部ない日が検出されたら、その開催中の最後の開催日と考える
                break
svg_path = '/home/hayato/horse_inference/data_for_train/scrayping_past_info/'
if not os.path.exists(svg_path):
    os.mkdir(svg_path)
# horse_info_column = ['name', 'jockey', 'horse_number', 'runtime', 'odds', 'pass', 'weight','sex_old', 'handi', 'last', 'pop', 'horse_id', 'jockey_id', 'owner_id', 'trainer_id']
# pay_back_column = ['win', 'place', 'frame', 'uma', 'wide', 'uma_tan', 'sanrenpuku', 'sanrentan']    
# race_info_column = ['title', 'date', 'detail', 'class', 'sur', 'distance', 'rou', 'condition', 'wed']

# total_columns = horse_info_column + race_info_column + pay_back_column
with open(svg_path + year+'_add_id.csv', 'w', newline='',encoding='shift_jis') as f:
    # csv.writer(f).writerow(total_columns)
    csv.writer(f).writerows(List)
print("終了")


#pandas.read_csv("2022-09-30-10.csv",encoding='shift_jis',header=None)