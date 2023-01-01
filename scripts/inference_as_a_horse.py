
import pandas as pd
import numpy as np
import tqdm
import datetime
import itertools
from sklearn.model_selection import KFold

from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import cross_validate
import matplotlib.pyplot as plt
import learning_method_inference
import learning_method_train
import os
import glob
import datetime

import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error as mae
"""推論精度向上→騎手を説明変数として追加する。"""
"""タイムのずれを確認する。"""


"""推論精度向上→レースごとにすれば向上するかも？？"""
## Usage  horse_name.pyで推論したいレースの馬名を取得する。
## 同じidにして推論を実行する。

# 学習データ
yearStart = 2005#開始年を入力
yearEnd = 2022#終了年を入力
# 予想したいレースのページID
assume_id = 2022090609

# vscode 使う-> true
debag_mode = False
# リザルトディレクトリの作成
if debag_mode:
    path = os.path.join('/Users/hayat/Desktop/keiba_analysis/',str(assume_id))
else:
    path = os.path.join('/mnt/c/Users/hayat/Desktop/keiba_analysis/',str(assume_id))
if not os.path.exists(path):
    os.mkdir(path)

# 学習に用いるデータの取得
data = learning_method_train.get_train_data(debag_mode,yearStart,yearEnd)

var_name = [ 'c{0:02d}'.format(i) for i in range(18) ]#列名を先に作らないと読み込めない

if debag_mode:
    var_pastIndex = np.array(pd.read_csv("/Users/hayat/Desktop/keiba_analysis/index/"+ str(yearStart)+"_"+str(yearEnd)+'_index.csv',encoding="shift_jis",header=None,names = var_name))
else:
    var_pastIndex = np.array(pd.read_csv("/mnt/c/Users/hayat/Desktop/keiba_analysis/index/"+ str(yearStart)+"_"+str(yearEnd)+'_index.csv',encoding="shift_jis",header=None,names = var_name))


xListBefore = []
yListBefore = []
horse_name_list = []
# 過去のレース戦績を取得する
pastIndex = learning_method_train.index(var_pastIndex)
var_addNum = 5#他の馬のタイム上位何頭分の過去データを説明変数に加えるか
decreaseRate = 1#ダミーへのペナルティー
need = 5 #前何走使うか
otherNeed = 1#他の馬は前何走使うか

for n in tqdm.tqdm((range(len(pastIndex)))):#nはレース数に対応
    # 説明変数を取得する
    # 説明変数= [馬番,年齢,性別,体重,体重変更量,騎手の重さ,クラス,総馬数,距離,ダートor芝,騎手勝率、連帯率、複勝率、
                                # 過去五戦の順位rank[0],rank[1],rank[2],rank[3],rank[4],
                                # 過去五戦の、、、time[0],time[1],time[2],time[3],time[4],
                                # throught[0],throught[1],throught[2],throught[3],throught[4],
                                # update[0],update[1],update[2],update[3],update[4],
                                # rank_difference[0],rank_difference[1],rank_difference[2],rank_difference[3],rank_difference[4],
                                # day_elapsed[0],day_elapsed[1],day_elapsed[2],day_elapsed[3],day_elapsed[4],
                                # change_distance[0],change_distance[1],change_distance[2],change_distance[3],change_distance[4],]
    xNList,yNList,horse_name = learning_method_train.makeExplainList_as_horse_for_train(n,var_addNum, pastIndex, data, need, decreaseRate, otherNeed, xListBefore, yListBefore)
    xListBefore.append(xNList)
    horse_name_list.append(horse_name)
    yListBefore.append(yNList)

xList = list(itertools.chain.from_iterable(xListBefore))
yList = list(itertools.chain.from_iterable(yListBefore))
horse_name_list = list(itertools.chain.from_iterable(horse_name_list))

ratio = 0.4#テストに回す割合を入力
numTrain = int(len(xList)*ratio)
xTrain = xList[numTrain:]
yTrain = yList[numTrain:]
horse_name_list = horse_name_list[:numTrain]
xTest = xList[:numTrain]
yTest = yList[:numTrain]
xTrainDf = pd.DataFrame(xTrain)
yTrainDf = pd.DataFrame(yTrain)
xTestDf = pd.DataFrame(xTest)
yTestDf = pd.DataFrame(yTest)


# ハイパラ設定
kf = KFold(n_splits=5, shuffle=True, random_state=0)#データをn個に分割する、型はscikitlearnで使うデータ分割方法みたいなやつ

#https://lightgbm.readthedocs.io/en/latest/Parameters.html
# LightGBMのハイパーパラメータを設定
paramsGrid = {
          'learning_rate': [0.01,0.1],#学習率[0.01,0.1,0.001]
            'metric': ["l1"],
          'num_leaves': [20,30,40], #ノードの数
          'reg_alpha': [0,0.5], #L1正則化係数
          'reg_lambda': [0,0.5],#L2正則化係数
          'colsample_bytree': [1], #各決定木においてランダムに抽出される列の割合(大きいほど過学習寄り)、0~1でデフォ1
          'subsample': [0.1], # 各決定木においてランダムに抽出される標本の割合(大きいほど過学習寄り)、0~1でデフォ1
          'subsample_freq': [0],#, # ここで指定したイテレーション毎にバギング実施(大きいほど過学習寄りだが、0のときバギング非実施となるので注意)
          'min_child_samples': [20],# 1枚の葉に含まれる最小データ数(小さいほど過学習寄り)、デフォ20
          'seed': [0],
          'n_estimators': [100]}#, # 予測器(決定木)の数:イタレーション
          #'max_depth': [70,90]} # 木の深さ

paramsList = list(ParameterGrid(paramsGrid))
len(paramsList)

estimatorParams = paramsList#ハイパーパラメータのグリッド
kfLength = kf.get_n_splits()#データを何個に分割して交差検証を行うか
totalSample = len(estimatorParams)*kfLength
counter = 0
estList = []
scoreList = []
estimatorParamsList = []
grid = True#グリッドサーチを行うかどうか

if grid==True:
    print("学習開始")
    for n in tqdm.tqdm(range(len(estimatorParams))):
        var_regressor = lgb.LGBMRegressor(**estimatorParams[n])
        # print(estimatorParams[n])
        CVResults = cross_validate(var_regressor,xTrainDf,np.ravel(yTrainDf),cv=kf, return_estimator=True)#estimatorParams[n]を使用してcrossValidate #結果は長さkfのリスト
        estList.append(CVResults["estimator"][0])#どれも同じなので0番目を取った
        var = CVResults["test_score"].mean()
        scoreList.append(var)
        # print("\n" + str(var))
        estimatorParamsList.append(estimatorParams[n])
        counter += kfLength
        # print("\r" + str(counter)+"/" + str(totalSample) + " 完了" , end="")
    var_maxInd = scoreList.index(max(scoreList))#最大の精度のインデックス
    bestEst = estList[var_maxInd]#最大の精度を与える予測器
    bestParam = estimatorParamsList[var_maxInd]
    print(bestParam)
else:
    bestEst = lgb.LGBMRegressor(**estimatorParams[0])

# 学習、検証フェーズ

#最適なハイパーパラメータでトレーニングとテストを行う
bestEst.fit(xTrainDf,np.ravel(yTrainDf))
predict = bestEst.predict(xTestDf)
print("score:",bestEst.score(xTestDf,yTestDf))
print(predict)
#テストデータを使用したときのプロット
fig, ax = plt.subplots(figsize=(5,5))
# plt.xlim(-3,3)
# plt.ylim(-3,3)
ax.set_title('Light GBM')
ax.set_xlabel('Predict')
ax.set_ylabel('Actual')
plt.scatter(predict, yTest, s=1, alpha = 0.1)
# plt.plot(predict, yTest)
# plt.show()
# now = datetime.datetime.now()
# filename = "/mnt/c/Users/hayat/Desktop/keiba_analysis/result_png/validation/" + now.strftime('%Y_%m_%d_%H_%M_%S') + '.jpg'
# plt.savefig(filename)

## ===========推論フェーズ=============
print("推論フェーズ")
var_name_scrayping = [ 'c{0:02d}'.format(i) for i in range(11) ]#列名を先に作らないと読み込めない
var_name_name = [ 'c{0:02d}'.format(i) for i in range(2) ]#列名を先に作らないと読み込めない

for i in tqdm.tqdm(range(1,13,1)):
    print("{}R目推論開始".format(i))
    if debag_mode:
        inference_path = "/Users/hayat/Desktop/keiba_analysis/"+str(assume_id)+"/scrayping_"+str(assume_id)+str(i)+'.csv'
        horse_name_path = "/Users/hayat/Desktop/keiba_analysis/"+str(assume_id)+"/horse_name_"+str(assume_id)+str(i)+'.csv'
    else:
        inference_path = "/mnt/c/Users/hayat/Desktop/keiba_analysis/"+str(assume_id)+"/scrayping_"+str(assume_id)+str(i)+'.csv'
        horse_name_path = "/mnt/c/Users/hayat/Desktop/keiba_analysis/"+str(assume_id)+"/horse_name_"+str(assume_id)+str(i)+'.csv'
    horse_information = np.array(pd.read_csv(inference_path,encoding="utf-8",header=None,names = var_name_scrayping))
    horse_name = np.array(pd.read_csv(horse_name_path,encoding="utf8",dtype=str,header=None,names = var_name_name))
    horse_information_list = np.delete(horse_information,0,1)
    horse_information_list = np.delete(horse_information_list,0,0)
    horse_name = np.delete(horse_name,0,1) #インデント列の削除
    horse_name = np.delete(horse_name,0,0) #0番目の削除
    # 新馬戦は過去情報ないため推論しない
    if horse_information_list[0][6] == "3":
        print("新馬戦のため推論しない")
        continue

    print("推論データ読み出し成功")
    name_goal = []
    name_list = None
    for name in horse_name:
        # print(name)
        name_goal.append(name)

    # for文内のlist平坦化はこっちじゃないとエラー吐かれる
    name_list = [x for row in name_goal for x in row]

    print(name_list)
    # continue
    # 推論したいレースの前走５つのデータ作成
    _,file_name = learning_method_inference.make_past_grades(debag_mode, assume_id, i ,name_list, data, yearStart, yearEnd)

    # file_name = '/Users/hayat/Desktop/keiba_analysis/2022090405/index_20220904052.csv'
   
    var_Index_this_time = np.array(pd.read_csv(file_name,encoding="shift_jis",header=None,names = var_name))

    index_at_this_time = learning_method_train.index(var_Index_this_time)

    # print(index_at_this_time)

    xListBefore_ = []

    # 説明変数作成
    # 説明変数= [馬番,年齢,性別,体重,体重変更量,騎手の重さ,クラス,総馬数,距離,ダートor芝,騎手勝率、連帯率、複勝率、
    #                     rank[0],rank[1],rank[2],rank[3],rank[4],
    #                     time[0],time[1],time[2],time[3],time[4],
    #                     throught[0],throught[1],throught[2],throught[3],throught[4],
    #                     update[0],update[1],update[2],update[3],update[4],
    #                     rank_difference[0],rank_difference[1],rank_difference[2],rank_difference[3],rank_difference[4],
    #                     day_elapsed[0],day_elapsed[1],day_elapsed[2],day_elapsed[3],day_elapsed[4],
    #                     change_distance[0],change_distance[1],change_distance[2],change_distance[3],change_distance[4],
    #                     ]
    xNList_ = learning_method_inference.makeExplainList_as_horse_for_inference(0,var_addNum, index_at_this_time, data, need, decreaseRate, otherNeed, xListBefore, yListBefore,horse_information_list)
    xListBefore_.append(xNList_)

    xList_ = [x for row in xListBefore_ for x in row]

    xTestDf_ = pd.DataFrame(xList_)

    predict_ = bestEst.predict(xTestDf_)
    # print("score:",bestEst.score(xTestDf,yTestDf))
    print(predict_)

    #レースタイムの出力方法
    save_list = []
    for predict_index in range(len(predict_)):
        list = [name_list[predict_index],predict_[predict_index]]
        save_list.append(list)

    column=["horse_name", "inference_horse_time"]
    df = pd.DataFrame(save_list, columns=column)
    df.to_csv(path+"/inference_horse_time_"+str(assume_id)+str(i) +".csv")
