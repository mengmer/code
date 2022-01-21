# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt


# %%================1 用户输入参数=====================
##Hello盒子
(N_c, N_r) = (20, 50)
City = ['上海', '杭州'][0]
gender = ['男', '女'][0]

# 日常收支
(I, O) = (10000, 5000)
(O_loan, N_loan) = (3000, 120)

# 持有资产
(H_ca, H_lr, H_hr, H_pr) = (40000, 40000, 20000, 100000)

# 人生保障
S = 10000
(N_s, N_e) = (1, 50)  # 年金开始缴纳和结束的年龄
O_annuity = 10000

# 愿望1-婚礼
(Y_1, M_1) = (2022, 11)
(C_1, E_1) = (0, 40000)

(R_1, N_1) = (10 / 100, 2)
(R_ca_1, R_lr_1, R_hr_1) = (50 / 100, 50 / 100, 50 / 100)

# %%================2 预设参数=====================
Y_now, M_now = 2021, 11
R_cpi = 2.57 / 100
R_ca, R_lr, R_hr, R_pr = 3.2 / 100, 5.01 / 100, 7.53 / 100, 3.2 / 100


# %%================3 预定义函数=====================
def Month_Index(age, month):  # **new**
    return 12 * (age - 1) + month  # assume birthday is Jan 1th


def Geo_Term(first_item, ratio, num_term):
    return first_item * pow(ratio, num_term - 1)


def Geo_Series(first_item, ratio, num_term):
    return first_item * (1 - pow(ratio, num_term)) / (1 - ratio)


def Holding_Eva(start_MI, end_MI, P_ca, P_lr, P_hr, P_pr, total_flow):
    for i in range(start_MI, end_MI + 1):
        if total_flow[i - 1] + P_ca[i - 1] >= 0:
            P_ca[i] = Geo_Term(total_flow[i - 1] + P_ca[i - 1], pow(1 + R_ca, 1 / 12), 2)
            P_lr[i] = Geo_Term(P_lr[i - 1], pow(1 + R_lr, 1 / 12), 2)
            P_hr[i] = Geo_Term(P_hr[i - 1], pow(1 + R_hr, 1 / 12), 2)
            P_pr[i] = Geo_Term(P_pr[i - 1], pow(1 + R_pr, 1 / 12), 2)
        elif total_flow[i - 1] + P_ca[i - 1] + P_lr[i - 1] >= 0:
            P_ca[i] = 0
            P_lr[i] = Geo_Term(total_flow[i - 1] + P_ca[i - 1] + P_lr[i - 1], pow(1 + R_lr, 1 / 12), 2)
            P_hr[i] = Geo_Term(P_hr[i - 1], pow(1 + R_hr, 1 / 12), 2)
            P_pr[i] = Geo_Term(P_pr[i - 1], pow(1 + R_pr, 1 / 12), 2)
        elif total_flow[i - 1] + P_ca[i - 1] + P_lr[i - 1] + P_hr[i - 1] >= 0:
            P_ca[i] = 0
            P_lr[i] = 0
            P_hr[i] = Geo_Term(total_flow[i - 1] + P_ca[i - 1] + P_lr[i - 1] + P_hr[i - 1], pow(1 + R_hr, 1 / 12), 2)
            P_pr[i] = Geo_Term(P_pr[i - 1], pow(1 + R_pr, 1 / 12), 2)
        elif total_flow[i - 1] + P_ca[i - 1] + P_lr[i - 1] + P_hr[i - 1] + P_pr[i - 1] >= 0:
            P_ca[i] = Geo_Term(total_flow[i - 1] + P_ca[i - 1] + P_lr[i - 1] + P_hr[i - 1] + P_pr[i - 1],
                               pow(1 + R_ca, 1 / 12), 2)  # 固定资产折现了
            P_lr[i] = 0
            P_hr[i] = 0
            P_pr[i] = 0
        else:
            P_ca[i] = total_flow[i - 1] + P_ca[i - 1] + P_lr[i - 1] + P_hr[i - 1] + P_pr[i - 1]
            P_lr[i] = 0
            P_hr[i] = 0
            P_pr[i] = 0
    return P_ca, P_lr, P_hr, P_pr


# %%================推导出的参数=====================
# Hello盒子
N = N_r - N_c
MI_c = Month_Index(N_c, M_now)  # **new**
MI_r = Month_Index(N_r, M_now)
MI_die = Month_Index(100, 12)

# 日常收支
income = np.repeat(0, MI_die + 1)  # **new** 先创建三个为零的数列
living_expense = np.repeat(0, MI_die + 1)
loan_repayment = np.repeat(0, MI_die + 1)

for i in range(MI_c, MI_r):  # range左闭右开
    income[i] = Geo_Term(I, 1 + R_cpi, np.ceil(i / 12) - N_c + 1)

for i in range(MI_c, MI_die + 1):
    living_expense[i] = Geo_Term(-O, 1 + R_cpi, np.ceil(i / 12) - N_c + 1)

for i in range(MI_c, MI_c + N_loan):  # N_loan个月
    loan_repayment[i] = -O_loan

# 人生保障 - 基础养老金 & 个人账户养老金


# 人生保障 - 年金
MI_s = Month_Index(N_s, M_now)  # **new**
MI_e = Month_Index(N_e, M_now)
annuity = np.repeat(0, MI_die + 1)
for i in range(min(MI_s, MI_c), MI_e + 1, 12):
    annuity[i] = -O_annuity  # 每年需交年金
A_retire = 1e5  # 退休时间可以领取年金,暂时放了一个数值这里需要添加计算逻辑

# 愿望
wish_1 = np.repeat(0, MI_die + 1)
MI_1 = Month_Index(N_c + Y_1 - Y_now, M_1)
for i in range(MI_1 + 1, MI_1 + N_1 + 1):
    wish_1[i] = -R_1 * income[i]

# 汇总
flow_matrix = np.array([income, living_expense, loan_repayment, annuity])
# total in&out flow
total_flow = np.sum(flow_matrix, axis=0)  # colunm-wise summation

# %%================推导出的资产变化趋势=====================

P_ca = np.repeat(0, MI_die + 1)
P_hr = np.repeat(0, MI_die + 1)
P_lr = np.repeat(0, MI_die + 1)
P_pr = np.repeat(0, MI_die + 1)

P_ca[MI_c] = H_ca
P_hr[MI_c] = H_hr
P_lr[MI_c] = H_lr
P_pr[MI_c] = H_pr

(P_ca, P_lr, P_hr, P_pr) = Holding_Eva(MI_c + 1, MI_die, P_ca, P_lr, P_hr, P_pr, total_flow)

holding_matrix = np.array([P_ca, P_lr, P_hr, P_pr])
total_holding = np.sum(holding_matrix, axis=0)

# %%================4 资产需求参考 - 退休时点手上需要持有的资产价值 =====================

# 没有填写日常收支盒子情况下，公式不变
# 但也可把填写&未填写日常收支盒子的两种情况并为一种, 通过设定O的默认值为O_city/12

# 填写日常收支盒子的情况下：
# 把退休后的花销投射回退休时点
P_retire = 0
for i in range(MI_r, MI_die + 1):
    P_retire -= Geo_Term(total_flow[i], 1 / pow(1 + R_ca, 1 / 12), i - MI_r + 1)

# %%================5 退休时点拥有的资产价值 =====================

# 5.1日常收支 & 5.2持有资产 & 5.3.1 养老保险
Q_retire = np.sum(total_holding[MI_r])
# 5.3.2 年金
Q_retire += A_retire

# %%================6 准备度 =====================

# 是否破产
bankrupt = np.size(np.where(total_holding < 0)[0]) > 0

# 假如破产，破产年龄
if bankrupt:
    bankrupt_age = np.floor(np.where(total_holding < 0)[0][0] / 12)

# 准备度
if bankrupt and bankrupt_age <= N_r:
    Readiness = 0
elif Q_retire < 0:
    Readiness = 0
elif P_retire <= 0:  # 考虑一种特殊情况，退休时点手上不需要持有资产
    Readiness = 100
else:
    Readiness = round(min(100 * Q_retire / P_retire, 100))  # 准备度不能超过100%

# %%================7 愿望盒子 =====================
# 愿望时点可以使用的剩余总金额，已经减去愿望需要的一次性开销
U_1 = R_ca_1 * P_ca[MI_1] + R_lr_1 * P_lr[MI_1] + R_hr_1 * P_hr[MI_1] + C_1 - E_1

# 7.1 能否按时完成
if U_1 >= 0 and U_1 + np.sum(total_flow[MI_1 + 1: MI_1 + N_1 + 1] + wish_1[MI_1 + 1: MI_1 + N_1 + 1]) >= 0:
    Can_1 = True
else:
    Can_1 = False

# 7.2 预计时长
if Can_1:
    Mon_1 = N_1 + MI_1 - MI_c
else:
    Mon_1 = N_1 + MI_1 - MI_c + np.ceil(
        -(U_1 + np.sum(total_flow[MI_1 + 1: MI_1 + N_1 + 1] + wish_1[MI_1 + 1: MI_1 + N_1 + 1])) / total_flow[
            MI_1 + N_1 + 1])

# %% Results

plt.plot(range(0, MI_die + 1), total_flow, label='total in&out flow')
plt.plot(range(0, MI_die + 1), holding_matrix[0, :], label='saving')
plt.plot(range(0, MI_die + 1), holding_matrix[1, :], label='low risk')
plt.plot(range(0, MI_die + 1), holding_matrix[2, :], label='high risk')
plt.plot(range(0, MI_die + 1), holding_matrix[3, :], label='property')

plt.legend()
plt.show()
if bankrupt:
    print(bankrupt_age, "岁破产")
print("准备度：", Readiness, '%')
print("资产需求参考：", round(P_retire))
print("假如有婚礼愿望-能否按时完成：", Can_1, " 预计时长：", Mon_1)



# # %% 当愿望可以按时完成时，加上婚礼愿望，进一步计算资产需求参考 & 准备度
#
# print("当愿望可以按时完成时，加上婚礼愿望，进一步计算资产需求参考 & 准备度")
#
# # %================推导出的资产变化趋势=====================
#
#
# flow_matrix = np.array([income, living_expense, loan_repayment, annuity, wish_1])
# total_flow = np.sum(flow_matrix, axis=0)
#
# if R_ca_1 * P_ca[MI_1] + C_1 - E_1 >= 0:
#     P_ca[MI_1] = P_ca[MI_1] + C_1 - E_1
# elif R_ca_1 * P_ca[MI_1] + R_lr_1 * P_lr[MI_1] + C_1 - E_1 >= 0:
#     P_ca[MI_1] = P_ca[MI_1] - R_ca_1 * P_ca[MI_1]
#     P_lr[MI_1] = P_lr[MI_1] + R_ca_1 * P_ca[MI_1] + C_1 - E_1
# elif R_ca_1 * P_ca[MI_1] + R_lr_1 * P_lr[MI_1] + R_hr_1 * P_hr[MI_1] + C_1 - E_1 >= 0:
#     P_ca[MI_1] = P_ca[MI_1] - R_ca_1 * P_ca[MI_1]
#     P_lr[MI_1] = P_lr[MI_1] - R_lr_1 * P_lr[MI_1]
#     P_hr[MI_1] = P_hr[MI_1] + R_ca_1 * P_ca[MI_1] + R_lr_1 * P_lr[MI_1] + C_1 - E_1
#
# (P_ca, P_lr, P_hr, P_pr) = Holding_Eva(MI_1 + 1, MI_die, P_ca, P_lr, P_hr, P_pr, total_flow)
#
# holding_matrix = np.array([P_ca, P_lr, P_hr, P_pr])
# total_holding = np.sum(holding_matrix, axis=0)
#
# # %================4 资产需求参考 - 退休时点手上需要持有的资产价值 =====================
#
# # 没有填写日常收支盒子情况下，公式不变
# # 但也可把填写&未填写日常收支盒子的两种情况并为一种, 通过设定O的默认值为O_city/12
#
# # 填写日常收支盒子的情况下：
# # 把退休后的花销投射回退休时点
# P_retire = 0
# for i in range(MI_r, MI_die + 1):
#     P_retire -= Geo_Term(total_flow[i], 1 / pow(1 + R_ca, 1 / 12), i - MI_r + 1)
#
# # %================5 退休时点拥有的资产价值 =====================
#
# # 5.1日常收支 & 5.2持有资产 & 5.3.1 养老保险 & 5.4 愿望盒子
# Q_retire = np.sum(total_holding[MI_r])
# # 5.3.2 年金
# Q_retire += A_retire
#
# # %================6 准备度 =====================
#
# # 是否破产
# bankrupt = np.size(np.where(total_holding < 0)[0]) > 0
#
# # 假如破产，破产年龄
# if bankrupt:
#     bankrupt_age = np.floor(np.where(total_holding < 0)[0][0] / 12)
#
# # 准备度
# if bankrupt and bankrupt_age <= N_r:
#     Readiness = 0
# elif Q_retire < 0:
#     Readiness = 0
# elif P_retire <= 0:  # 考虑一种特殊情况，退休时点手上不需要持有资产
#     Readiness = 100
# else:
#     Readiness = round(min(100 * Q_retire / P_retire, 100))  # 准备度不能超过100%
#
# plt.plot(range(0, MI_die + 1), total_flow, label='total in&out flow')
# plt.plot(range(0, MI_die + 1), holding_matrix[0, :], label='saving')
# plt.plot(range(0, MI_die + 1), holding_matrix[1, :], label='low risk')
# plt.plot(range(0, MI_die + 1), holding_matrix[2, :], label='high risk')
# plt.plot(range(0, MI_die + 1), holding_matrix[3, :], label='property')
#
# plt.legend()
# plt.show()
# if bankrupt:
#     print(bankrupt_age, "岁破产")
# print("准备度：", Readiness, '%')
# print("资产需求参考：", round(P_retire))