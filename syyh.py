
import pandas as pd
# from fancyimpute import KNN
df = pd.read_excel(r'./syyhsj_1.xlsx')
print('1')
df = df.interpolate()
df.to_csv(r'商业银行数据.csv')