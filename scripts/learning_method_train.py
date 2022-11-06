import pandas as pd
import numpy as np
import tqdm
import csv
import os


def index(var_pastIndex):
    #第一インデックス：レース数、　第二インデックス：馬番、　第三インデックス：過去何レース前で何着か
    pastIndex = []
    for for_races in range(len(var_pastIndex)):
        var0 = var_pastIndex[for_races]
        var_listUmaban = []
        for for_umaban in range(len(var0)):
            var1 = var0[for_umaban]
            # nanはfloatなのでパス、それ以外を処理
            if type(var1) is str:
                var2 = var1.replace(", [","A").replace("[","").replace("]","").split("A")
            else:
                continue
            var_listPast = []
            for for_past in range(len(var2)):
                try:
                    var_listPast.append(np.array(var2[for_past].replace(",","").split(" "),dtype=np.int64))
                except ValueError:#前走がない時、空のリストで埋める
                    var_listPast.append([])
            var_listUmaban.append(var_listPast)
        pastIndex.append(var_listUmaban)
    return pastIndex

def makeExplainList_as_horse_for_train(n,var_addNum, pastIndex, data, need, decreaseRate, otherNeed,xListBefore,yListBefore):#n番目のレースの説明変数のリストを作る、後々のことを考えて関数化
    var_data = data[n]
    allNum = len(var_data[0])
    xNList = []
    yNList = []
    horse_name_list = []

    for nn in range(allNum):#nnは出走馬数に対応
        if len(pastIndex[n][nn][0]) == 0: #過去データが全くない馬が1頭でもいるか
            break
        if len(pastIndex[n][nn]) <= 0:#過去データが2以下の馬が1頭でもいるか
            break
        if allNum<var_addNum+2:#var_addNum+1いないと説明変数が足りないため
            break
    else:#過去データ数が条件を満たしていると確認した時
        #馬番、年齢、性、体重、体重増減、斤量、クラス、出走馬数、距離、芝・ダ、過去５レース着順、過去５レースタイム、過去５レースの上がり、

        #以下は簡略化のため省略
        #過去５レースの着差、過去５レースの間隔、過去５レースの距離変化、他の馬で平均タイム上位5頭の前走タイム、
        #他の馬で平均タイム上位5頭の前走クラス
        #馬数でループ
        for nn in range(allNum):
            var_list = []
            var = var_data[6][nn]
            if var == 0:
                var = 480
            horse_name = var_data[0][nn]
            horse_number = var_data[2][nn]
            horse_age = var_data[9][nn]
            horse_sex = var_data[8][nn]
            horse_weight = var
            horse_weight_change = var_data[7][nn]
            weight = var_data[10][nn]
            class_ = var_data[16]
            total_number = allNum
            distance = var_data[18]
            condition = var_data[17]
            win_rate, rentairitu, hukusyourate =get_jockey_rate(var_data[1][nn])

            counter = 0#ダミーの枚数
            rank = []
            time = []
            throught = []
            update = []
            rank_difference = []
            day_elapsed = []
            change_distance = []
            for nnn in range(need):#nnnは過去5レースに対応
                try:
                    # n レース番号、nn そのレースでの着順、nnn 何回前のレースか、　0？？
                    var_ind = pastIndex[n][nn][nnn][0]
                    var_chakujun = pastIndex[n][nn][nnn][1]
                    var_data1 = data[var_ind]
                    var_allNum = len(data[var_ind][0])
                    if nnn == 0:
                        pass
                except IndexError:#ちなみにnnnはXXX以上であることは確定している
                    counter += 1
                    try:
                        var_ind = pastIndex[n][nn][counter-1][0]#最近のデータ、最近2番目のデータで補完
                        var_chakujun = pastIndex[n][nn][counter-1][1]
                        var_data1 = data[var_ind]
                        var_allNum = len(data[var_ind][0])
                    except IndexError:
                        var_ind = pastIndex[n][nn][0][0]#最近のデータで補完
                        var_chakujun = pastIndex[n][nn][0][1]
                        var_data1 = data[var_ind]
                        var_allNum = len(data[var_ind][0])
                
                rank.append(var_chakujun)
                time.append(var_data1[3][var_chakujun]*decreaseRate**counter)#タイム
                throught.append(var_data1[5][var_chakujun])#通過
                update.append(var_data1[11][var_chakujun])#上がり
                rank_difference.append(var_data1[3][0]-var_data1[3][var_chakujun])#着差
                day_elapsed.append(var_data[14]-var_data1[14])#前走からの日数
                change_distance.append(var_data[18]-var_data1[18])#距離変化
                
            # 馬ごとの説明変数リスト作成
            horse_explain_list = [horse_number,horse_age,horse_sex,horse_weight,horse_weight_change,weight,class_,total_number,distance,condition,
                                    win_rate,rentairitu,hukusyourate,
                                    rank[0],rank[1],rank[2],rank[3],rank[4],
                                    time[0],time[1],time[2],time[3],time[4],
                                    throught[0],throught[1],throught[2],throught[3],throught[4],
                                    update[0],update[1],update[2],update[3],update[4],
                                    rank_difference[0],rank_difference[1],rank_difference[2],rank_difference[3],rank_difference[4],
                                    day_elapsed[0],day_elapsed[1],day_elapsed[2],day_elapsed[3],day_elapsed[4],
                                    change_distance[0],change_distance[1],change_distance[2],change_distance[3],change_distance[4],
                                    ]
            xNList.append(horse_explain_list)
            yNList.append(var_data[3][nn])
            horse_name_list.append(horse_name)
        # xListBefore.append(xNList)
        # yListBefore.append(yNList)
        # oddsListBefore.append(var_data[4])
        # oddsListBeforeFuku.append(var_data[23])
        # umarenListBefore.append(var_data[24])
        # umatanListBefore.append(var_data[26])
        # sanrentanListBefore.append(var_data[28])
        # sanrenpukuListBefore.append(var_data[27])
        # wideListBefore.append(var_data[25])
        # indexList.append(n)
    # column=["horse_number", "horse_age", "horse_sex","horse_weight","horse_weight_change","weight","class_","total_number",
    #         "distance","condition","rank1","rank2","rank3","rank4","rank5",
    #         "time1","time2","time3","time4","time5",
    #         "throught1","throught2","throught3","throught4","throught5",
    #         "update1","update2","update3","update4","update5",
    #         "rank_difference1","rank_difference2","rank_difference3","rank_difference4","rank_difference5",
    #         "day_elapsed1","day_elapsed2","day_elapsed3","day_elapsed4","day_elapsed5",
    #         "change_distance1","change_distance2","change_distance3","change_distance4","change_distance5"]
    # # データフレームを作成
    # df = pd.DataFrame(xNList, columns=column)
    
    # # CSV ファイル出力
    # df.to_csv("pandas_test.csv")
    return xNList,yNList,horse_name_list

def get_jockey_rate(jokey):
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
    return win_rate,rentairitu,hukusyouritu

def get_train_data(debag_mode,yearStart,yearEnd):
    '''
    data
    第一指数：全レース数
    第二指数：0~28でレースの情報

    return data
    '''
    yearList = np.arange(yearStart, yearEnd+1, 1, int) 
    data=[]

    for for_year in yearList:
        if debag_mode:
            var_path = "/Users/hayat/Desktop/keiba_analysis/scrayping/"+str(for_year)+".csv"
        else:
            var_path = "/mnt/c/Users/hayat/Desktop/keiba_analysis/scrayping/"+str(for_year)+".csv"

        var_data = pd.read_csv(var_path,encoding='shift_jis',header=None)
        data.append(var_data)

    nameList,jockyList,umabanList,timeList,oddsList,passList,weightList,dWeightList,sexList,oldList,handiList,agariList,ninkiList = [],[],[],[],[],[],[],[],[],[],[],[],[]
    umaList = [nameList,jockyList,umabanList,timeList,oddsList,passList,weightList,dWeightList,sexList,oldList,handiList,agariList,ninkiList]

    raceNameList,dateList,courseList,classList,surfaceList,distanceList,rotationList,surCondiList,weatherList = [],[],[],[],[],[],[],[],[]
    infoList=[raceNameList,dateList,courseList,classList,surfaceList,distanceList,rotationList,surCondiList,weatherList]

    tanList,fukuList,umarenList,wideList,umatanList,renpukuList,rentanList = [],[],[],[],[],[],[]
    paybackList = [tanList,fukuList,umarenList,wideList,umatanList,renpukuList,rentanList]
    print("学習フェーズ")
    print("csvからデータ取得")
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

    return data
