# 完成ソフト、試作ソフトで用いる共通関数を定義
# 前処理

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
import pickle

def preprocess(train_data, is_ranking=False, is_mlp=False):
    # 不要な特長量であるUnnamed: 0、class_list_in_raceを削除する
    # train_data = train_data.drop(['馬名','騎手_x', '人気',"調教師","枠番"], axis=1)
    # これはlightGBMによる成約であり、0からクラス数-1の目的変数にラベリングしなければならない

    # 着順はobject型であるため、int型に変換する。"除"、"中"のような文字列だった場合は100に変換する
    train_data['着順'] = train_data['着順'].replace('除', 100).replace('中', 100).replace('取', 100).replace('計不', 100)
    # 着順が計不の場合は100に変換する
    train_data['着順'] = train_data['着順'].replace('計不', 100)
    # 着順列の値を処理して数値部分のみを抽出
    train_data['着順'] = train_data['着順'].apply(lambda x: int(x.split('(')[0]) if isinstance(x, str) else x)
    train_data['着順'] = train_data['着順'].astype(int)
    train_data['goal_number'] = train_data['着順']
    train_data = train_data.rename(columns={'馬 場':'馬場'})
    train_data = train_data.rename(columns={'天 気':'天気'})

    # 予測に使用する特長量を定義する
    # train_data.columns = train_data.columns.str.replace(' ', '')
    # train_data.columns = train_data.columns.str.replace('　', '')

    if not is_ranking:
        # ランキング学習でない場合は通常のグルーピング
        # 目的変数であるgoal_numberをグルーピングする。1であれば0、2と3は1にまとめる、4以上は2にまとめる
        train_data['goal_number'] = train_data['goal_number'].replace(
            {1: 0, 2: 1, 3: 1}
        ).apply(lambda x: 2 if x >= 4 else x)
    else:
        # ランキング学習の場合は1位が30、2位が28、3位が26、残りは0の着順関連度に変換する。
        # goal numberをスコア化
        # ランキング学習の場合は1位が30、2位が28、3位が26、残りは0の着順関連度に変換する。
        # ->評価指標(NDCG)に合わせて指数関数的にスコアをつける
        train_data['goal_number_replace'] = train_data['goal_number'].apply(
            # lambda x: 10 if x == 1 else (5 if x == 2 else (2 if x == 3 else 0)))
            lambda x: 10 if x == 1 else (3 if x == 2 else (1 if x == 3 else 0)))
    
    # inference に合わせて前処理を実施
    # 性齢の1文字から性別を取得しhorse_sexへ、2文字目以降から年齢を取得しhorse_ageへ格納する
    train_data['horse_sex'] = train_data['性齢'].apply(lambda x: x[0])
    train_data['horse_age'] = train_data['性齢'].apply(lambda x: int(x[1:]))
    # 馬体重_xから体重と、()内の増減を取得する
    # 馬体重が計不の場合は500
    train_data['馬体重_x'] = train_data['馬体重_x'].replace('計不', '500(0)')
    train_data['horse_weight'] = train_data['馬体重_x'].apply(lambda x: int(x.split('(')[0]))
    train_data['weight_change'] = train_data['馬体重_x'].apply(lambda x: int(x.split('(')[1].replace(')', '')))
    # 斤量を取得しhandiに格納する
    train_data['handi'] = train_data['斤量'].apply(lambda x: int(x))
    # course_lenを取得しdistanceに格納する
    train_data['distance'] = train_data['course_len'].apply(lambda x: int(x))
    # race_typeを取得し1文字目を取得しconditionに格納する
    train_data['condition'] = train_data['race_type'].apply(lambda x: x[0])
    # 馬番を取得しumabanに格納する
    train_data['umaban'] = train_data['馬番'].apply(lambda x: int(x))
    # 単勝を取得しoddsに格納する
    # 単勝が---の場合は100に変換する
    train_data['単勝'] = train_data['単勝'].replace('---', 100)
    train_data['odds'] = train_data['単勝'].apply(lambda x: float(x))
    # oddsの逆数を取得し、odds_invに格納する
    train_data['odds_inv'] = train_data['odds'].apply(lambda x: 1 / x)

    # タイム_yは1:34.0のような形式なので、秒に変換する
    # nanの場合は100に変換する
    # 'タイム_y'列の値を文字列に変換し、NaN値を無視して処理を行う
    train_data['タイム_y'] = train_data['タイム_y'].astype(str).apply(
        lambda x: int(x.split(':')[0]) * 60 + float(x.split(':')[1]) if ':' in x else np.nan
    )

    # 'ペース'列の値を文字列に変換し、NaN値を無視して処理を行う
    train_data['pace1'] = train_data['ペース'].astype(str).apply(
        lambda x: float(x.split('-')[0]) if '-' in x else np.nan
    )
    train_data['pace2'] = train_data['ペース'].astype(str).apply(
        lambda x: float(x.split('-')[1]) if '-' in x else np.nan
    )

    # 馬体重_yは480(+2)のような形式なので、体重と増減を分ける
    train_data['馬体重_y'] = train_data['馬体重_y'].replace('計不', '500(0)')
    train_data['horse_weight_y'] = train_data['馬体重_y'].apply(lambda x: int(x.split('(')[0]))
    # 'weight_change_y'列を作成し、'馬体重_y'列の値を処理
    train_data['weight_change_y'] = train_data['馬体重_y'].apply(
        lambda x: int(x.split('(')[1].replace(')', '')) if '(' in x else np.nan
    )

    # '連対率'列の値を処理し、全角の'％'を半角の'%'に置き換えてからfloatに変換
    train_data['連対率'] = train_data['連対率'].apply(
        lambda x: float(x.replace('％', '')) if isinstance(x, str) else x
    )

    # '勝率'列の値を処理し、全角の'％'を半角の'%'に置き換えてからfloatに変換
    train_data['勝率'] = train_data['勝率'].apply(
        lambda x: float(x.replace('％', '')) if isinstance(x, str) else x
    )

    # '複勝率'列の値を処理し、全角の'％'を半角の'%'に置き換えてからfloatに変換
    train_data['複勝率'] = train_data['複勝率'].apply(
        lambda x: float(x.replace('％', '')) if isinstance(x, str) else x
    )

    # train_data = train_data.rename(columns={'天 気':'天気'})
    # train_data = train_data.rename(columns={'馬 場':'馬場'})

    # オッズの逆数を取得し、オッズの逆数に格納する
    train_data['1/オ ッ ズ'] = train_data['オ ッ ズ'].apply(lambda x: 1 / x)
    # columnの名前を確認し、:や 、"、'がある場合は_に置き換える
    # train_data.columns = train_data.columns.str.replace(":", "_")
    # train_data.columns = train_data.columns.str.replace(",", "_")
    # train_data.columns = train_data.columns.str.replace("'", "_")
    # train_data.columns = train_data.columns.str.replace('"', "_")
    # train_data.columns = train_data.columns.str.replace(" ", "_")

    # train dataのカラム情報を表示
    # print(train_data.columns)

    # 学習、推論データの特長量を定義する
    target_feature = 'goal_number'
    features = [
        'distance',
        'condition',
        'umaban', # 100%になったし、そもそも不要なのでコメントアウト
        'horse_age',
        'horse_sex',
        # 'horse_weight', # 馬の体重は引っ張ってこれないのでコメントアウト
        # 'weight_change',
        'handi',
        # 'odds',
        "odds_inv",
        # ここまではtrain_resultとinferenceから抽出できる共通データ

        "weather",
        "ground_state", # 分類特長量

        # ここからは馬の過去データから抽出できるので必要な情報を追加する
        '天気',
        '頭 数',
        '枠番',
        '馬番',
        # 'オ ッ ズ',
        '1/オ ッ ズ',
        '人気',
        # '着順', # 目的変数なので削除する
        '斤量',
        '距離',
        '馬場',
        'タイム_y',
        'pace1',
        'pace2',
        '上り',
        'horse_weight_y',
        'weight_change_y',
        '賞金',
        # # ここからはジョッキーの過去データから抽出できるので必要な情報を追加する
        '1着',
        '2着',
        '3着',
        '4着〜',
        '騎乗 回数',
        '重賞 出走',
        '重賞 勝利',
        '勝率',
        '連対率',
        '複勝率',
        'peds_0',   # 血統情報を学習データに入れると結果が悪くなったのでコメントアウト
        'peds_1',
        'peds_2',
        'peds_3',
        'peds_4',
        'peds_5',
    ]
    if is_mlp:
        # race idを追加する
        features += ["race_id"]
    # 特長量を抽出する
    if is_ranking:
        additional_features = ['log_odds', 'normalized_odds', 'zscore_odds', 'odds_rank', 'odds_std','odds_diff-1-2',"odds_diff-1-3"]
        # additional_features = ['odds_std', "odds_diff-1-2","odds_diff-1-3"]
        # additinal_features = []
        train_data = train_data[features + [target_feature] + ['goal_number_replace'] + additional_features]
        # train_data = train_data[features + [target_feature] + ['goal_number_replace'] ]
    else:
        train_data = train_data[features + [target_feature]]
    # inference_dataの特長量のobject型は、LabelEncoderで数値に変換する
    # object型の特長量を確認する
    object_columns = train_data.select_dtypes(include='object').columns
    object_columns
    # ラベルエンコーダーを保存する辞書
    label_encoders = {}
    for column in object_columns:
        # print(column)
        le = LabelEncoder()
        # object型は別のラベル名にてラベルエンコーディングする
        train_data[column] = le.fit_transform(train_data[column])
        label_encoders[column] = le
    # ラベルエンコーダーを保存
    with open('pkl_registory/label_encoders.pkl', 'wb') as f:
        pickle.dump(label_encoders, f)
        print(le.classes_)
    # 学習データが大きすぎるので、train_dataの上から1000行を取得して学習データとする
    # if not is_ranking:
    #     train_data = train_data[:50000]
    print(train_data.info())

    return train_data

# 特長量の前処理①対数変換
def log_transform(train_data):
    # 対数変換を行う特長量を定義する。対象はスケールの大きいもの、右に裾が長いもの、指数的に増加するものがある。
    log_features = [
        # 'distance',
        'odds',
        'オ ッ ズ',
        # 'タイム_y',
        # '4着〜',
        # '騎乗 回数'
    ]
    # 対数変換を行う
    for feature in log_features:
        train_data[feature] = np.log1p(train_data[feature])
    return train_data

def standard_scaler(train_data):
    # 標準化を行う特長量を定義する。標準化は特長量のスケールを揃えるために行う。ラベルエンコーディングされた特長量以外は基本実施
    standard_features = [
        'distance',
        # 'condition',
        # 'umaban', # 100%になったし、そもそも不要なのでコメントアウト
        # 'horse_age',
        # 'horse_sex',
        # 'horse_weight',
        # 'weight_change',
        'handi',
        # 'odds',
        # ここまではtrain_resultとinferenceから抽出できる共通データ

        # ここからは馬の過去データから抽出できるので必要な情報を追加する
        # '天 気',
        '頭 数',
        # '枠番',
        # '馬番',
        # 'オ ッ ズ',
        '人気',
        # '着順', # 目的変数なので削除する
        '斤量',
        # '距離',  # ラベルなので削除
        # '馬 場',
        'タイム_y',
        'pace1',
        'pace2',
        '上り',
        'horse_weight_y',
        'weight_change_y',
        '賞金',
        # # ここからはジョッキーの過去データから抽出できるので必要な情報を追加する
        '1着',
        '2着',
        '3着',
        '4着〜',
        '騎乗 回数',
        '重賞 出走',
        '重賞 勝利',
        '勝率',
        '連対率',
        '複勝率',
    ]
    # 標準化実施
    scaler = StandardScaler()
    train_data[standard_features] = scaler.fit_transform(train_data[standard_features])
    return train_data

# ================================
# for lanking learning
# ================================

def odds_feature_engineering(train_data_for_ranking):
    # クエリを使用してオッズの特長量をエンジニアリング
    # 1 オッズを対数変換
    train_data_for_ranking["log_odds"] = np.log1p(train_data_for_ranking["odds"])

    # 2 同一レースidにおけるオッズのmin-max正規化
    train_data_for_ranking["normalized_odds"] = (train_data_for_ranking["odds"] - train_data_for_ranking["odds"].min()) / (train_data_for_ranking["odds"].max() - train_data_for_ranking["odds"].min())
    # 3 zスコア標準化
    train_data_for_ranking["zscore_odds"] = (train_data_for_ranking["odds"] - train_data_for_ranking["odds"].mean()) / train_data_for_ranking["odds"].std()

    # 4オッズの順位
    train_data_for_ranking["odds_rank"] = train_data_for_ranking.groupby('race_id')['odds'].rank(ascending=True, method='min')

    # 5 レースごとのオッズのばらつき
    train_data_for_ranking["odds_std"] = train_data_for_ranking.groupby("race_id")["odds"].transform("std")
    return train_data_for_ranking

# 各レースごとにオッズをソートして1位、2位、3位のオッズを取得
def get_odds_differences(df):
    odds_diff_1_2 = []
    odds_diff_1_3 = []
    for race_id, group in df.groupby('race_id'):
        sorted_group = group.sort_values('odds')
        if len(sorted_group) >= 3:
            odds_1 = sorted_group.iloc[0]['odds']
            odds_2 = sorted_group.iloc[1]['odds']
            odds_3 = sorted_group.iloc[2]['odds']
            odds_diff_1_2.extend([odds_1 - odds_2] * len(group))
            odds_diff_1_3.extend([odds_1 - odds_3] * len(group))
        else:
            odds_diff_1_2.extend([None] * len(group))
            odds_diff_1_3.extend([None] * len(group))
    return odds_diff_1_2, odds_diff_1_3


def create_query(df, name='train'):
    """
    Create a query for the given DataFrame.
    Returns the query and the number of unique
    """

    # groupbyを使用してdate, race_name, place, number_of_horses, distanceごとにカウント
    race_place_counts = df.groupby(['race_id']).size().reset_index(name='horse_count')

    # date列を昇順にソート
    # race_place_counts = race_place_counts.sort_values(by='date', ascending=False)

    # 各レースの馬の数をリストに保存
    horse_counts_list = race_place_counts['horse_count'].tolist()

    # 結果の表示
    print("\nResulting list of horse counts per race (sorted by date):")
    print(horse_counts_list)

    # 特徴量データを日付の古い順にソート
    # sorted_df = df.sort_values(by='date', ascending=True)

    # ソートデータの保存
    # df.to_csv("sorted_{}_data.csv".format(name), index=False)
    # date, race_name, place, number_of_horses, distanceのユニークな組み合わせを表示して確認
    print("\nUnique combinations of date, race_name, place, number_of_horses, distance:")
    # 上から100データを表示
    # print(df[['course_len', 'weather', 'race_type', 'ground_state', 'date']].head(100))
    return horse_counts_list, df

# 予測結果の評価
def rank_evaluation(df_prediction_test_ranking, modelname='予測順位(lambdarank)'):
    # 1位予想で1位だった数
    true_positive = df_prediction_test_ranking[
        (df_prediction_test_ranking[modelname] == 1) & 
        (df_prediction_test_ranking['着順'] == 1)
    ].shape[0]

    # 1位予想で1位じゃなかった数
    false_positive = df_prediction_test_ranking[
        (df_prediction_test_ranking[modelname] == 1) & 
        (df_prediction_test_ranking['着順'] != 1)
    ].shape[0]

    # 1位じゃない予想で1位だった数
    false_negative = df_prediction_test_ranking[
        (df_prediction_test_ranking[modelname] != 1) & 
        (df_prediction_test_ranking['着順'] == 1)
    ].shape[0]

    # 1位じゃない予想で1位じゃなかった数
    true_negative = df_prediction_test_ranking[
        (df_prediction_test_ranking[modelname] != 1) & 
        (df_prediction_test_ranking['着順'] != 1)
    ].shape[0]

    print(f'True Positive: {true_positive}')
    print(f'False Positive: {false_positive}')
    print(f'False Negative: {false_negative}')
    print(f'True Negative: {true_negative}')
    # presicion, recall, f1 scoreの計算
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    f1 = 2 * precision * recall / (precision + recall)
    print(f'Precision: {precision:.4f}')
    print(f'Recall: {recall:.4f}')
    print(f'F1 Score: {f1:.4f}')

    # Confusion Matrixの作成
    confusion_matrix = np.array([[true_positive, false_negative],
                                [false_positive, true_negative]])

    # Confusion Matrixの可視化
    plt.figure(figsize=(8, 6))
    sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Predicted 1', 'Predicted Not 1'], yticklabels=['Actual 1', 'Actual Not 1'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()


# ================================
# 1位と2位のスコアの差からロバスト性を向上させる
# ================================

# 1位と2位のスコアの差を算出
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

# 1位が正解した時、2位だった時、それ以外だった時のスコアの差を可視化
def plot_score_diff(df, modelname, N=1):
    correct_1st = df[(df[f'予測順位({modelname})'] == N) & (df['着順'] == N)]
    second_place = df[(df[f'予測順位({modelname})'] == N) & (df['着順'] == N+1)]
    other_places = df[(df[f'予測順位({modelname})'] == N) & (df['着順'] > N+1)]

    plt.figure(figsize=(10, 6))
    sns.histplot(correct_1st[f'score_diff_{modelname}'], kde=True, color='green', label='Correct 1st', bins=50)
    sns.histplot(second_place[f'score_diff_{modelname}'], kde=True, color='blue', label='2nd Place', bins=50)
    sns.histplot(other_places[f'score_diff_{modelname}'], kde=True, color='red', label='Other Places', bins=50)
    plt.xlabel('Score Difference')
    plt.ylabel('Frequency')
    plt.title(f'Score Difference for {modelname}')
    plt.legend()
    plt.show()

from sklearn.metrics import roc_curve, precision_recall_curve

# 最適な閾値を見つける
def find_optimal_threshold(df, modelname, N):
    y_true = (df['着順'] == N).astype(int)
    y_scores = df[f'score_diff_{modelname}']

    # ROC曲線を使用して最適な閾値を見つける
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    optimal_idx = np.argmax(tpr - fpr)
    optimal_threshold = thresholds[optimal_idx]

    # Precision-Recall曲線を使用して最適な閾値を見つける
    precision, recall, thresholds_pr = precision_recall_curve(y_true, y_scores)
    f1_scores = 2 * precision * recall / (precision + recall)
    optimal_idx_pr = np.argmax(f1_scores)
    optimal_threshold_pr = thresholds_pr[optimal_idx_pr]

    return optimal_threshold, optimal_threshold_pr

def apply_threshold(df, modelname, threshold, N):
    # 予測結果を閾値で分類
    # 予測スコアが閾値以上の場合かつ予測順位が1の時は1、それ以外は0
    df[f'予測結果({modelname})'] = ((df[f'score_diff_{modelname}'] >= threshold) & (df[f'予測順位({modelname})'] == N)).astype(int)
    # 予測順位が的中している場合は2を返す
    df.loc[df[f'予測順位({modelname})'] == N, f'予測結果({modelname})'] = 2
    return df



# 予測精度を評価し、Confusion Matrixを出力
def evaluate_predictions(df, modelname):
    true_positive = df[
        (df[f'予測結果({modelname})'] == 1) & 
        (df['着順'] == 1)
    ].shape[0]

    false_positive = df[
        (df[f'予測結果({modelname})'] == 1) & 
        (df['着順'] != 1)
    ].shape[0]

    false_negative = df[
        (df[f'予測結果({modelname})'] != 1) & 
        (df['着順'] == 1)
    ].shape[0]

    true_negative = df[
        (df[f'予測結果({modelname})'] != 1) & 
        (df['着順'] != 1)
    ].shape[0]

    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    print(f'Precision for {modelname}: {precision:.4f}')
    print(f'Recall for {modelname}: {recall:.4f}')
    print(f'F1 Score for {modelname}: {f1_score:.4f}')

    # Confusion Matrixの作成
    # Confusion Matrixの作成
    confusion_matrix = np.array([[true_positive, false_negative],
                                [false_positive, true_negative]])

    # Confusion Matrixの可視化
    plt.figure(figsize=(8, 6))
    sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Predicted 1', 'Predicted Not 1'], yticklabels=['Actual 1', 'Actual Not 1'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title(f'Confusion Matrix for {modelname}')
    plt.show()

# 予測結果の評価を行う関数
def evaluate_predictions_without_cm(df, modelname):
    # TP, FP, FN, TNを計算
    true_positive = df[
        (df[f'予測結果({modelname})'] == 1) & 
        (df['着順'] == 1)
    ].shape[0]

    false_positive = df[
        (df[f'予測結果({modelname})'] == 1) & 
        (df['着順'] != 1)
    ].shape[0]

    false_negative = df[
        (df[f'予測結果({modelname})'] != 1) & 
        (df['着順'] == 1)
    ].shape[0]

    true_negative = df[
        (df[f'予測結果({modelname})'] != 1) & 
        (df['着順'] != 1)
    ].shape[0]

    # Precision, Recallを計算
    precision = true_positive / (true_positive + false_positive) if (true_positive + false_positive) > 0 else 0
    recall = true_positive / (true_positive + false_negative) if (true_positive + false_negative) > 0 else 0
    # print(f'True Positive: {true_positive}')
    # print(f'False Positive: {false_positive}')
    # print(f'False Negative: {false_negative}')
    # print(f'True Negative: {true_negative}')
    # print(f'Precision for {modelname}: {precision:.4f}')
    # print(f'Recall for {modelname}: {recall:.4f}')

    return   round(precision, 2), round(recall, 2)


# ================================
# 各特長量ごとにデータを分類して評価
# ================================
def evaluate_by_feature(df, feature, modelname):
    unique_values = df[feature].unique()
    results = []
    for value in unique_values:
        
        # print(f'feature {feature}:value : {value}')
        subset = df[df[feature] == value]
        precision, recall = evaluate_predictions_without_cm(subset, modelname)
        results.append((value, precision, recall))
    return results

# 評価結果をデータフレームにまとめる
def results_to_dataframe(results, feature_name):
    df = pd.DataFrame(results, columns=[feature_name, 'Precision', 'Recall'])
    return df

# 棒グラフで可視化
def plot_results(df, feature_name, modelname):
    df_melted = df.melt(id_vars=[feature_name], value_vars=['Recall', 'Precision'], var_name='Metric', value_name='Score')
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(x=feature_name, y='Score', hue='Metric', data=df_melted)
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.2f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points')
    plt.title(f'Recall and Precision by {feature_name}: {modelname}')
    plt.xticks(rotation=45)
    plt.show()

def model_evaluation_by_feature(df_prediction_test_ranking, modelname):
    # 各特長量ごとに評価
    distance_results = evaluate_by_feature(df_prediction_test_ranking, 'distance', modelname)
    condition_results = evaluate_by_feature(df_prediction_test_ranking, 'condition', modelname)
    weather_results = evaluate_by_feature(df_prediction_test_ranking, 'weather', modelname)
    ground_state_results = evaluate_by_feature(df_prediction_test_ranking, 'ground_state', modelname)

    distance_df = results_to_dataframe(distance_results, 'Distance')
    condition_df = results_to_dataframe(condition_results, 'Condition')
    weather_df = results_to_dataframe(weather_results, 'Weather')
    ground_state_df = results_to_dataframe(ground_state_results, 'Ground State')
            

    plot_results(distance_df, 'Distance',modelname)
    plot_results(condition_df, 'Condition',modelname)
    plot_results(weather_df, 'Weather',modelname)
    plot_results(ground_state_df, 'Ground State',modelname)

# 馬連の予測確率を計算
def umaren_precision(df, modelname):
    y_true = []
    y_pred = []
    
    for race_id, group in df.groupby('race_id'):
        # print(race_id)
        # 予測結果の1位と2位の馬を抽出
        predicted_top2 = set(group.nsmallest(2, modelname)['馬番号'].values)
        # print("predicted_top2",predicted_top2)
        # 実際のレース結果の1位と2位の馬を抽出
        actual_top2 = set(group.nsmallest(2, '着順')['馬番号'].values)
        # print("actual_top2",actual_top2)
        # 予測結果と実際のレース結果を比較して一致しているかを判断しているのがここ。
        y_true.append(1 if actual_top2 == predicted_top2 else 0)
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    # print(y_true)
    
    # すべてのレースのうちの予測的中率
    sum_ = len(y_true)
    print(sum_)
    y_true_total = np.sum(y_true == 1)
    print(y_true_total)
    print("precision rate {}".format(y_true_total / sum_))
    
# for secandary prediction evaluate
# 予測結果の評価
def rank_evaluation_N(df_prediction_test_ranking, modelname='予測順位(lambdarank)', N=2):
    true_positive = df_prediction_test_ranking[
        (df_prediction_test_ranking[modelname] == N) & 
        (df_prediction_test_ranking['着順'] == N)
    ].shape[0]

    false_positive = df_prediction_test_ranking[
        (df_prediction_test_ranking[modelname] == N) & 
        (df_prediction_test_ranking['着順'] != N)
    ].shape[0]

    false_negative = df_prediction_test_ranking[
        (df_prediction_test_ranking[modelname] != N) & 
        (df_prediction_test_ranking['着順'] == N)
    ].shape[0]

    true_negative = df_prediction_test_ranking[
        (df_prediction_test_ranking[modelname] != N) & 
        (df_prediction_test_ranking['着順'] != N)
    ].shape[0]

    print(f'True Positive: {true_positive}')
    print(f'False Positive: {false_positive}')
    print(f'False Negative: {false_negative}')
    print(f'True Negative: {true_negative}')
    # presicion, recall, f1 scoreの計算
    precision = true_positive / (true_positive + false_positive)
    recall = true_positive / (true_positive + false_negative)
    f1 = 2 * precision * recall / (precision + recall)
    print(f'Precision: {precision:.4f}')
    print(f'Recall: {recall:.4f}')
    print(f'F1 Score: {f1:.4f}')

    # Confusion Matrixの作成
    confusion_matrix = np.array([[true_positive, false_negative],
                                [false_positive, true_negative]])

    # Confusion Matrixの可視化
    plt.figure(figsize=(8, 6))
    sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=['Predicted 1', 'Predicted Not 1'], yticklabels=['Actual 1', 'Actual Not 1'])
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.show()