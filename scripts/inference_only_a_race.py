
import pandas as pd
import numpy as np
import tqdm
import datetime
import itertools
from sklearn.model_selection import KFold
import lightgbm as lbg
from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import cross_validate
import matplotlib.pyplot as plt
import learning_method
import os

## Usage  horse_name.pyで推論したいレースの馬名を取得する。
## 同じidにして推論を実行する。

### adjust_for_learning.pyでcsv作成していないようなレースに対する推論ソフト。csvを作っている場合はlearning.pyで推論すること。

# 学習データ
yearStart = 2005#開始年を入力
yearEnd = 2022#終了年を入力
# 予想したいレースのページID
assume_id = 2022050402
# 予想したいレース番号
race_number =3 

# vscode 使う-> true
debag_mode = False

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
'''
data
第一指数：全レース数
第二指数：0~28でレースの情報
'''
var_name = [ 'c{0:02d}'.format(i) for i in range(18) ]#列名を先に作らないと読み込めない

if debag_mode:
    var_pastIndex = np.array(pd.read_csv("/Users/hayat/Desktop/keiba_analysis/index/"+ str(yearStart)+"_"+str(yearEnd)+'_index.csv',encoding="shift_jis",header=None,names = var_name))
else:
    var_pastIndex = np.array(pd.read_csv("/mnt/c/Users/hayat/Desktop/keiba_analysis/index/"+ str(yearStart)+"_"+str(yearEnd)+'_index.csv',encoding="shift_jis",header=None,names = var_name))


xListBefore = []
yListBefore = []
pastIndex = learning_method.index(var_pastIndex)
var_addNum = 5#他の馬のタイム上位何頭分の過去データを説明変数に加えるか
decreaseRate = 1#ダミーへのペナルティー
need = 5 #前何走使うか
otherNeed = 1#他の馬は前何走使うか
    
# 学習データ成型
#「馬番、年齢、性、体重、体重増減、斤量、クラス、出走馬数、距離、芝・ダ、過去５レース着順、過去５レースタイム、
# 過去５レースの上がり、過去５レースの着差、過去５レースの間隔、過去５レースの距離変化、他の馬で平均タイム上位5頭の前走タイム、
# 他の馬で平均タイム上位5頭の前走クラス」
print("make train param list")
for n in tqdm.tqdm((range(len(pastIndex)))):#nはレース数に対応
    learning_method.makeXParamList(n,var_addNum, pastIndex, data, need, decreaseRate, otherNeed, xListBefore, yListBefore)
    # print("\r" + str(n+1)+"/" + str(len(pastIndex)) + " 完了" , end="")

xList = list(itertools.chain.from_iterable(xListBefore))
yList = list(itertools.chain.from_iterable(yListBefore))

ratio = 0.4#テストに回す割合を入力
numTrain = int(len(xList)*ratio)
xTrain = xList[numTrain:]
yTrain = yList[numTrain:]
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
        var_regressor = lbg.LGBMRegressor(**estimatorParams[n])
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
    bestEst = lbg.LGBMRegressor(**estimatorParams[0])

# 学習、検証フェーズ

#最適なハイパーパラメータでトレーニングとテストを行う
bestEst.fit(xTrainDf,np.ravel(yTrainDf))
predict = bestEst.predict(xTestDf)
print("score:",bestEst.score(xTestDf,yTestDf))
print(len(predict))
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
now = datetime.datetime.now()
# filename = "/mnt/c/Users/hayat/Desktop/keiba_analysis/result_png/validation" + now.strftime('%Y_%m_%d_%H_%M_%S') + '.jpg'
# plt.savefig(filename)

#=====================推論フェーズ=============================

print("推論フェーズ")
# 推論したい馬名をインポート

if debag_mode:
    inference_horse_name = np.array(pd.read_csv("/Users/hayat/Desktop/keiba_analysis/race_horse_name/"+ str(assume_id) + ".csv",encoding="shift_jis",header=None,names = var_name))
    inference_path = os.path.join("/Users/hayat/Desktop/keiba_analysis/inference/", str(assume_id))

else:
    inference_horse_name = np.array(pd.read_csv("/mnt/c/Users/hayat/Desktop/keiba_analysis/race_horse_name/"+ str(assume_id) + "_test.csv",encoding="shift_jis",header=None,names = var_name))
    inference_path = os.path.join("/mnt/c/Users/hayat/Desktop/keiba_analysis/inference/", str(assume_id))

# 結果保存ディレクトリを作成
if not os.path.exists(inference_path):
    os.mkdir(inference_path)
inferemce_index = []

print("{}R処理開始".format(race_number))

horse_name = inference_horse_name[race_number]

var_Index_this_time = []
index_at_this_time = []
# nanを削除
horse_name_without_nan = [x for x in horse_name if pd.isnull(x) == False and x != 'nan']
# print ("horse_name{}".format(horse_name_without_nan))

# print (horse_name_without_nan)

# 推論したいレースの前走５つのデータ作成
_,file_name = learning_method.make_past_grades(debag_mode, assume_id, race_number ,horse_name_without_nan, data, yearStart, yearEnd)

# file_name = "/Users/hayat/Desktop/keiba_analysis/index/2022050402/0_20000_2005_2022_index.csv"
var_Index_this_time = np.array(pd.read_csv(file_name[race_number],encoding="shift_jis",header=None,names = var_name))

index_at_this_time = learning_method.index(var_Index_this_time)

# inferemce_index.append(index_at_this_time[i])


var_addNum = 5#他の馬のタイム上位何頭分の過去データを説明変数に加えるか
decreaseRate = 1#ダミーへのペナルティー
need = 5 #前何走使うか
otherNeed = 1#他の馬は前何走使うか
# データ成型
xListBefore = []
yListBefore = []
xList_ = []
print("推論説明変数作成")
# for n in tqdm.tqdm((range(len(inferemce_index)))):#nはレース数に対応
learning_method.makeXParamList(0,var_addNum, index_at_this_time, data, need, decreaseRate, otherNeed, xListBefore, yListBefore)


xList_ = list(itertools.chain.from_iterable(xListBefore))
# yList = list(itertools.chain.from_iterable(yListBefore))

print("推論")
list = []

xTestDf = pd.DataFrame(xList_)
# yTestDf = pd.DataFrame(yTest)

#最適なハイパーパラメータでトレーニングとテストを行う
try:
    predict = bestEst.predict(xTestDf)
except:
    print("説明変数作れなかったので推論できませんでした。")

predict_interpolated = predict
horse_name_write = horse_name_without_nan
while True:
    # print("predict:{}, name:{}".format(len(predict_interpolated),len(horse_name)))
    if (len(horse_name_write)) > len(predict_interpolated):
        predict_interpolated = np.append(predict_interpolated,9999)
    elif (len(horse_name_write)) < len(predict_interpolated):
        horse_name_write.append("補完")
    elif (len(horse_name_write)) == len(predict_interpolated):
        break

    print("{}R推論完了".format(n))

dict = dict(Row2=horse_name_write,Row3=predict_interpolated)
df = pd.DataFrame(data=dict)
# df = pd.DataFrame(predict,assume_name,)
df.to_csv(inference_path + "/"+"raceid_"+str(assume_id)+"_"+str(race_number) +"_result.csv", encoding="shift_jis")




