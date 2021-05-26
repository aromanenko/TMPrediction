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

def get_res(data, startdate='2020-01-01'):
    date_idx = data.index.get_level_values('date')
    res = np.array(data[(date_idx >= startdate)]['p1_win'])
    return res
    
def get_names(data, startdate = '2020-01-01'):
    date_idx = data.index.get_level_values('date')
    names = np.array(data[(date_idx >= startdate)].reset_index()[['p1', 'p2']]).transpose()
    return names

def loss_function(res, pred):
    return (pred[0] - res) ** 2 + (pred[1] - abs(res - 1)) ** 2

def aggregate(df, startdate, pred_list, loss_func = loss_function, weights = None, m = 2):
    player_names = get_names(df, startdate)
    res = get_res(df, startdate)
    pred_df = make_df(pred_list)
    val = pred_df.values.transpose()
    pred = np.array(list(map(lambda x : np.array(list(map(list, x))), val)))
    T = len(res)
    K = len(pred)
    res_df = pd.DataFrame()
    names = pred_df.columns
    if not weights:
        weights = np.full(K, 1/K)
    agg_pred = np.zeros(2 * T).reshape(T, 2)
    start_new_period = 0
    for t in range(1, T):
        if res[t] == -1 and start_new_period == 0:
            start_new_period = t
        gamma = pred[:,t]
        def G(omega):
            return -np.log(np.inner(weights, np.exp(-loss_func(omega, np.transpose(gamma)))))
        delta = abs(G(1) - G(0))
        if (delta >= m):
            s = min(G(1), G(0)) + m
        else:
            s = (m + G(0) + G(1)) / 2
        agg_pred[t] = np.array([abs(s - G(1)) / 2, abs(s - G(0)) / 2])
        if res[t] != -1:
            weights = (weights * np.exp(-loss_func(res[t], np.transpose(gamma))))
            weights /= np.sum(weights)
    res_df['p1'] = player_names[0]
    res_df['p2'] = player_names[1]
    res_df['p1_win_prob'] = agg_pred.transpose()[0]
    res_df['p2_win_prob'] = agg_pred.transpose()[1]
    res_df = res_df[start_new_period:]
    res_df = res_df.set_index(['Player1', 'Player2'])
    return res_df
