# 競馬予想

LightGBM を使用して馬のタイムを予想する。

## Usage

1. 過去情報をスクレイピングする。
   結果は`keiba_analysis/data_for_train/scrayping_past_info/`に保存される。

```
cd scripts/scrayping
python3 horse_scrayping_update.py
```

2. 上の情報から、過去情報のインデックスリストを作成する
   結果は`keiba_analysis/data_for_train/horse_index/`に保存される。

```
cd scripts/scrayping
python3 adjust_for_learning.py
```

3. 予想したいレースの馬情報を取得する。
   結果は`keiba_analysis/inference/<assume_id>/scrayping_<assume_id>`に馬情報、
   `keiba_analysis/inference/assume_id>/horse_name_<assume_id>`に馬名が保存される。

```
cd scripts/scrayping
python3 scrayping_horse_info.py
```

4. 学習&推論を行う。
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