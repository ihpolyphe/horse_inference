# 競馬予想

LightGBM を使用して馬のタイムを予想する。

## Usage
### 学習
1. 過去情報をスクレイピングする。
   結果は`keiba_analysis/data_for_train/scrayping_past_info/`に保存される。

```
cd scripts/scrayping
python3 horse_scrayping_update.py
```

2. 上の情報から、馬の過去レース情報と、学習データを生成する。
   結果は`keiba_analysis/data_for_train/horse_index/`に保存される。

```
cd scripts/scrayping
python3 adjust_for_learning.py
```

3. 以下のスクリプトで学習させる。


### 推論
3. 予想したいレースの馬情報を取得する。
   結果は`keiba_analysis/inference/<assume_id>/scrayping_<assume_id>`に馬情報、
   `keiba_analysis/inference/assume_id>/horse_name_<assume_id>`に馬名が保存される。

```
cd scripts/scrayping
python3 scrayping_horse_info.py
```

4. 推論を行う。
   結果は`keiba_analysis/inference/<assume_id>/inference_horse_time_<assume_id>`にレースごとの馬のタイム推論結果が保存される。

```
cd scripts/
python3 inference_as_a_horse.py
```

## ToDo

- 推論単位の変更

  今は馬ごとのレースを推論しているだけで、一位になるかどうかを推論していない。レースの中で１位を特徴量として学習させ、単勝の精度向上を図る。

- 動的スクレイピングを用いたオッズ情報、馬体重情報の取得。

  今は、馬体重や、オッズが動的スクレイピングできていない関係で、推論時に使用できておらず、推論制度が低いことが想定できる。動的スクレイピングによって情報量を増やすことで精度向上を図る。

- デバッグ(vscode) or ターミナル実行の変更をオーギュメンテーションから設定できるようにする。


### bs4 install
In WSL, you can install `bs4` with bellow command.
```bash
 python3 -m pip install bs4
```

# additional
推論データにオッズを追加

一位になる馬番を予測する。一位だけしか予測できないように見えて、１位になる馬番の確率値が算出できるので、上位３つで３連単なども予測できるようになるはず。

## 動的スクレイピングセットアップ
`scrayping_inference_data.py`を実行する場合はいかで動的スクレイピングできる準備を行う.

セットアップ方法は以下に記載の通り。
https://qiita.com/query1000/items/747b1b34a197a55e7fec

### 実行方法
`WSL2`側でchromeを起動してあげないとスクレイピングできないので、以下のコマンドでブラウザを起動する。
```bash
google-chrome&
```

その後スクレイピングスクリプトを実行する。不要なブラウザやvscodeなどを起動しているとGPU不足により失敗する可能性あるので、不要なものは閉じた状態で実行すること。


```python
hayato@ihpolyphe:/mnt/c/Users/hayat/Desktop/keiba_analysis/scripts/scrayping$ python3 scrayping_inference_data.py
オッズ 1: 11.8
オッズ 2: 26.5
オッズ 3: 17.4
オッズ 4: 22.8
オッズ 5: 25.9
オッズ 6: 80.2
オッズ 7: 4.6
オッズ 8: 27.6
オッズ 9: 6.5
オッズ 10: 13.4
オッズ 11: 73.3
オッズ 12: 52.3
オッズ 13: 77.6
オッズ 14: 203.4
オッズ 15: 2.3
```


VScode固まった時
https://stackoverflow.com/questions/43556933/extension-host-terminated-unexpectedly