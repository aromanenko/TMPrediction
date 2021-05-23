import numpy as np
import pandas as pd
import time
import datetime

def make_df(models_pred):
    preds = []
    for x in models_pred:
        x = np.array(list(map(lambda x: np.array([x[1], x[0]]), x)))
        preds.append(x)
    pred = np.array(preds)
    pred_list = list(map(lambda x : list(map(list, x)), pred))
    return pd.DataFrame(pred_list).transpose()

def get_res(data, startdate1='2020-01-01'):
    date_idx = data.index.get_level_values('date')
    res = np.array(data[(date_idx >= startdate1)]['p1_win'])
    return res
    
def loss_function(res, pred):
    return (pred[0] - res) ** 2 + (pred[1] - abs(res - 1)) ** 2

def aggregate(res, pred_df, loss_func = loss_function, weights = None, m = 2):
    val = pred_df.values.transpose()
    pred = np.array(list(map(lambda x : np.array(list(map(list, x))), val)))
    T = len(res)
    K = len(pred)
    res_df = pd.DataFrame()
    names = pred_df.columns
    for i in range(K):
        res_df[str(names[i]) + '_mean'] = np.zeros(T)
        res_df[str(names[i]) + '_mean_100'] = np.zeros(T)
        res_df[str(names[i]) + '_accumulated'] = np.zeros(T)
        res_df[str(names[i]) + '_weight'] = np.zeros(T)
    res_df['composition_mean'] = np.zeros(T)
    res_df['composition_mean_100'] = np.zeros(T)
    res_df['composition_accumulated'] = np.zeros(T)
    if not weights:
        weights = np.full(K, 1/K)
    agg_pred = np.zeros(2 * T).reshape(T, 2)
    for t in range(1, T):
        gamma = pred[:,t]
        def G(omega):
            return -np.log(np.inner(weights, np.exp(-loss_func(omega, np.transpose(gamma)))))
        delta = abs(G(1) - G(0))
        if (delta >= m):
            s = min(G(1), G(0)) + m
        else:
            s = (m + G(0) + G(1)) / 2
        agg_pred[t] = np.array([abs(s - G(1)) / 2, abs(s - G(0)) / 2])
        if res[t] != None:
            weights = (weights * np.exp(-loss_func(res[t], np.transpose(gamma))))
            weights /= np.sum(weights)
        for i in range(K):
            if (res[t] != None):
                res_df[str(names[i])+'_accumulated'][t] = res_df[str(names[i])+'_accumulated'][t - 1] + loss_func(res[t], gamma[i])
                res_df[str(names[i])+'_mean'][t] = res_df[str(names[i])+'_accumulated'][t] / t
            res_df[str(names[i]) + '_weight'][t] = weights[i]
            if t > 100 and res[t] != None:
                res_df[str(names[i])+'_mean_100'][t] = (res_df[str(names[i])+'_accumulated'][t] - res_df[str(names[i])+'_accumulated'][t - 100]) / 100
            elif res[t] != None:
                res_df[str(names[i])+'_mean_100'][t] = res_df[str(names[i])+'_mean'][t]
        if res[t] != None:
            res_df['composition_accumulated'][t] = res_df['composition_accumulated'][t - 1] + loss_func(res[t], agg_pred[t])
            res_df['composition_mean'][t] = res_df['composition_accumulated'][t] / t
        if t > 100 and res[t] != None:
            res_df['composition_mean_100'][t] = (res_df['composition_accumulated'][t] - res_df['composition_accumulated'][t - 100]) / 100
        elif res[t] != None:
            res_df['composition_mean_100'][t] = res_df['composition_mean'][t]
    res_df['composition_k1'] = agg_pred.transpose()[0]
    res_df['composition_k2'] = agg_pred.transpose()[1]
    return res_df
