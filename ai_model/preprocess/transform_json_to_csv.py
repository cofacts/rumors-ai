# coding=utf-8

# import packages
import os
import json
import argparse

import pandas as pd
import numpy as np




def main():

    parser = argparse.ArgumentParser()

    # Required parameters
    parser.add_argument(
        "--data_dir",
        default=None,
        type=str,
        required=True,
        help="input JSON files directory",
    )
    parser.add_argument(
        "--output_dir",
        default=None,
        type=str,
        required=True,
        help="output CSV files directory",
    )


    args = parser.parse_args()

    data_dir = args.data_dir
    output_dir = args.output_dir


    files = os.listdir(data_dir)
    files = [file for file in files if 'json' in file]


    # load tags and text information of the json files
    define_columns = ['id', 'text', 'label']

    data_list = []
    for file in files:

        with open(os.path.join(data_dir, file), 'r') as f:
            data = json.load(f)

        label = [data['tags'][0]]

        data_list.append([file, data['text']] + label)

    df_data = pd.DataFrame(data_list, columns=define_columns)


    # create train/dev/test csv files for modulized BERT
    num_files = df_data.shape[0]
    train_ratio = 0.7
    dev_ratio = 0.1
    test_ratio = 0.2

    if os.path.exists(output_dir) == False:
        os.mkdir(output_dir)

    df_data[:int(train_ratio*num_files)].to_csv(os.path.join(output_dir, 'train.csv'))
    df_data[int(train_ratio*num_files):int((train_ratio+dev_ratio)*num_files)].to_csv(os.path.join(output_dir, 'dev.csv'))
    df_data[int((train_ratio+dev_ratio)*num_files):].to_csv(os.path.join(output_dir, 'test.csv'))


if __name__ == "__main__":
    main()
