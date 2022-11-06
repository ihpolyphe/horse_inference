import pandas as pd
import numpy as np
import tqdm
import csv
import os


def make_past_grades(debug, assume_id, i ,target_race, data, yearStart, yearEnd):
    """
    予想馬の前五走の結果を取得
    """
    #前走のインデックスのリストを生成する
    dataGet = 20000#何レース分のデータを取得するか
    pastRaces = 6000#過去何レース調べるか
    pastResults = 5#前走何レースを参考にするか
    pastIndexList = []
    lenData = len(data)
    if len(data) < dataGet:
        dataGet = len(data)
    for for_races in tqdm.tqdm(range(dataGet)):
        var_pastIndexList = []#1レース分の馬柱
        var_min = min([lenData,for_races+pastRaces])
        # for for_horses in range(len(data[for_races][0])):#馬の数、0はnameListを示す
        for for_horses in range(len(target_race)):#馬の数、0はnameListを示す
            var_name = target_race[for_horses]
            # var_name = data[for_races][0][for_horses]
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
    # file_name = '/mnt/c/Users/hayat/Desktop/keiba_analysis/index/sauzi_G3'+str(yearStart)+"_"+str(yearEnd)+'_index.csv'
    if debug:
        file_name = '/Users/hayat/Desktop/keiba_analysis/'+str(assume_id)+"/index_"+str(assume_id)+str(i) +".csv"
        # file_name = '/Users/hayat/Desktop/keiba_analysis/2022050404/index_20220504041.csv'
    else:
        file_name = '/mnt/c/Users/hayat/Desktop/keiba_analysis/'+str(assume_id)+"/index_"+str(assume_id)+str(i) +".csv"
    with open(file_name, 'w', newline='',encoding="shift_jis") as f:
        csv.writer(f).writerows(pastIndexList)
    return pastIndexList, file_name

def makeExplainList_as_horse_for_inference(n,var_addNum, pastIndex, data, need, decreaseRate, otherNeed,xListBefore,yListBefore,horse_information_list):#n番目のレースの説明変数のリストを作る、後々のことを考えて関数化
    """予想馬ごとの説明変数リストの作成"""
    var_data = data[n]
    allNum = len(pastIndex[0])
    xNList = []

    #過去５レースの着差、過去５レースの間隔、過去５レースの距離変化、他の馬で平均タイム上位5頭の前走タイム、
    #他の馬で平均タイム上位5頭の前走クラス
    #馬数でループ
    for nn in range(allNum):
        counter = 0#ダミーの枚数
        rank = []
        time = []
        throught = []
        update = []
        rank_difference = []
        day_elapsed = []
        change_distance = []
        for nnn in range(need):#nnnは過去5レースに対応
            # 過去データがない場合の補完
            # print(len(pastIndex[n][nn][0]))
            if len(pastIndex[n][nn][0]) == 0: #過去データが全くない馬が1頭でもいる時は最下位
                print("nn番目={}の馬の過去情報ないため補完".format(nn))
                rank = [16] * 5    #ないときは適当にn番目データを差し込み
                time = [150] * 5
                throught = [100] * 5
                update = [30] * 5
                rank_difference = [0] * 5
                day_elapsed = [0] * 5
                change_distance = [0] * 5
            
            else:
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
        horse_explain_list = [int(horse_information_list[nn][0]),int(horse_information_list[nn][1]),int(horse_information_list[nn][2]),
                                int(horse_information_list[nn][3]),int(horse_information_list[nn][4]),float(horse_information_list[nn][5]),
                                int(horse_information_list[nn][6]),int(horse_information_list[nn][7]),int(horse_information_list[nn][8]),
                                int(horse_information_list[nn][9]),int(horse_information_list[nn][10]),int(horse_information_list[nn][11]),
                                int(horse_information_list[nn][12]),
                                rank[0],rank[1],rank[2],rank[3],rank[4],
                                time[0],time[1],time[2],time[3],time[4],
                                throught[0],throught[1],throught[2],throught[3],throught[4],
                                update[0],update[1],update[2],update[3],update[4],
                                rank_difference[0],rank_difference[1],rank_difference[2],rank_difference[3],rank_difference[4],
                                day_elapsed[0],day_elapsed[1],day_elapsed[2],day_elapsed[3],day_elapsed[4],
                                change_distance[0],change_distance[1],change_distance[2],change_distance[3],change_distance[4],
                                ]
        xNList.append(horse_explain_list)
            
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
    return xNList
