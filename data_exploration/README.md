# Flow labeled dataset exploration

There are 3 time-consecutive labeled data provided by Flow:
1. 2020.03.13
2. 2020.03.20
3. 2020.03.24

Total labeled articles are 14,908.

This [notebook](https://github.com/cofacts/rumors-ai/blob/master/data_exploration/EDA.ipynb) is for data exploration and provided some insights of these labeled data.

## Cofacts pre-defined article classes

There are 17 classes listed below:

![pre-defined article classes](./img/Tags_definition.png)


## Tag numbers distribution comparison

It should be noted that for each article may contain **more than 1 tag!**

![Tags distribution](./img/Tags_distribution.png)

![Tags table](./img/Tags_comparison_table.png)

From above figure and table, we can know that:
* There are at most 3 tags in one article
* Most articles are labeled with 1 tag (~92%)
* Tag numbers distributions are similar among all datasets


## Class number distribution comparison

![Class distribution](./img/Class_distribution.png)

From above figure, we can know that:
* Class 11, 13, 15, and 16 change dramatically between 0313 → 0320

To analyze in more detail, we plot the comparison table:

 ![Class table](./img/Class_comparison_table.png)

From above table, we can know that:
* [11 有意義但不包含在以上標籤]: 7.37% → 5.43%
* [13 廣告]: 9.57% → 5.11%
* [15 政治、政黨]: 20.45% → 24.85%
* [16 轉發協尋、捐款捐贈]: 7.81% → 11.32%
* Pretty unbalanced labels
* Dominating Classes: [4] + [12] + [15] + [16]
  * 62.02% → 69.18% → 68.23% (from 0313 to 0324)

## Labeled data quality check and verification

In order to verify Flow labels quality, we are doing eyeball check on 3,000 randomly selected articles.

For the verification report, you can check it out at: **TBC**


# Cofacts articles trending keywords extraction

This [notebook](https://github.com/cofacts/rumors-ai/blob/master/data_exploration/Keywords.ipynb) is for articles trending keywords extraction.

To inspect what topics are hot in a given period of time, the first step is to extract the keywords within that time period.

Here, we demonstrate trending keywords extraction using [jieba](https://github.com/fxsjy/jieba).

We set the interested date = **2017-01-01**, and extract keywords from 1, 3, 7, and 30 days ago.

## Keywords (2017-01-01)

### 1 day & 3 days
![2017-01-01-1d](./img/2017-01-01-1d.png) ![2017-01-01-3d](./img/2017-01-01-3d.png)

### 7 days & 30 days
![2017-01-01-7d](./img/2017-01-01-7d.png) ![2017-01-01-30d](./img/2017-01-01-30d.png)
