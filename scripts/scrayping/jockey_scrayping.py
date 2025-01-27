import os
import requests
import re
import tqdm
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
    
class jockeyResults:
    @staticmethod
    def scrape(jockey_id_list):
        """
        騎手の過去成績データをスクレイピングする関数

        Parameters:
        ----------
        jockey_id_list : list
            騎手IDのリスト

        Returns:
        ----------
        jockey_results_df : pandas.DataFrame
            全騎手の過去成績データをまとめてDataFrame型にしたもの
        """
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/85.0.4341.72",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 OPR/85.0.4341.72",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Vivaldi/5.3.2679.55",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Vivaldi/5.3.2679.55",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Brave/1.40.107",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Brave/1.40.107",
        ]
        jockey_results_df = []
        jockey_results = {}
        for jockey_id in tqdm(jockey_id_list):
            try:
                time.sleep(1)
                url = 'https://db.netkeiba.com/jockey/' + str(jockey_id)
                headers = {'User-Agent': random.choice(USER_AGENTS),
                            'Referer': "https://db.netkeiba.com/",
                            'Accept-Language': 'ja-jp,ja;q=0.9,en-US;q=0.8,en;q=0.7'
                            }
                html = requests.get(url, headers=headers)
                html.encoding = "EUC-JP"
                # HTMLからデータフレームを取得
                df = pd.read_html(html.text)[2]
                df.index = [jockey_id] * len(df)
                # 3行目を削除
                # df = df.drop(df.index[1])
                # インデックスをリセット
                jockey_results = df.reset_index(drop=True)
                # 代表馬、順位列を削除
                jockey_results = jockey_results.drop(["代表馬", "順位"], axis=1)

                # jockey_idを追加
                jockey_results["jockey_id"] = jockey_id
                # print(jockey_results)
                jockey_results_df.append(jockey_results)
            except IndexError:
                continue
            except Exception as e:
                print(e)
                break
            except:
                break
        # pd.DataFrame型にして一つのデータにまとめる    
        jockey_results_df = pd.concat(jockey_results_df, ignore_index=True)
        # print(jockey_results_df)
        return jockey_results_df



#============スクレイピング実行============
race_id_list = []
scrayping_year = "2024"


# 取得したrace resultsをcsvに保存
is_denso = False
is_windows = False
if is_denso:
    if is_windows:
        sys.exit()
    save_path = "/home/denso/horse_inference/data_for_train/train_data/" + str(scrayping_year) + "/"
else:
    if not is_windows:
        save_path = "/home/hayato/horse_inference/data_for_train/train_data/" + str(scrayping_year) + "/"
    else:
        save_path = r"C:\Users\hayat\Desktop\horse_inference\data_for_train\train_data\train_data" + str(scrayping_year) + "\\"

print(save_path)
# 保存先のディレクトリが存在しない場合は作成
if not os.path.exists(save_path):
    os.makedirs(save_path)

# is_saveがTrueだった場合、csvのデータからhorse_id_listを取得
results = pd.read_csv(save_path+"train_data_results_" + str(scrayping_year) + ".csv",dtype={'jockey_id': str})

# テストなので10レース分だけ取得
# results = results.iloc[:3]

# jockey_id_listをstr型で取得
jockey_id_list = results["jockey_id"].astype(str).unique()
print(jockey_id_list)
# jokeyの過去成績のスクレイピング
print("start jokey scrayping")
jockey_results = jockeyResults.scrape(jockey_id_list)
jockey_results.to_csv("jockey_results_test.csv", index=False)
jockey_results.to_csv(save_path+"jockey_results_" + str(scrayping_year) + ".csv", index=False)
