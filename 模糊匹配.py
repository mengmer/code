
#%%
# 齐欣慧择的数据处理
import pandas as pd
df1 = pd.read_excel(r"D:\战略检视\业务策略总结\下沉市场特点\保险密度统计\city_gdp.xlsx")
df2 = pd.read_excel(r"D:\战略检视\业务策略总结\下沉市场特点\保险密度统计\city_no_sink.xlsx")
list1 = []
count = 0
city_type = 4
df2.fillna('空值', inplace=True)
for tup in df1.itertuples():
    city_name = tup[1]
    test_city_1 = df2['city_1'].str.contains(city_name)
    test_city_new1 = df2['city_new1'].str.contains(city_name)
    test_city_2 = df2['city_2'].str.contains(city_name)
    if test_city_1.any():
        city_type = 1
    if test_city_new1.any():
        city_type = 2
    if test_city_2.any():
        city_type = 3
    list1.append(city_type) 
    city_type = 4
df1['city_type'] = list1

df1.to_excel(r"D:\战略检视\业务策略总结\下沉市场特点\保险密度统计\sink_data.xlsx")


# df = pd.read_excel(r"D:\战略检视\业务策略总结\下沉市场特点\保险密度统计\齐欣慧择data_new.xlsx")
# df3 = df.groupby(['年份', '预算险种', 'is_sink'], as_index=False)['投保单数'].sum()


#%%
import pandas as pd
import numpy as np
pd.set_option('mode.use_inf_as_na', True)
df = pd.read_excel(r"D:\战略检视\业务策略总结\下沉市场特点\保险密度统计\data_new.xlsx")
# def cal_grow(df):
#     '''
#     :param df:分组计算增长率，默认两位小数百分比，空值为nan
#     :return:
#     '''
#     return df.Insurance_density.pct_change().mul(100).round(2).map(lambda x: '{0:g}%'.format(x) if x == x else x)
# df1 = df.groupby('City').apply(cal_grow)

Iusure_density_grow = df.groupby('City')['Insurance_density'].pct_change().mul(100).round(2).map(lambda x: '{0:g}%'.format(x) if x == x else x)
updi_grow = df.groupby('City')['UPDI'].pct_change().mul(100).round(2).map(lambda x: '{0:g}%'.format(x) if x == x else x)
df['Iusure_density_grow'] = Iusure_density_grow
df['updi_grow'] = updi_grow
df = df.loc[df['Iusure_density_grow'] != 'inf%',]
# df.fillna(0, inplace=True)
df.updi_grow = df.updi_grow.map(lambda x:  x if str(x) == 'nan' else float(x[:-1])/100)
df.Iusure_density_grow = df.Iusure_density_grow.map(lambda x:  x if str(x) == 'nan' else float(x[:-1])/100)
df.to_excel(r"D:\战略检视\业务策略总结\下沉市场特点\保险密度统计\data_grow_new.xlsx")

#%%

import pandas as pd
import numpy as np
pd.set_option('mode.use_inf_as_na', True)
df = pd.read_excel(r"D:\战略检视\业务策略总结\下沉市场特点\保险密度统计\data_grow_new.xlsx")
df1 = df.groupby(['city_type', 'Year'], as_index=False)['Iusure_density_grow'].mean()
df2 = df.groupby(['is_sink', 'Year'], as_index=False)['Iusure_density_grow'].mean()
df3 = df.groupby(['is_sink', 'Year'], as_index=False)['Insurance_density'].mean()
df4 = df.groupby(['City', 'is_sink'], as_index=False)[['Iusure_density_grow', 'updi_grow']].mean()
df5 = df.groupby(['City'], as_index=False)['updi_grow'].mean()


#%%
import pandas as pd
import numpy as np
df = pd.read_excel(r"D:\战略检视\业务策略总结\下沉市场特点\保险密度统计\各级城市客均保费(含保单数).xls")
df1 = df.groupby(['城市类别', '投保年份'], as_index=False)[['投保人数', '首年规模保费', '保单数']].sum()

# df_sink = df.loc[df['city_type'] == 4, ]
# df2 = df.groupby(['所属省份'], as_index=False)["is_10000"].sum()
# df3 = df.groupby(['所属省份'], as_index=False)["5000_10000"].sum()



