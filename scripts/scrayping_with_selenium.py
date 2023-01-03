from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import lxml.html
import pandas as pd

import re
import datetime
from time import sleep
from argparse import ArgumentParser

# クローリング・スクレイピングのメイン関数
def get_win_odds_list(open_date,output_mode,target_race_course,target_race_no):
    # pandasの標準出力の桁揃えオプション
    pd.set_option('display.unicode.east_asian_width', True)

    # 引数事前処理
    open_info               = get_open_info(open_date)                  # 対象日付より開催情報を取得
    target_race_course_code = conversion_racecourse(target_race_course) # 競馬場名をコードに変換
    target_race_no_fill     = str(target_race_no).zfill(2)              # レースNoを2桁に変換

    # メイン処理
    for race_place in open_info:
        if race_place["race_course"] == target_race_course_code:
            win_odds_url = format_win_odds_url(race_place["race_course"],race_place["race_times"],race_place["race_day"],target_race_no_fill)
            sleep(1)
            # 出力モードSの場合は標準出力にprint、出力モードDの場合はDataFrame形式でreturn
            if output_mode == 'S':

                print(get_win_odds_df(win_odds_url))
            elif output_mode == 'D':
                return get_win_odds_df(win_odds_url)


# 単勝オッズページを引数に指定して、そのページから馬番・馬名・単勝オッズを取得し、DataFrame形式で返す
def get_win_odds_df(url):
    # Seleniumを用いてクローリング
    driver = webdriver.PhantomJS()                  # PhamtomJSのWebDriverオブジェクトを作成する。
    driver.get(url)                                 # オッズ表示画面を開く
    sleep(1)                                        # 負荷分散の為のsleep
    root = lxml.html.fromstring(driver.page_source) # 検索結果を表示し、lxmlで解析準備

    # 辞書・リストの初期化
    win_odds_dict       = {}
    horse_number_list   = []
    horse_name_list     = []
    tan_odds_list       = []

    # 馬番・馬名・単勝オッズをスクレイピング
    for horse_number,horse_name,tan_odds in zip(root.cssselect('.umaban'),root.cssselect('.h_name'),root.cssselect('[axis^=oddsDataTan]')):
        horse_number_list.append(horse_number.text)
        horse_name_list.append(horse_name.text)
        tan_odds_list.append(tan_odds.text)

    # スクレイピング結果を辞書からDataFrame形式に変換
    win_odds_dict["horse_number"]   =   horse_number_list
    win_odds_dict["horse_name"]     =   horse_name_list
    win_odds_dict["tan_odds"]       =   tan_odds_list
    win_odds_df                     =   pd.DataFrame(win_odds_dict,columns=['horse_number', 'horse_name', 'tan_odds'])

    return win_odds_df


# 単勝オッズ取得対象ページのURLを整形する
def format_win_odds_url(race_course,race_times,race_day,race_no):
    win_odds_url_template = "http://race.netkeiba.com/?pid=odds&id=p"
    year = datetime.date.today().year

    win_odds_url = win_odds_url_template + str(year) + str(race_course) + str(race_times) + str(race_day) + str(race_no)

    return "https://race.netkeiba.com/odds/index.html?race_id=202203030212"

# 引数に指定したmmdd形式の日付で開催されるレースの開催情報を取得しリストで返す
def get_open_info(mmdd):
    race_list_url_template = "http://race.netkeiba.com/?pid=race_list&id=p"
    race_list_url = race_list_url_template + mmdd

    open_info_list = []

    # スクレイピング処理
    driver = webdriver.PhantomJS()
    driver.get(race_list_url)
    root = lxml.html.fromstring(driver.page_source)
    for open_info in root.cssselect('.kaisaidata'):
        open_info_dict = {}
        m = re.match(r"(\d+)回(..)(\d+)日目", open_info.text)
        open_info_dict["race_times"]     = m.group(1).zfill(2)                  # 開催回を2桁に整形
        open_info_dict["race_course"]    = conversion_racecourse(m.group(2))    # 開催競馬場をコード変換
        open_info_dict["race_day"]       = m.group(3).zfill(2)                  # 開催日を2桁に整形
        open_info_list.append(open_info_dict)

    '''
    スクレイピング結果
    [
      {'race_course': '04', 'race_day': '10', 'race_times': '02'},
      {'race_course': '10', 'race_day': '10', 'race_times': '02'},
      {'race_course': '01', 'race_day': '04', 'race_times': '02'}
    ]
    '''

    return open_info_list

# 競馬場から2桁の競馬場コードへの変換関数
def conversion_racecourse(rc_name):
    rc_code = ""

    if rc_name == "札幌":
        rc_code = "01"
    elif rc_name == "函館":
        rc_code = "02"
    elif rc_name == "福島":
        rc_code = "03"
    elif rc_name == "新潟":
        rc_code = "04"
    elif rc_name == "東京":
        rc_code = "05"
    elif rc_name == "中山":
        rc_code = "06"
    elif rc_name == "中京":
        rc_code = "07"
    elif rc_name == "京都":
        rc_code = "08"
    elif rc_name == "阪神":
        rc_code = "09"
    elif rc_name == "小倉":
        rc_code = "10"

    return rc_code


if __name__ == '__main__':
    # 引数処理
    parser = ArgumentParser(description='Process some integers.')
    ## 日付（必須）
    parser.add_argument('-d','--date', help='date(mmdd)', required=True)
    ## 競馬場名（必須・入力値制限）
    parser.add_argument('-c','--race_course', help='Race Course',choices=['札幌','函館','福島','新潟','東京','中山','中京','京都','阪神','小倉'],required=True)
    ## レース番号（任意・デフォルト11・入力値制限）
    parser.add_argument('-n','--race_no', help='Race No',default=11, type=int, choices=range(1, 13))
    ## 出力モード（任意・デフォルト値S・入力値制限）
    parser.add_argument('-m','--output_mode', help='OutputMode S:stdout D:dataframe',default='S',choices=['S','D'])

    args            =   parser.parse_args()

    # 引数で指定された情報を変数に格納
    open_date                   =   args.date            # 開催情報をクローリングしたい日付を格納
    output_mode                 =   args.output_mode     # アウトプットモードを格納
    target_race_course          =   args.race_course     # 指定した競馬場名を格納
    target_race_no              =   args.race_no         # 指定したレース番号を格納

    # クローリング・スクレイピング実行
    get_win_odds_list(open_date,output_mode,target_race_course,target_race_no)