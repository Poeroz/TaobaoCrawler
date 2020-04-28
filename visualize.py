import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

class visual:
    def __init__(self):
        plt.rcParams['font.sans-serif'] = ['Heiti TC']
        plt.rcParams.update({'figure.autolayout': True})
        plt.style.use('seaborn-bright')
        self.phase1_jd = '../data/jd_result.csv'
        self.phase1_tb = '../data/tb_result.csv'
        self.phase2_jd = '../data/jd.csv'
        self.phase2_tb = '../data/tb.csv'
        self.phase3_title = [
            'iPhone XR',
            'iPhone 11',
            '荣耀 9X',
            '华为 Mate30 Pro 5G',
            '红米 K30'
        ]
        self.phase3_tb = [
            '../data/tb_iPhoneXR.csv',
            '../data/tb_iPhone11.csv',
            '../data/tb_honor9X.csv',
            '../data/tb_mate30pro5G.csv',
            '../data/tb_redmik30.csv'
        ]
        self.phase3_jd = [
            '../data/jd_iPhoneXR.csv',
            '../data/jd_iPhone11.csv',
            '../data/jd_honor9X.csv',
            '../data/jd_mate30pro5G.csv',
            '../data/jd_redmik30.csv'
        ]
        self.phase1()
        self.phase2()
        self.phase3()

    def phase1(self):
        fig, ax = plt.subplots()

        df_jd = pd.read_csv(self.phase1_jd, usecols=[1,2,3,4,5], nrows=20)
        df_jd.fillna('', inplace=True)
        df_jd['名称'] = df_jd['品牌'] + df_jd['产品名称'] + ' ' + df_jd['运行内存'] + ' ' + df_jd['机身存储']
        df_jd.sort_values('总销量', inplace=True, ascending=False)

        plt.subplot(121)
        plt.title('京东手机销量排名')
        plt.xticks(rotation=90)
        # plt.xlabel('型号')
        plt.ylabel('销量（个）')
        plt.bar(df_jd['名称'], df_jd['总销量'], color='lightcoral')

        df_tb = pd.read_csv(self.phase1_tb, usecols=[1,2,3,4,5], nrows=20)
        df_tb.fillna('', inplace=True)
        df_tb['名称'] = df_tb['品牌'] + df_tb['型号'] + ' ' + df_tb['运行内存'] + ' ' + df_tb['机身存储']
        df_tb.sort_values('总销量', inplace=True, ascending=False)

        plt.subplot(122)
        plt.title('淘宝手机销量排名')
        plt.xticks(rotation=90)
        # plt.xlabel('型号')
        plt.ylabel('销量（个）')
        plt.bar(df_tb['名称'], df_tb['总销量'], color='skyblue')

        plt.show()


    def phase2(self):
        fig, ax = plt.subplots()

        df_jd = pd.read_csv(self.phase2_jd, usecols=[2])
        df_jd['价格'].astype(int)
        plt.subplot(121)
        cnt = pd.value_counts(df_jd.loc[:, '价格'])
        x = cnt.index
        y = cnt.values
        plt.scatter(x, y, s=20, c='lightcoral')
        plt.xlim(1, 18000)
        plt.xlabel('价格（元）')
        plt.ylabel('数量（个）')
        plt.title('京东价格分布图')

        df_tb = pd.read_csv(self.phase2_tb, usecols=[1])
        df_tb['价格'].astype(int)
        plt.subplot(122)
        cnt = pd.value_counts(df_tb.loc[:, '价格'])
        x = cnt.index
        y = cnt.values
        plt.scatter(x, y, s=20, c='skyblue')
        plt.xlim(1, 18000)
        plt.xlabel('价格（元）')
        plt.ylabel('数量（个）')
        plt.title('淘宝价格分布图')

        plt.show()


    def phase3(self):
        fig, ax = plt.subplots()
        
        for i in range(5):
            plt.subplot(1, 5, i + 1)
            df_jd = pd.read_csv(self.phase3_jd[i], usecols=[1])
            df_tb = pd.read_csv(self.phase3_tb[i], usecols=[1])
            bplot = plt.boxplot([df_jd['价格'], df_tb['价格']], patch_artist=True, labels=['京东', '淘宝'])
            plt.xlabel('电商平台')
            plt.ylabel('价格（元）')
            plt.title(self.phase3_title[i])
            plt.grid(axis='y')
            colors = ['lightcoral', 'skyblue']
            for patch, color in zip(bplot['boxes'], colors):
                patch.set_facecolor(color)
            
        plt.show()
        

if __name__ == '__main__':
    vis = visual() 