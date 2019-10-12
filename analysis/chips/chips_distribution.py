# -*- coding:utf-8 -*-
"""
@author: fsksf
@since: 2019-10-11 11:51
筹码分布， CYQ
"""

import numpy as np


class CYQ:
    def __init__(self, low_arr, high_arr, volume_arr, amount=100, precision=4):
        self._low_arr = low_arr
        self._high_arr = high_arr
        self._volume_arr = volume_arr
        self._amount = amount
        self._precision = precision

        self._low = min(self._low_arr)
        self._high = max(self._high_arr)

        self._sep = self.calc_separate(self._low, self._high, self._amount, self._precision)
        self._total_cost_list = self.calc_cost_list(self._low, self._high, self._sep)

    @staticmethod
    def calc_separate(low, high, amount, precision=4):
        # 计算区间刻度
        sep = ((high - low) * 10 ** precision // amount + 1) / 10 ** precision
        return sep

    @staticmethod
    def calc_cost_list(low, high, sep, precision=4):
        cost_list = [low, ]
        c = low
        while True:
            c += sep
            cost_list.append(round(c, precision))
            # index==-1 位置大于high
            if c > high:
                break
        return cost_list

    def index_of_cost(self, cost):
        return int((cost - self._low) // self._sep + 1)

    def calc_daily_cyq(self, low, high, volume, shape='triangle'):
        # square，triangle
        low_index = self.index_of_cost(low)
        high_index = self.index_of_cost(high)
        cost_len = int(high_index - low_index + 1)

        cost_arr = np.zeros((len(self._total_cost_list)))
        if shape == 'triangle':
            cost_list = self._triangle_daily_cyq(volume, cost_len)
        elif shape == 'square':
            cost_list = self._square_daily_cyq(volume, cost_len)
        else:
            raise NotImplementedError
        cost_arr[low_index: high_index+1] = cost_list
        return cost_arr

    @staticmethod
    def _triangle_daily_cyq(volume, cost_len):
        # area = 1/2 * ah
        mid_volume = volume * 2 / cost_len
        half_cost_len = cost_len / 2

        tan = mid_volume / half_cost_len
        cost_volume_list = []
        for i in range(cost_len):
            if i < half_cost_len:
                c_volume = tan * i
            else:
                c_volume = tan * (cost_len - i)
            cost_volume_list.append(c_volume)
        return cost_volume_list

    def _square_daily_cyq(self, amount, cost_list):
        raise NotImplementedError

    def calc_cyq(self, shape='triangle'):
        all_cost_list = []
        for i in range(len(self._low_arr)):
            daily_cost_arr = self.calc_daily_cyq(self._low_arr[i],
                                                 self._high_arr[i],
                                                 self._volume_arr[i],
                                                 shape=shape)
            all_cost_list.append(daily_cost_arr)
        cost_arr = np.vstack(all_cost_list)
        cost = cost_arr.sum(axis=0)
        return list(zip(self._total_cost_list, cost))


if __name__ == '__main__':
    import time
    data = np.array([[175.225, 177.75, 173.8,176.57,66539371],
                    [175.88, 177.5, 174.441,176.89,34068180],
                    [178.25, 184.25, 178.17,183.83,56201317],
                    [185.18, 187.67, 184.75,185.16,42451423],
                    [184.99, 186.22, 183.665,186.05,28402777],
                    [186.55, 187.4, 185.22,187.36,23211241],
                    [187.74, 190.37, 187.65,190.04,27989289],
                    [189.49, 190.06, 187.45,188.59,26212221],
                    [189.01, 189.53, 187.86,188.15,20778772],
                    [186.78, 187.07, 185.1,186.44,23695159],
                    [186.07, 188.46, 186.0,188.18,19183064],
                    [188.0, 188.91, 186.36,186.99,17294029],
                    [187.19, 187.81, 186.13,186.31,18297728],
                    [188.0, 189.27, 186.911,187.63,18400787],
                    [188.375, 188.88, 186.78,187.16,15240704],
                    [186.35, 188.5, 185.76,188.36,20058415],
                    [188.77, 188.84, 186.21,188.15,23233975],
                    [188.23, 189.65, 187.65,188.58,17460963],
                    [187.6, 188.75, 186.87,187.9,22514075]])

    aapl_cyq = CYQ(data[:, 2], data[:, 1], data[:, 4])
    start = time.time()
    out = aapl_cyq.calc_cyq()
    print(time.time() - start)
    import pandas as pd
    import matplotlib.pyplot as plt

    print(out)
    df = pd.DataFrame(out, columns=['cost', 'volumes'])

    plt.plot(df['cost'], df['volumes'])
    plt.show()
