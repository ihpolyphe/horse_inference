# 競馬予想

LightGBM を使用して馬のタイムを予想する。

## Usage

1. 過去情報をスクレイピングする。
   結果は`keiba_analysis/scrayping/`に保存される。

```
cd scripts/scrayping
python3 horse_scrayping_update.py
```

2. 予想したいレースの馬情報を取得する。
   結果は`keiba_analysis/<assume_id>/scrayping_<assume_id>`に馬情報、
   `keiba_analysis/<assume_id>/horse_name_<assume_id>`に馬名が保存される。

```
cd scripts/scrayping
python3 scrayping_horse_info.py
```

3. 学習&推論を行う。
   結果は`keiba_analysis/<assume_id>/inference_horse_time_<assume_id>`にレースごとの馬のタイム推論結果が保存される。

```
cd scripts/
python3 inference_as_a_horse.py
```

## ToDo

- 推論単位の変更

  今は馬ごとのレースを推論しているだけで、一位になるかどうかを推論していない。レースの中で１位を特徴量として学習させ、単勝の精度向上を図る。

- 動的スクレイピングを用いたオッズ情報、馬体重情報の取得。

  今は、馬体重や、オッズが動的スクレイピングできていない関係で、推論時に使用できておらず、推論制度が低いことが想定できる。動的スクレイピングによって情報量を増やすことで精度向上を図る。
