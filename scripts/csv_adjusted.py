

# csvを読み込み、指定行分だけの情報を新しいcsvに出力する
import csv

def csv_adjusted(input_file, output_file, row_num):
    with open(input_file, 'r') as f:
        reader = csv.reader(f)
        # トータル行を出力
        print(len([row for row in reader]))
        # 

        rows = [row for row in reader]
        print(reader)
    
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(rows[:row_num])

path = '/mnt/c/Users/hayat/Desktop/keiba_analysis/data_for_train/train/2005_2022/train_data__sorted2005_2022.csv'
csv_adjusted(path, 'train_data_sorted2005_2022_extract_30000.csv', 30000)
