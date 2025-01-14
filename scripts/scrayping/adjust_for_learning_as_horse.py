import pandas as pd
import numpy as np
import tqdm
import csv
import os
import sys

"""
各のレースデータから、trainデータおよび、馬の過去レースデータを抽出するscript
1列に1馬の情報を残すようにするスクリプト。１列に全レースの情報を保持する方法では学習結果が向上せず、データの拡張性が乏しかったためこちらで対応。
"""
yearStart = 2005#開始年を入力
yearEnd = 2019#終了年を入力

yearList = np.arange(yearStart, yearEnd+1, 1, int) 
data=[]

# 馬の過去データが欲しいのであればTrueにする
# 学習データだけを撮りたい場合はFalseにする
request_horse_past_data = False

# 学習パス
is_denso = True

# 学習用レースごとのデータは以下に保存
train_data_path = "/home/hayato/horse_inference/data_for_train/train/"
if is_denso:
    train_data_path = "/home/denso/horse_inference/data_for_train/train/"
if not os.path.exists(train_data_path):

    os.makedirs(train_data_path)

train_data_path_year = train_data_path + str(yearStart) + "_" + str(yearEnd) + "/"
if not os.path.exists(train_data_path_year):
    os.makedirs(train_data_path_year)


for for_year in yearList:
    # var_path = "/Users/hayat/Desktop/keiba_analysis/data_for_train/scrayping_past_info/"+str(for_year)+".csv"
    var_path = "/home/hayato/horse_inference/data_for_train/scrayping_past_info/"+str(for_year)+".csv"
    if is_denso:
        var_path = "/home/denso/horse_inference/data_for_train/scrayping_past_info/"+str(for_year)+".csv"
    var_data = pd.read_csv(var_path,encoding='shift_jis',header=None)
    data.append(var_data)

nameList,jockyList,umabanList,goal_numberList,timeList,oddsList,passList,weightList,dWeightList,sexList,oldList,handiList,agariList,ninkiList = [],[],[],[],[],[],[],[],[],[],[],[],[],[]
umaList = [nameList,jockyList,umabanList,goal_numberList,timeList,oddsList,passList,weightList,dWeightList,sexList,oldList,handiList,agariList,ninkiList]

raceNameList,dateList,courseList,classList,surfaceList,distanceList,rotationList,surCondiList,weatherList = [],[],[],[],[],[],[],[],[]
infoList=[raceNameList,dateList,courseList,classList,surfaceList,distanceList,rotationList,surCondiList,weatherList]

tanList,fukuList,umarenList,wideList,umatanList,renpukuList,rentanList = [],[],[],[],[],[],[]
paybackList = [tanList,fukuList,umarenList,wideList,umatanList,renpukuList,rentanList]

train_data_total_frame = []
for for_year in tqdm.tqdm(range(len(data))):
    for for_race in range(len(data[for_year][0])):
        # レースごとの保存用リストを初期化
        name_list_in_race = []
        jocky_list_in_race = []
        umaban_list_in_race = []
        goal_number_list_in_race = []
        horse_age_list = []
        horse_sex_list = []
        weight_list_in_race = []
        weight_change_list_in_race = []
        handi_list_in_race  = []
        class_list_in_race = None
        number_of_horses = None
        distance_list = None
        condition_list = None
        odds_list_in_race  = []
        race_name = None
        data_list = None
        

        var_dataReplaced = data[for_year][0][for_race].replace(' ','').replace('[','').replace('\'','').split("]")
        var = var_dataReplaced[0].split(",")
        var_allNumber = len(var)#出走馬の数
        #馬の名前
        nameList.append(var)
        name_list_in_race.append(var)
        # 着順は馬の名前順になっているので、リストで格納する
        goal_number =list( range(1,len(var)+1,1))
        goal_numberList.append(goal_number)
        goal_number_list_in_race.append(goal_number)
        #騎手
        jockyList.append(var_dataReplaced[1].split(",")[1:])
        jocky_list_in_race.append(var_dataReplaced[1].split(",")[1:])
        #馬番
        umabanList.append(list(map(int,var_dataReplaced[2].split(",")[1:])))
        umaban_list_in_race.append(list(map(int,var_dataReplaced[2].split(",")[1:])))
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
        odds_list_in_race.append(var1)
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
        weight_list_in_race.append(var1)
        dWeightList.append(var2)
        weight_change_list_in_race.append(var2)
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
        horse_age_list.append(var2)
        horse_sex_list.append(var1) 

        #斤量
        handiList.append(list(map(float,var_dataReplaced[8].split(",")[1:])))
        handi_list_in_race.append(list(map(float,var_dataReplaced[8].split(",")[1:])))
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
        race_name = var_infoReplaced[0]
        #日付
        var = var_infoReplaced[1]
        var1 = var.split("年")
        var2 = var1[1].split("月")
        # 年月日を基準年からの経過日数に変換→数字が大きいほど最新、小さいほど基準年に近い古いデータとなる
        # 年の抽出
        year = int(var1[0].replace(",",""))
        # 月の抽出
        month = int(var2[0])
        # 日の抽出
        day = int(var2[1].split("日")[0])

        #競馬場
        var = var_infoReplaced[2]
        place = var
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
        class_list_in_race = var1
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
        condition_list = var
        #距離
        distanceList.append(int(var_infoReplaced[5].replace(",","")))
        distance_list = int(var_infoReplaced[5].replace(",",""))
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
        number_of_horses = len(name_list_in_race[0])

        # umaban_list_in_raceの小さい順にインデックスを取得
        sorted_indices = sorted(range(len(umaban_list_in_race[0])), key=lambda k: umaban_list_in_race[0][k])


        # レースごとの結果がリストに格納されているので、csvに書き出し
        # リストが2重になっているので、0番目のリストの指定が必要
        initialize = True
        for i in sorted_indices:
            # 年月日は年、月、日プラスfor_raceをつけてすべてのレースと切り分けできるindexも作成する
            # 例えば、2005年の1月1日であれば、20050101としたい.レースはその後の情報で切り分けられるのでそのまま
            dateList.append((year*10000+month*100+day)*100)
            data_list = (year*10000+month*100+day)*100
            race_data_list = []
            name = name_list_in_race[0][i]
            race_common_data = [
                        umaban_list_in_race[0][0],  # 目的変数は1着の馬番号
                        str(data_list) ,
                        str(race_name),
                        str(place),
                        class_list_in_race,
                        number_of_horses,
                        distance_list ,
                        condition_list,
            ]
            race_data = [name, 
                        umaban_list_in_race[0][i],    
                        horse_age_list[0][i], 
                        horse_sex_list[0][i],
                        weight_list_in_race[0][i],
                        weight_change_list_in_race[0][i],
                        handi_list_in_race[0][i],
                        jocky_list_in_race[0][i], 
                        odds_list_in_race[0][i],
                        goal_number_list_in_race[0][i]] # goalは目的変数なので最後においておく
            race_data_list += race_common_data
            race_data_list += race_data
            train_data_total_frame.append(race_data_list)
# columnを作成
column_list = []
race_comon_column = ["target_no1_umaban",
                    "date",
                    "race_name",
                    "place",
                    "class_list_in_race",
                    "number_of_horses",
                    "distance",
                    "condition"
                    ]
column = ["horse_name_", "umaban", "horse_age", "horse_sex","horse_weight",
                "weight_change","handi",
                "jocky","odds", "goal_number"]
column_list =race_comon_column + column 
one_race_horse_data = pd.DataFrame(train_data_total_frame, columns=column_list)

# データフレームをCSVに書き出し
one_race_horse_data.to_csv(train_data_path_year +"train_data_sorted" + "_horse_standard_" + str(yearStart) + "_" + str(yearEnd)+ ".csv", index=True, header=True)
# sys.exit()
print("finish to write train csv data")
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

# 馬の過去レースデータが欲しい場合はrequest_horse_past_dataをTrueにする
if request_horse_past_data:
    pass
else:
    sys.exit()
    pass

data = sorted(data, key = lambda x: x[14],reverse = True)#日付が大きい順番に並べる。理由は次のループで、馬ごとに新しい順に馬のレース順位を格納するため
'''
data
第一指数：全レース数
第二指数：0~28でレースの情報
'''
# 0~28の情報は以下の通り
# 0:馬名
# 1:騎手
# 2:馬番
# 3:着順
# 4:走破時間
# 5:オッズ
# 6:通過
# 7:体重
# 8:体重変化
# 9:性
# 10:年齢
# 11:斤量
# 12:上がり
# 13:人気
# 14:レース名
# 15:日付
# 16:競馬場
# 17:クラス
# 18:芝ダート
# 19:距離
# 20:回り
# 21:馬場状態
# 22:単勝
# 23:複勝
# 24:枠連
# 25:馬連
# 26:ワイド
# 27:馬単
# 28:三連複
# 29:三連単

# "[['テイエムヒスイ', 'シゲルダイノウカイ', 'ヤマニンデクスター', 'アルカライズ', 'ウォーターフロント', 'スズカイエロー', 'サクラモサ', 'インザリピート', 'ワンセカンドキス', 'スイートゴールド'],
#  ['秋山真一', '小原義之', '四位洋文', '横山典弘', '松田大作', '蛯名正義', '武幸四郎', '松永幹夫', '宮崎光行', '藤岡佑介'],
#   ['5', '1', '8', '10', '6', '3', '7', '4', '9', '2'], 
#   ['1:31.3', '1:31.3', '1:31.4', '1:31.5', '1:31.6', '1:31.7', '1:31.8', '1:32.2', '1:32.4', None], 
#   ['3.8', '7.0', '18.6', '5.0', '88.1', '2.3', '8.9', '74.4', '81.6', '---'],
#    ['1-2-2', '2-1-1', '9-7-7', '2-3-3', '7-7-7', '5-3-5', '4-3-3', '6-3-5', '7-7-9', None],
#     ['432(-18)', '462(+4)', '438(-12)', '466(-10)', '492(+6)', '500(-2)', '476(+6)', '448(-8)', '480(-14)', '計不'],
#      ['牝2', '牡2', '牡2', '牡2', '牡2', '牡2', '牡2', '牝2', '牝2', '牝2'], 
#      ['54', '54', '54', '54', '54', '54', '54', '54', '54', '53'], 
#      ['37.5', '37.6', '37.1', '37.5', '37.2', '37.7', '37.8', '38.1', '38.0', None], 
#      ['1', '7', '8', '6', '3', '7', '4', '8', '2', None]]",
#      "[['2歳未勝利'], ['2005年8月13日'], ['1回札幌1日目'], ['2歳未勝利'], ['芝'], ['1500'], ['右'], ['良'], ['晴']]",
#      "[['5', '380'], ['5', '200', '1', '190', '8', '430'], ['1 - 5', '1,290'], ['1 - 5', '540', '5 - 8', '1,110', '1 - 8', '1,330'], ['5 → 1', '2,480'], ['1 - 5 - 8', '5,230'], ['1 - 5 - 8', '5,230']]"
print(data[0][0])
# dataの情報を可視化
print("レース数：",len(data))
print("馬数：",len(data[0][0]))
print("データ数：",len(data[0][0][0]))
print("データ：",data[0][0][0])
# print("データ：",data[0][0][1])

#前走のインデックスのリストを生成する
dataGet = 20000#何レース分のデータを取得するか
pastRaces = 6000#過去何レース調べるか
pastResults = 5#前走何レースを参考にするか
lenData = len(data) # レース数

assume_name = ["アフロビート","グランデスパーダ","ルーラーリッチ","ノーブルヴィクター","カイザーブリッツ","インナーサンクタム","サウザンパンチ","マイショウチャン","サノノウォーリア","リッチハンター","レーガンテソーロ","サイタブラウン","トレジャートレイル","ジェイケイファイン","ミサイルビスケッツ","シゲルタイムフライ"]
dataGet = len(data)

# 過去のレース情報の書き出しファイルパス
csv_path = '/mnt/c/Users/hayat/Desktop/keiba_analysis/data_for_train/horse_index/'
if not os.path.exists(csv_path):
    os.mkdir(csv_path)
# 過去のレース情報の書き出しファイルを作成
with open(csv_path + str(yearStart)+"_"+str(yearEnd)+'_index_new_train_data.csv', 'w', newline='',encoding="shift_jis") as f:
    csv.writer(f).writerow(["馬名","騎手","馬番","着順","走破時間","オッズ","通過","体重","体重変化","性","年齢","斤量","上がり","人気","レース名","日付","競馬場","クラス","芝ダート","距離","回り","馬場状態","単勝","複勝","枠連","馬連","ワイド","馬単","三連複","三連単"])

# すでにサーチ済みの馬であればスキップする
horse_name_list = []
for for_races in tqdm.tqdm(range(dataGet)):
     # 過去何レース分のデータを取得するか。現在探査クレーン番号からpastRaces(6000)レースまでを見るか、設定レーンの最大分まで見るかを設定。
    var_min = min([lenData,for_races+pastRaces])
    #馬の数、0はnameListを示す
    for for_horses in range(len(data[for_races][0])):

        #そのレースの馬の名前
        horse_name = data[for_races][0][for_horses] 
        #何レース前で何着かを記録する
        horse_past_achive = [] 
        # horse_past_achiveに馬の名前を記録する
        horse_past_achive.append(horse_name)
        # horse_name_listに含まれている馬であればスキップする
        if horse_name in horse_name_list:
            print("すでにサーチ済みの馬です。")
            print("馬名:",horse_name)
            continue

        #ここのレースから前で馬の過去レース情報をサーチ
        for  past_race_number in range(for_races+1,var_min,1):
            #for_racesの次のレースから、探索したいレース分までのレース番号の馬名をserch_horse_name_listに格納
            for serch_horse_name_list in range(len(data[past_race_number][0])): 
                # horse_name(実績を調べたい)馬名が過去のレースで一致したら
                if horse_name == data[past_race_number][0][serch_horse_name_list]: 
                    # その馬の過去データとして残っているのは data[past_race_number][X][serch_horse_name_list] であるXには該当馬のデータが入っている
                    # 基準日に対して以下の情報をリストで記録する
                    # 1:騎手
                    # 2:馬番
                    # 3:着順
                    # 4:走破時間
                    # 5:オッズ
                    # 6:通過
                    # 7:体重
                    # 8:体重変化
                    # 9:性
                    # 10:年齢
                    # 11:斤量
                    # 12:上がり
                    # 13:人気
                    # 14:レース名
                    # 15:日付
                    # 16:競馬場
                    # 17:クラス
                    # 18:芝ダート
                    # 19:距離
                    # 20:回り
                    # 21:馬場状態
                    # 22:単勝
                    # 23:複勝
                    # 24:枠連
                    # 25:馬連
                    # 26:ワイド
                    # 27:馬単
                    # 28:三連複
                    # 29:三連単
                    add_data_number_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]
                    # add_data_number_listのデータをhorse_past_achiveに追加
                    for add_data_number in add_data_number_list:
                        # print(f"Debug: data[{past_race_number}][{add_data_number}] = {data[past_race_number][add_data_number]}")
                        # add_data_number_listが14はint型なのでそのまま追加
                        int_type_list = [14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]
                        if add_data_number in int_type_list:
                            horse_past_achive.append(data[past_race_number][add_data_number])
                        else:
                            if isinstance(data[past_race_number][add_data_number], list) or isinstance(data[past_race_number][add_data_number], dict):
                                try:
                                    horse_past_achive.append(data[past_race_number][add_data_number][serch_horse_name_list])
                                except IndexError:
                                    print(data[past_race_number][add_data_number])
                                    print(data[past_race_number][0])

                            else:
                                print(f"Warning: Unexpected data type at data[{past_race_number}][{add_data_number}]")
                                # データがずれないようにNoneをappendしておく
                                horse_past_achive.append(None)
                    # 過去のレース情報をcsvに書き出し
                    with open(csv_path + str(yearStart)+"_"+str(yearEnd)+'_index_new_train_data_add_goal_number.csv', 'a', newline='',encoding="shift_jis") as f:
                        csv.writer(f).writerow(horse_past_achive)
                    # print("馬過去データ追加完了馬名:", horse_name)
            #リストの中身が規定の数越えたら終了する
            if len(horse_past_achive) >= pastResults:
                print("馬過去データpastResults分収集完了,次の馬に行きます。")
                # horse_name_listに馬の名前を記録する
                horse_name_list.append(horse_name)
                break
        # 馬サーチの最後の処理でhorse_name_listに馬の名前を記録する
        horse_name_list.append(horse_name)

# svg_path = '/mnt/c/Users/hayat/Desktop/keiba_analysis/data_for_train/horse_index/'
# if not os.path.exists(svg_path):
#     os.mkdir(svg_path)

# with open(svg_path + str(yearStart)+"_"+str(yearEnd)+'_index_test.csv', 'w', newline='',encoding="shift_jis") as f:
#     csv.writer(f).writerows(pastIndexList)