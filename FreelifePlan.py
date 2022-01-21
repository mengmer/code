# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

class homepage(object):
    '''
    主页计算
    '''
    def __init__(self, *args, **kwargs):
        self.Y_now, self.M_now = 2021, 11
        R_cpi = 2.57 / 100
        R_ca, R_lr, R_hr, R_pr = 2.403 / 100, 10.9813 / 100, 4.0459 / 100, 2.57 / 100
        N_y = 23
        N_law_male = 60
        N_law_female = 55
        Nj = 'df'
        R_mr, R_wd, R_acc, R_a = 4.9 / 100, 10.9813 / 100, 4.0459 / 100, 2.57 / 100


    def user_input_homepage(self):
        '''
        用户输入参数
        '''
        ##Hello盒子
        N_c = 20
        N_r = 50
        City = '景德镇'
        gender = ['男', '女'][0]

        # 日常收支
        I = 10000
        O = 5000
        O_loan = 5000
        N_loan = 24

        # 持有资产
        H_ca = 1
        H_hr = 1
        H_lr = 1
        H_pr = 1

        # 人生保障
        S = 0
        N_s = 25
        N_e = 40
        O_annuity = 10000


    pass