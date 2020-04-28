# coding=utf-8
import re
import numpy as np
import pandas as pd

pd.options.mode.chained_assignment = None 

mixbrand = [
    ['荣耀', 'honor'],
    ['华为', 'huawei'],
    ['小米', 'xiaomi'],
    ['苹果', 'apple'],
    ['飞利浦', 'philips'],
    ['尼凯恩', 'neken'],
    ['诺基亚', 'nokia'],
    ['魅族', 'meizu'],
    ['酷比', 'koobee'],
    ['波导', 'bird'],
    ['三星', 'samsung'],
    ['朵唯', 'doov'],
    ['长虹', 'changhong'],
    ['硕王', 'sailf'],
    ['天语', 'k-touch'],
    ['努比亚', 'nubia'],
    ['一加', 'oneplus'],
    ['誉品', 'yepen'],
    ['酷派', 'coolpad'],
    ['美图', 'meitu'],
    ['索品', 'swopy'],
    ['乐视', 'letv'],
    ['唯米','weiimi'],
    ['康佳', 'konka'],
    ['中兴', 'zte'],
    ['金立', 'gionee'],
    ['京立', 'gineek'],
    ['泰美利', 'taiml'],
    ['欧沃', 'owwo'],
    ['欧博信', 'obxin'],
    ['黑莓', 'blackberry'],
    ['海尔', 'haier'],
    ['酷和', 'kuh'],
    ['索尼', 'sony'],
    ['联想', 'lenovo'],
    ['摩托罗拉', 'motorola'],
    ['纽曼', 'newman'],
    ['多亲', 'qin'],
    ['海信', 'hisense'],
    ['锤子', 'smartisian'],
]

mixbrand_dict = dict(mixbrand)

class dataprocess_TB:
    def __init__(self):
        self.path = '../data/tb.csv'
        self.df = pd.read_csv(self.path, usecols=[1,2,3,4,5,6])
        self.grouped_result = pd.DataFrame(columns=['品牌', '型号', '机身存储', '运行内存', '总销量'])
        self.df.dropna(subset=['品牌', '型号'], inplace=True)
    
        self.process_brand()
        self.process_model()
        self.process_disk()
        self.process_memory()
        self.process_deal()
        self.process_price()

        self.group()

        self.df.reset_index(drop=True, inplace=True)
        self.grouped_result.reset_index(drop=True, inplace=True)
        self.df.to_csv('../data/tb_fresh.csv')
        self.grouped_result.to_csv('../data/tb_result.csv')

    def process_brand(self):
        brand = self.df['品牌']
        brand = brand.str.lower()
        for i in range(len(brand)):
            for ch, en in mixbrand:
                if en in brand.iloc[i] or ch in brand.iloc[i]:
                    brand.iloc[i] = ch      
                    break         
        self.df['品牌'] = brand

    def process_model(self):
        rep = self.df['型号'].str.contains('骁龙')
        self.df['型号'][rep] = None
        self.df.dropna(subset=['型号'], inplace=True)
        self.df['型号'] = self.df['型号'].str.replace('其他', '')
        model = self.df['型号']
        model = model.str.replace(' ', '')
        for i in range(len(model)):
            ch = self.df['品牌'].iloc[i]
            if ch in model.iloc[i]:
                model.iloc[i] = model.iloc[i].replace(ch, '')
            try:
                en = mixbrand_dict[ch]
                reg = re.compile(re.escape(en), re.IGNORECASE)
                model.iloc[i] = reg.sub('', model.iloc[i])
            except KeyError:
                pass
        self.df['型号'] = model

    def process_disk(self):
        disk = self.df['机身存储']
        disk = disk.str.extract(r'(\d+[G|M|T]B)', expand=False)
        self.df['机身存储'] = disk

    def process_memory(self):
        memory = self.df['运行内存']
        memory = memory.str.extract(r'(\d+[G|M|T]B)', expand=False)
        self.df['运行内存'] = memory

    def process_deal(self):
        deal = self.df['销量']
        deal = deal.str.replace(r'(\+*人收货)', '')
        big = deal.str.contains('万')
        deal[big] = deal[big].str.replace('万', '').astype(float) * 10000
        deal = deal.astype(int)
        self.df['销量'] = deal

    def process_price(self):
        self.df['价格'] = self.df['价格'].astype(float)

    def group(self):
        grouped = self.df.groupby(['品牌', '型号'])
        for (a, b), e in grouped:
            self.grouped_result = self.grouped_result.append(pd.DataFrame({
                '品牌': [a],
                '型号': [b],
                '机身存储': [e['机身存储'].iloc[0]],
                '运行内存': [e['运行内存'].iloc[0]],
                '总销量': [e['销量'].sum()]
            }))
        self.grouped_result.sort_values('总销量', inplace=True, ascending=False)
            

class dataprocess_JD:
    def __init__(self):
        self.path = '../data/jd.csv'
        self.df = pd.read_csv(self.path, usecols=[1,2,3,4,5,6])
        self.grouped_result = pd.DataFrame(columns=['品牌', '产品名称', '机身存储', '运行内存', '总销量'])
        self.df.dropna(subset=['产品名称'], inplace=True)

        self.process_brand()
        self.process_model()
        self.process_disk()
        self.process_memory()
        self.process_deal()
        self.process_price()

        self.group()

        self.df.reset_index(drop=True, inplace=True)
        self.grouped_result.reset_index(drop=True, inplace=True)
        self.df.to_csv('../data/jd_fresh.csv')
        self.grouped_result.to_csv('../data/jd_result.csv')

    def process_brand(self):
        brand = self.df['品牌']
        brand = brand.str.lower()
        for i in range(len(brand)):
            if type(brand.iloc[i]) is str:
                for ch, en in mixbrand:
                    if en in brand.iloc[i] or ch in brand.iloc[i]:
                        brand.iloc[i] = ch      
                        break
            else:
                for ch, en in mixbrand:
                    if en in self.df['产品名称'].iloc[i] or ch in self.df['产品名称'].iloc[i]:
                        brand.iloc[i] = ch
                        break                
        self.df['品牌'] = brand
        self.df.dropna(subset=['品牌'], inplace=True)

    def process_model(self):
        model = self.df['产品名称']
        model = model.str.replace(' ', '')
        for i in range(len(model)):
            ch = self.df['品牌'].iloc[i]
            if ch in model.iloc[i]:
                model.iloc[i] = model.iloc[i].replace(ch, '')
            try:
                en = mixbrand_dict[ch]
                reg = re.compile(re.escape(en), re.IGNORECASE)
                model.iloc[i] = reg.sub('', model.iloc[i])
            except KeyError:
                pass
        self.df['产品名称'] = model

    def process_disk(self):
        disk = self.df['机身存储']
        disk = disk.str.extract(r'(\d+[G|M|T]B)', expand=False)
        self.df['机身存储'] = disk

    def process_memory(self):
        memory = self.df['运行内存']
        memory = memory.str.extract(r'(\d+[G|M|T]B)', expand=False)
        self.df['运行内存'] = memory

    def process_deal(self):
        deal = self.df['销量']
        big = deal.str.contains('万+')
        small = (1 - big).astype(np.bool)
        deal[big] = deal[big].str.replace(r'万\+', '').astype(float) * 10000
        deal[small] = deal[small].str.replace('+', '').astype(int)
        deal[big] = deal[big].astype(int)
        self.df['销量'] = deal

    def process_price(self):
        self.df['价格'] = self.df['价格'].astype(float)

    def group(self):
        grouped = self.df.groupby(['品牌', '产品名称'])
        for (a, b), e in grouped:
            self.grouped_result = self.grouped_result.append(pd.DataFrame({
                '品牌': [a],
                '产品名称': [b],
                '机身存储': [e['机身存储'].iloc[0]],
                '运行内存': [e['运行内存'].iloc[0]],
                '总销量': [e['销量'].sum()]
            }))
        self.grouped_result.sort_values('总销量', inplace=True, ascending=False)
            

if __name__ == '__main__':
    dataprocess_tb = dataprocess_TB()
    dataprocess_jd = dataprocess_JD()
