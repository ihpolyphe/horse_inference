import warnings
from sklearn.svm import SVC, LinearSVC
from sklearn import multiclass
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import classification_report, f1_score, confusion_matrix
import seaborn as sns
import lightgbm as lgb
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.utils.class_weight import compute_sample_weight
import scipy.stats
from sklearn.datasets import load_breast_cancer
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
import tqdm


# オッズの差分を計算して新しい特徴量として追加
def add_odds_differences_for_inference(df):
    sorted_df = df.sort_values('odds')
    if len(sorted_df) >= 3:
        odds_1 = sorted_df.iloc[0]['odds']
        odds_2 = sorted_df.iloc[1]['odds']
        odds_3 = sorted_df.iloc[2]['odds']
        df['odds_diff-1-2'] = odds_1 - odds_2
        df['odds_diff-1-3'] = odds_1 - odds_3
    else:
        df['odds_diff-1-2'] = None
        df['odds_diff-1-3'] = None
    return df

def preprocess_for_inference(inference_data):
    inference_data_answer = inference_data["goal_number"]
    inference_data = inference_data.drop("goal_number", axis=1)

    # 学習データとカラム名を統一する
    # 枠 番は枠番に変換する
    inference_data = inference_data.rename(columns={'枠 番':'枠番'})
    # 馬 番は馬番に変換する
    inference_data = inference_data.rename(columns={'馬 番':'馬番'})
    # 人 気は人気に変換する
    inference_data = inference_data.rename(columns={'人 気':'人気'})
    # 斤 量は斤量に変換する
    inference_data = inference_data.rename(columns={'斤 量':'斤量'})
    # タイムはタイム_yに変換する
    inference_data = inference_data.rename(columns={'タイム':'タイム_y'})
    # 天 気は天気に変換する
    inference_data = inference_data.rename(columns={'天 気':'天気'})
    # 頭 数は頭数に変換する
    inference_data = inference_data.rename(columns={'頭 数':'頭数'})
    # オ ッ ズ はオッズに変換する
    inference_data = inference_data.rename(columns={'オ ッ ズ':'オッズ'})
    # 馬 場は馬場に変換する
    inference_data = inference_data.rename(columns={'馬 場':'馬場'})
    # 騎乗 回数は騎乗回数に変換する
    inference_data = inference_data.rename(columns={'騎乗 回数':'騎乗回数'})
    # 重賞 出走は重賞出走に変換する
    inference_data = inference_data.rename(columns={'重賞 出走':'重賞出走'})
    # 重賞 勝利は重賞勝利に変換する
    inference_data = inference_data.rename(columns={'重賞 勝利':'重賞勝利'})

    # 学習データとの共通処理
    # タイム_yは1:34.0のような形式なので、秒に変換する
    # nanの場合は100に変換する
    # 'タイム_y'列の値を文字列に変換し、NaN値を無視して処理を行う
    inference_data['タイム_y'] = inference_data['タイム_y'].astype(str).apply(
        lambda x: int(x.split(':')[0]) * 60 + float(x.split(':')[1]) if ':' in x else np.nan
    )

    # 'ペース'列の値を文字列に変換し、NaN値を無視して処理を行う
    inference_data['pace1'] = inference_data['ペース'].astype(str).apply(
        lambda x: float(x.split('-')[0]) if '-' in x else np.nan
    )
    inference_data['pace2'] = inference_data['ペース'].astype(str).apply(
        lambda x: float(x.split('-')[1]) if '-' in x else np.nan
    )

    # 馬体重_yは480(+2)のような形式なので、体重と増減を分ける
    # '馬体重'列の値を文字列に変換し、'計不'を'500(0)'に置き換える
    inference_data['馬体重'] = inference_data['馬体重'].astype(str).replace('計不', '500(0)')

    # 'horse_weight_y'列を作成し、'馬体重'列の値を処理
    inference_data['horse_weight_y'] = inference_data['馬体重'].apply(
        lambda x: int(x.split('(')[0]) if '(' in x else np.nan
    )

    # 'weight_change_y'列を作成し、'馬体重'列の値を処理
    inference_data['weight_change_y'] = inference_data['馬体重'].apply(
        lambda x: int(x.split('(')[1].replace(')', '')) if '(' in x else np.nan
    )

    # '連対率'列の値を処理し、全角の'％'を半角の'%'に置き換えてからfloatに変換
    # ％しかない場合は暫定で0％に変換する
    # '連対率'列の値を処理し、全角の'％'を半角の'%'に置き換えてからfloatに変換
    inference_data['連対率'] = inference_data['連対率'].apply(
        lambda x: float(x.replace('％', '')) if isinstance(x, str) and x.strip() != '' else 0.0
    )

    # '勝率'列の値を処理し、全角の'％'を半角の'%'に置き換えてからfloatに変換
    inference_data['勝率'] = inference_data['勝率'].apply(
        lambda x: float(x.replace('％', '')) if isinstance(x, str) and x.strip() != '' else 0.0
    )
    
    # '複勝率'列の値を処理し、全角の'％'を半角の'%'に置き換えてからfloatに変換
    inference_data['複勝率'] = inference_data['複勝率'].apply(
        lambda x: float(x.replace('％', '')) if isinstance(x, str) and x.strip() != '' else 0.0
    )
    # 1/オッズを計算して新しい特徴量として追加
    inference_data['odds_inv'] = 1 / inference_data['オッズ']

    # クエリを使用してオッズの特長量をエンジニアリング
    # 1 オッズを対数変換
    inference_data["log_odds"] = np.log1p(inference_data["odds"])

    # 2 同一レースidにおけるオッズのmin-max正規化
    inference_data["normalized_odds"] = (inference_data["odds"] - inference_data["odds"].min()) / (inference_data["odds"].max() - inference_data["odds"].min())
    # 3 zスコア標準化
    inference_data["zscore_odds"] = (inference_data["odds"] - inference_data["odds"].mean()) / inference_data["odds"].std()

    # 4オッズの順位
    inference_data["odds_rank"] = inference_data["odds"].rank(ascending=False)

    # 5 レースごとのオッズのばらつき
    inference_data["odds_std"] = inference_data["odds"].std()

    inference_data_odds = inference_data["odds"]

    # odds_inv = 1 / inference_data["odds"]
    inference_data["1/オッズ"] = 1 / inference_data["odds"]

    # 前処理用の適当なrace_idを追加
    inference_data_race_id = ["test"] * len(inference_data)
    return inference_data, inference_data_odds, inference_data_race_id,inference_data_answer

def calculate_score_diff(df, modelname):
    score_diff = []
    for race_id, group in df.groupby('race_id'):
        sorted_group = group.sort_values(f'予測スコア({modelname})', ascending=False)
        if len(sorted_group) >= 2:
            score_1 = sorted_group.iloc[0][f'予測スコア({modelname})']
            score_2 = sorted_group.iloc[1][f'予測スコア({modelname})']
            diff = score_1 - score_2
            score_diff.extend([diff] * len(group))
        else:
            score_diff.extend([None] * len(group))
    return score_diff

def prediction_print(df_prediction_test_ranking, optimal_threshold_lambdarank, optimal_threshold_ranknet, optimal_threshold_pairwise):
    # 予測スコアの差を計算
    df_prediction_test_ranking['score_diff_lambdarank'] = calculate_score_diff(df_prediction_test_ranking, 'lambdarank')
    df_prediction_test_ranking['score_diff_RankNet'] = calculate_score_diff(df_prediction_test_ranking, 'RankNet')
    df_prediction_test_ranking['score_diff_Pairwise'] = calculate_score_diff(df_prediction_test_ranking, 'Pairwise')
    # 閾値を適用して1位を予測
    df_prediction_test_ranking = apply_threshold(df_prediction_test_ranking, 'lambdarank', optimal_threshold_lambdarank)
    df_prediction_test_ranking = apply_threshold(df_prediction_test_ranking, 'RankNet', optimal_threshold_ranknet)
    df_prediction_test_ranking = apply_threshold(df_prediction_test_ranking, 'Pairwise', optimal_threshold_pairwise)

    # 予測結果{modelname}の中で1がある場合はその情報を出力
    if df_prediction_test_ranking['予測結果(lambdarank)'].sum() > 0:
        print(f'\033[92m1位と予測した数(lambdarank): {df_prediction_test_ranking["予測結果(lambdarank)"].sum()}\033[0m')
        print(df_prediction_test_ranking[df_prediction_test_ranking['予測結果(lambdarank)'] == 1])
        # その時のほかモデルの1位と2位のスコアの差と閾値を出力
        print(f'RankNet:1位と予測した時の2位とのスコアの差: {df_prediction_test_ranking["score_diff_RankNet"].values[0]}')
        print(f'RankNet:閾値: {optimal_threshold_ranknet}')
        print(f'Pairwise:1位と予測した時の2位とのスコアの差: {df_prediction_test_ranking["score_diff_Pairwise"].values[0]}')
        print(f'Pairwise:閾値: {optimal_threshold_pairwise}')
        # 各特長 (condition, weather, distance, ground_state)を出力
        print(f"distance: {df_prediction_test_ranking['distance'].values[0]}")
        if df_prediction_test_ranking['distance'].values[0] >= 2000:
            print("\033[34m距離は2000m以上の時正答率ぐんと上がる\033[0m")
        else:
            print("スコアは高いけど、距離が2000m未満")
        print(f"condition: {df_prediction_test_ranking['condition'].values[0]}")
        if df_prediction_test_ranking['condition'].values[0] == 1:
            print("\033[34mconditionは1なので正答率高い\033[0m")
        else:
            print("スコアは高いけど、conditionが1以外")
        print(f"weather: {df_prediction_test_ranking['weather'].values[0]}")
        if df_prediction_test_ranking['weather'].values[0] ==1:
            print("\033[34mweatherは0なので正答率高い\n\033[0m")
        else:
            print("スコアは高いけど、weatherが0以外")
        print(f"ground_state: {df_prediction_test_ranking['ground_state'].values[0]}")


    if df_prediction_test_ranking['予測結果(RankNet)'].sum() > 0:
        print(f'\033[94m1位と予測した数(RankNet): {df_prediction_test_ranking["予測結果(RankNet)"].sum()}\033[0m')
        print(df_prediction_test_ranking[df_prediction_test_ranking['予測結果(RankNet)'] == 1])
        # その時のほかモデルの1位と2位のスコアの差と閾値を出力
        print(f'lambdarank:1位と予測した時の2位とのスコアの差: {df_prediction_test_ranking["score_diff_lambdarank"].values[0]}')
        print(f'lambdarank:閾値: {optimal_threshold_lambdarank}')
        print(f'Pairwise:1位と予測した時の2位とのスコアの差: {df_prediction_test_ranking["score_diff_Pairwise"].values[0]}')
        print(f'Pairwise:閾値: {optimal_threshold_pairwise}')
        # 各特長 (condition, weather, distance, ground_state)を出力
        print(f"distance: {df_prediction_test_ranking['distance'].values[0]}")
        if df_prediction_test_ranking['distance'].values[0] >= 2000:
            print("\033[34m距離は2000m以上の時正答率ぐんと上がる\033[0m")
        else:
            print("スコアは高いけど、距離が2000m未満")
        print(f"condition: {df_prediction_test_ranking['condition'].values[0]}")
        if df_prediction_test_ranking['condition'].values[0] !=3:
            print("\033[34mconditionは3以外の時正答率高い\033[0m")
        else:
            print("スコアは高いけど、conditionが3なので微妙")
        print(f"weather: {df_prediction_test_ranking['weather'].values[0]}")
        if df_prediction_test_ranking['weather'].values[0] !=0:
            print("\033[34mweatherは0以外の時正答率高い\n\033[0m")
        else:
            print("スコアは高いけど、weatherが0なので微妙")
        print(f"ground_state: {df_prediction_test_ranking['ground_state'].values[0]}")

    if df_prediction_test_ranking['予測結果(Pairwise)'].sum() > 0:
        print(f'\033[93m1位と予測した数(Pairwise): {df_prediction_test_ranking["予測結果(Pairwise)"].sum()}\033[0m')
        print(df_prediction_test_ranking[df_prediction_test_ranking['予測結果(Pairwise)'] == 1])
        # その時のほかモデルの1位と2位のスコアの差と閾値を出力
        print(f'lambdarank:1位と予測した時の2位とのスコアの差: {df_prediction_test_ranking["score_diff_lambdarank"].values[0]}')
        print(f'lambdarank:閾値: {optimal_threshold_lambdarank}')   
        print(f'RankNet:1位と予測した時の2位とのスコアの差: {df_prediction_test_ranking["score_diff_RankNet"].values[0]}')
        print(f'RankNet:閾値: {optimal_threshold_ranknet}')
        # 各特長 (condition, weather, distance, ground_state)を出力
        print(f"condition: {df_prediction_test_ranking['condition'].values[0]}")
        if df_prediction_test_ranking['condition'].values[0] != 2:
            print("\033[34mconditionは2以外の時正答率高い\033[0m")
        else:
            print("スコアは高いけど、conditionが2なので微妙")
        print(f"weather: {df_prediction_test_ranking['weather'].values[0]}")
        if df_prediction_test_ranking['weather'].values[0] == 0:
            print("\033[34mweatherは0の時めっちゃ正答率高い\n\033[0m")
        else:
            print("スコアは高いけど、weatherが0以外(微妙ではない)")
        print(f"distance: {df_prediction_test_ranking['distance'].values[0]}")
        if df_prediction_test_ranking['distance'].values[0] == 1600:
            print("\033[34m距離は1600mの時正答率ぐんと上がる\033[0m")
        elif df_prediction_test_ranking['distance'].values[0] == 1700:
            print("\033[34m距離は1700mの時正答率ぐんと上がる\033[0m")
        elif df_prediction_test_ranking['distance'].values[0] >= 2000:
            print("\033[34m距離は2000m以上の時正答率ぐんと上がる\033[0m")
        else:
            print("スコアは高いけど、距離が2000m未満")
        print(f"ground_state: {df_prediction_test_ranking['ground_state'].values[0]}")
        if df_prediction_test_ranking['ground_state'].values[0] != 0:
            print("\033[34mground_stateは0以外の時正答率高い\033[0m")
        else:
            print("スコアは高いけど、ground_stateが0の時は微妙")
        return df_prediction_test_ranking

def add_prediction_info(df_prediction_test_ranking):
    buy_candidates_all_positive = df_prediction_test_ranking[
        (df_prediction_test_ranking["予測順位(lambdarank)"] == 1) &
        (df_prediction_test_ranking["予測順位(RankNet)"] == 1) &
        (df_prediction_test_ranking["予測順位(Pairwise)"] == 1) &
        (df_prediction_test_ranking["予測スコア(lambdarank)"] > 0) &
        (df_prediction_test_ranking["予測スコア(RankNet)"] > 0) &
        (df_prediction_test_ranking["予測スコア(Pairwise)"] > 0)
    ]

    # 1つのモデルのスコアがマイナスでも他のモデルのスコアが0以上で1着のものをフィルタリング
    buy_candidates_one_negative = df_prediction_test_ranking[
        ((df_prediction_test_ranking['予測順位(lambdarank)'] == 1) & (df_prediction_test_ranking['予測スコア(lambdarank)'] > 0) &
        (df_prediction_test_ranking['予測順位(Pairwise)'] == 1) & (df_prediction_test_ranking['予測スコア(Pairwise)'] > 0) &
        (df_prediction_test_ranking['予測順位(RankNet)'] == 1) & (df_prediction_test_ranking['予測スコア(RankNet)'] <= 0)) |
        ((df_prediction_test_ranking['予測順位(lambdarank)'] == 1) & (df_prediction_test_ranking['予測スコア(lambdarank)'] > 0) &
        (df_prediction_test_ranking['予測順位(Pairwise)'] == 1) & (df_prediction_test_ranking['予測スコア(Pairwise)'] <= 0) &
        (df_prediction_test_ranking['予測順位(RankNet)'] == 1) & (df_prediction_test_ranking['予測スコア(RankNet)'] > 0)) |
        ((df_prediction_test_ranking['予測順位(lambdarank)'] == 1) & (df_prediction_test_ranking['予測スコア(lambdarank)'] <= 0) &
        (df_prediction_test_ranking['予測順位(Pairwise)'] == 1) & (df_prediction_test_ranking['予測スコア(Pairwise)'] > 0) &
        (df_prediction_test_ranking['予測順位(RankNet)'] == 1) & (df_prediction_test_ranking['予測スコア(RankNet)'] > 0))
    ]

    # スコアがすべて正のとき1つのモデルの順位が1でない場合をフィルタリング
    buy_candidates_one_not_first = df_prediction_test_ranking[
        ((df_prediction_test_ranking['予測順位(lambdarank)'] == 1) & (df_prediction_test_ranking['予測スコア(lambdarank)'] > 0) &
        (df_prediction_test_ranking['予測順位(Pairwise)'] == 1) & (df_prediction_test_ranking['予測スコア(Pairwise)'] > 0) &
        (df_prediction_test_ranking['予測順位(RankNet)'] != 1) & (df_prediction_test_ranking['予測スコア(RankNet)'] > 0)) |
        ((df_prediction_test_ranking['予測順位(lambdarank)'] == 1) & (df_prediction_test_ranking['予測スコア(lambdarank)'] > 0) &
        (df_prediction_test_ranking['予測順位(Pairwise)'] != 1) & (df_prediction_test_ranking['予測スコア(Pairwise)'] > 0) &
        (df_prediction_test_ranking['予測順位(RankNet)'] == 1) & (df_prediction_test_ranking['予測スコア(RankNet)'] > 0)) |
        ((df_prediction_test_ranking['予測順位(lambdarank)'] != 1) & (df_prediction_test_ranking['予測スコア(lambdarank)'] > 0) &
        (df_prediction_test_ranking['予測順位(Pairwise)'] == 1) & (df_prediction_test_ranking['予測スコア(Pairwise)'] > 0) &
        (df_prediction_test_ranking['予測順位(RankNet)'] == 1) & (df_prediction_test_ranking['予測スコア(RankNet)'] > 0))
    ]
    # 買い目として出力
    if not buy_candidates_all_positive.empty:
        print("Buy candidates (all positive scores and all ranks 1):")
        print(buy_candidates_all_positive)
    elif not buy_candidates_one_negative.empty:
        print("Buy candidates (one negative score but all ranks 1):")
        print(buy_candidates_one_negative)
    elif not buy_candidates_one_not_first.empty:
        print("Buy candidates (all positive scores but one rank not 1):")
        print(buy_candidates_one_not_first)
    else:
        print("No buy candidates found.")

def apply_threshold(df, modelname, threshold):
    # 予測結果を閾値で分類
    # 予測スコアが閾値以上の場合かつ予測順位が1の時は1、それ以外は0
    df[f'予測結果({modelname})'] = ((df[f'score_diff_{modelname}'] >= threshold) & (df[f'予測順位({modelname})'] == 1)).astype(int)
    return df