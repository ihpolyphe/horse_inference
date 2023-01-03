import pandas as pd
import numpy as np
import tqdm
import csv
import os
# 前５走のデータを馬番号別に整理する。
# レース番号0で一着だった馬の前5レースまでをデータ化する。

yearStart = 2005#開始年を入力
yearEnd = 2022#終了年を入力

yearList = np.arange(yearStart, yearEnd+1, 1, int) 
data=[]

for for_year in yearList:
    # var_path = "/Users/hayat/Desktop/keiba_analysis/scrayping_past_info/"+str(for_year)+".csv"
    var_path = "/mnt/c/Users/hayat/Desktop/keiba_analysis/scrayping_past_info/"+str(for_year)+".csv"
    var_data = pd.read_csv(var_path,encoding='shift_jis',header=None)
    data.append(var_data)

nameList,jockyList,umabanList,timeList,oddsList,passList,weightList,dWeightList,sexList,oldList,handiList,agariList,ninkiList = [],[],[],[],[],[],[],[],[],[],[],[],[]
umaList = [nameList,jockyList,umabanList,timeList,oddsList,passList,weightList,dWeightList,sexList,oldList,handiList,agariList,ninkiList]

raceNameList,dateList,courseList,classList,surfaceList,distanceList,rotationList,surCondiList,weatherList = [],[],[],[],[],[],[],[],[]
infoList=[raceNameList,dateList,courseList,classList,surfaceList,distanceList,rotationList,surCondiList,weatherList]

tanList,fukuList,umarenList,wideList,umatanList,renpukuList,rentanList = [],[],[],[],[],[],[]
paybackList = [tanList,fukuList,umarenList,wideList,umatanList,renpukuList,rentanList]


for for_year in tqdm.tqdm(range(len(data))):
    for for_race in range(len(data[for_year][0])):
        var_dataReplaced = data[for_year][0][for_race].replace(' ','').replace('[','').replace('\'','').split("]")
        var = var_dataReplaced[0].split(",")
        var_allNumber = len(var)#出走馬の数
        #馬の名前
        nameList.append(var)
        #騎手
        jockyList.append(var_dataReplaced[1].split(",")[1:])
        #馬番
        umabanList.append(list(map(int,var_dataReplaced[2].split(",")[1:])))
        #走破時間
        var = var_dataReplaced[3].split(",")[1:]
        var1 = []
        for n in range(var_allNumber):
            try:
                var2 = var[n].split(":")
                var1.append(float(var2[0])*60 + float(var2[1]))
            except ValueError:
                var1.append(var1[-1])#ひとつ前の値で補間する
        timeList.append(var1)
        #オッズ
        var = var_dataReplaced[4].split(",")[1:]
        var1 = []
        for n in range(var_allNumber):
            try:
                var1.append(float(var[n]))
            except ValueError:
                var1.append(var1[-1])#ひとつ前の値で補間する
        oddsList.append(var1)
        #通過
        var = var_dataReplaced[5].split(",")[1:]
        var1 = []
        for n in range(var_allNumber):
            try:
                var1.append(np.average(np.array(list(map(int,var[n].split("-")))))/var_allNumber)
            except ValueError:
                var1.append(var1[-1])#ひとつ前の値で補間する    
        passList.append(var1)
        #体重
        var = var_dataReplaced[6].split(",")[1:]
        var1 = []
        var2 = []
        for n in range(var_allNumber):
            try:
                var1.append(int(var[n].split("(")[0]))
                var2.append(int(var[n].split("(")[1][0:-1]))
            except ValueError:
                var1.append(var2[-1])
                var2.append(var2[-1])
        weightList.append(var1)
        dWeightList.append(var2)
        #性齢
        var = var_dataReplaced[7].split(",")[1:]
        var1 = []
        var2 = []
        for n in range(var_allNumber):
            var11 = var[n][0]
            if "牡" in var11:
                var1.append(0)
            elif "牝" in var11:
                var1.append(1)
            elif "セ" in var11:
                var1.append(2)
            else:
                print(var11)
            var2.append(int(var[n][1:]))
        sexList.append(var1)
        oldList.append(var2)
        #斤量
        handiList.append(list(map(float,var_dataReplaced[8].split(",")[1:])))
        #上がり
        var = var_dataReplaced[9].split(",")[1:]
        var1 = []
        for n in range(var_allNumber):
            try:
                var1.append(float(var[n]))
            except ValueError:
                var1.append(var1[-1])#ひとつ前の値で補間する
        agariList.append(var1)
        #人気
        var = var_dataReplaced[10].split(",")[1:]
        var1 = []
        for n in range(var_allNumber):
            try:
                var1.append(int(var[n]))
            except ValueError:
                var1.append(var1[-1])#ひとつ前の値で補間する
        ninkiList.append(var1)

        var_infoReplaced = data[for_year][1][for_race].replace(' ','').replace('[','').replace('\'','').split("]")[:-2]
        #レースの名前
        raceNameList.append(var_infoReplaced[0])
        #日付
        var = var_infoReplaced[1]
        var1 = var.split("年")
        var2 = var1[1].split("月")
        dateList.append((int(var1[0].replace(",",""))-yearStart)*365+int(var2[0])*30+int(var2[1].split("日")[0]))
        #競馬場
        var = var_infoReplaced[2]
        if "札幌" in var:
            courseList.append(0)
        elif "函館" in var:
            courseList.append(1)
        elif "福島" in var:
            courseList.append(2)
        elif "新潟" in var:
            courseList.append(3)
        elif "東京" in var:
            courseList.append(4)
        elif "中山" in var:
            courseList.append(5)
        elif "中京" in var:
            courseList.append(6)
        elif "京都" in var:
            courseList.append(7)
        elif "阪神" in var:
            courseList.append(8)
        elif "小倉" in var:
            courseList.append(9)
        else:
            print(var)
        #クラス
        var = var_infoReplaced[0]
        var1 = var_infoReplaced[3]
        if "障害" in var1:
            classList.append(0)
        elif "G1" in var:
            classList.append(10)
        elif "G2" in var:
            classList.append(9)
        elif "G3" in var:
            classList.append(8)
        elif ("(L)" in var) or ("オープン" in var1):
            classList.append(7)
        elif ("3勝" in var1) or ("1600" in var1):
            classList.append(6)
        elif ("2勝" in var1) or ("1000" in var1):
            classList.append(5)
        elif ("1勝" in var1) or ("500" in var1):
            classList.append(4)
        elif "新馬" in var1:
            classList.append(3)
        elif "未勝利" in var1:
            classList.append(2)
        else:
            print(var)
        #芝、ダート
        var = var_infoReplaced[4]
        if "芝" in var:
            surfaceList.append(0)
        elif "ダ" in var:
            surfaceList.append(1)
        elif "障" in var:
            surfaceList.append(2)
        else:
            print(var)
        #距離
        distanceList.append(int(var_infoReplaced[5].replace(",","")))
        #回り
        var = var_infoReplaced[6]
        if "右" in var:
            rotationList.append(0)
        elif "左" in var:
            rotationList.append(1)
        elif ("芝" in var) or ("直" in var):
            rotationList.append(2)
        else:
            print(var)
        #馬場状態
        var = var_infoReplaced[7]
        if "良" in var:
            surCondiList.append(0)
        elif "稍" in var:
            surCondiList.append(1)
        elif "重" in var:
            surCondiList.append(2)
        elif "不" in var:
            surCondiList.append(3)
        else:
            print(var)
        #天気
        var = var_infoReplaced[8]
        if "晴" in var:
            weatherList.append(0)
        elif "曇" in var:
            weatherList.append(1)
        elif "小" in var:
            weatherList.append(2)
        elif "雨" in var:
            weatherList.append(3)
        elif "雪" in var:
            weatherList.append(4)
        else:
            print(var)
        
        #単勝、複勝、馬連、ワイド、馬単、三連複、三連単の順番で格納
        var_paybackReplaced = data[for_year][2][for_race].replace('[','').replace(",","").replace('\'','').split("]")
        #単勝
        tanList.append(int(var_paybackReplaced[0].split(" ")[1]))
        #複勝
        var = var_paybackReplaced[1].split(" ")[1:]
        var_list = []
        for for_var in range(int(len(var)/2)):
            var_list.append(int(var[2*for_var+1]))
        fukuList.append(var_list)
        #馬連
        umarenList.append(int(var_paybackReplaced[2].split(" ")[-1]))
        #ワイド
        var = var_paybackReplaced[3].split(" ")[1:]
        var_list = []
        for for_var in range(int(len(var)/4)):
            var_list.append(int(var[4*for_var+3]))
        wideList.append(var_list)
        #馬単
        umatanList.append(int(var_paybackReplaced[4].split(" ")[-1]))
        #三連複
        renpukuList.append(int(var_paybackReplaced[5].split(" ")[-1]))
        #三連単
        rentanList.append(int(var_paybackReplaced[6].split(" ")[-1]))

data = []
for for_races in tqdm.tqdm(range(len(nameList))):
    var_list = []#uma,info,payback
    for for_lists in umaList:
        var_list.append(for_lists[for_races])
    for for_lists in infoList:
        var_list.append(for_lists[for_races])
    for for_lists in paybackList:
        var_list.append(for_lists[for_races])
    data.append(var_list)

data = sorted(data, key = lambda x: x[14],reverse = True)#日付が大きい順番に並べる
'''
data
第一指数：全レース数
第二指数：0~28でレースの情報
'''

# print(data[0][0])

#前走のインデックスのリストを生成する
dataGet = 20000#何レース分のデータを取得するか
pastRaces = 6000#過去何レース調べるか
pastResults = 5#前走何レースを参考にするか
pastIndexList = []
lenData = len(data)

assume_name = ["アフロビート","グランデスパーダ","ルーラーリッチ","ノーブルヴィクター","カイザーブリッツ","インナーサンクタム","サウザンパンチ","マイショウチャン","サノノウォーリア","リッチハンター","レーガンテソーロ","サイタブラウン","トレジャートレイル","ジェイケイファイン","ミサイルビスケッツ","シゲルタイムフライ"]

dataGet = len(data)
for for_races in tqdm.tqdm(range(dataGet)):
    var_pastIndexList = []#1レース分の馬柱
    var_min = min([lenData,for_races+pastRaces])
    for for_horses in range(len(data[for_races][0])):#馬の数、0はnameListを示す
    # for for_horses in range(len(assume_name)):#馬の数、0はnameListを示す
        # var_name = assume_name[for_horses]
        var_name = data[for_races][0][for_horses]
        var_list = []#何レース前で何着かを記録する
        for for_pastRaces in range(for_races+1,var_min,1):#ここのレースから前を調べる
            for for_allNum in range(len(data[for_pastRaces][0])):#照合先の馬の数
                if var_name == data[for_pastRaces][0][for_allNum]:
                    var_list.append([for_pastRaces,for_allNum])
                    break
            if len(var_list) >= pastResults:#リストの中身が規定の数越えたら終了する
                break
        var_pastIndexList.append(var_list)
    pastIndexList.append(var_pastIndexList)
# print(pastIndexList)

svg_path = '/mnt/c/Users/hayat/Desktop/keiba_analysis/data_for_train/horse_index/'
if not os.path.exists(svg_path):
    os.mkdir(svg_path)

with open(svg_path + str(yearStart)+"_"+str(yearEnd)+'_index.csv', 'w', newline='',encoding="shift_jis") as f:
    csv.writer(f).writerows(pastIndexList)