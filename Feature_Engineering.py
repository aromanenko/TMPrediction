import datetime
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.preprocessing import OrdinalEncoder
from itertools import product
from ipywidgets import IntProgress
from IPython.display import display
pd.options.display.max_columns = 50
pd.options.mode.chained_assignment = None


def log_progress(sequence, every=10):

    progress = IntProgress(min=0, max=len(sequence), value=0)
    display(progress)
    
    for index, record in enumerate(sequence):
        if index % every == 0:
            progress.value = index
        yield record
        

def fix_time(df):
    time = []
    date_fx = []
    months = {"Jan": 1, "Feb": 2, "Mar": 3,
              "Apr": 4, "May": 5, "Jun": 6,
              "Jul": 7, "Aug": 8, "Sep": 9,
              "Oct": 10, "Nov": 11, "Dec": 12
             }
    for date in df["date"]:
        mas = date.split()
        date_fx.append(datetime.date(int(mas[2][:-1]), months[mas[1]], int(mas[0])))
        podmas = mas[-1].split(":")
        time.append(datetime.time(int(podmas[0]), int(podmas[1]), 0))
    df["time"] = time
    df["date"] = date_fx
    
    
def fix_names1(players):
    print("FIXING PLAYERS' NAMES...")
    progress = IntProgress(min=0, max=len(players), value=0)
    display(progress)
    
    arr = []
    for i, x in enumerate(players['name']):
        surname = ''
        tmp = x.split(' ')
        if len(tmp) > 1:
            surname = tmp[-1]
            name = tmp[0][0] + '.'
            arr.append(surname + " " + name)
        else:
            arr.append(np.nan)
        
        ## Progress fill
        if (i % 10 == 0):
            progress.value = i
        
    players['name'] = arr
    
def fix_names2(players):
    ## Progress bar
    progress = IntProgress(min=0, max=len(players), value=0)
    display(progress)
    arr = []
    for i, x in enumerate(players['name']):
        surname = ''
        tmp = x.split(' ')
        if len(tmp) > 1:
            surname = " ".join(tmp[1:])
            name = tmp[0][0] + '.'
            arr.append(surname + " " + name)
        else:
            arr.append(np.nan)
            
        ## Progress fill
        if (i % 10 == 0):
            progress.value = i
    players['name'] = arr
    print("PLAYERS' NAMES FIXED\n")


def add_stats(df, players, is_fst_time=1):
    names = ['p1_height', 'p1_birth', 'p1_hand', 'p1_nation']
    if is_fst_time:
    	print("IMPORTING STATIC STATS...")
    progress = IntProgress(min=0, max=len(df), value=0)
    display(progress)
    if is_fst_time:
        for name in names:
            df[name] = [np.nan for x in range(len(df))]
        for name in names:
            df[name.replace('1', '2')] = [np.nan for x in range(len(df))]
    arr1_player1 = []
    arr1_player2 = []
    arr2_player1 = []
    arr2_player2 = []
    arr3_player1 = []
    arr3_player2 = []
    arr4_player1 = []
    arr4_player2 = []
    for i in range(len(df)):
        try:
            player1 = players[df['player1'][i]:].head(1)
            arr1_player1.append(player1['height'][0])
            arr2_player1.append(player1['birth_date'][0])
            arr4_player1.append(player1['hand'][0])
            arr3_player1.append(player1['nationality'][0])
        except Exception:
            arr1_player1.append(df['p1_height'][i])
            arr2_player1.append(df['p1_birth'][i])
            arr4_player1.append(df['p1_hand'][i])
            arr3_player1.append(df['p1_nation'][i])
            
        try:
            player2 = players[df['player2'][i]:].head(1)
            arr1_player2.append(player2['height'][0])
            arr2_player2.append(player2['birth_date'][0])
            arr4_player2.append(player2['hand'][0])
            arr3_player2.append(player2['nationality'][0])
        except Exception:
            arr1_player2.append(df['p2_height'][i])
            arr2_player2.append(df['p2_birth'][i])
            arr4_player2.append(df['p2_hand'][i])
            arr3_player2.append(df['p2_nation'][i])
            
        ## Progress fill
        if (i % 10 == 0):
            progress.value = i
    
    df['p1_height'] = arr1_player1
    df['p2_height'] = arr1_player2
    df['p1_birth'] = arr2_player1
    df['p2_birth'] = arr2_player2
    df['p1_nation'] = arr3_player1
    df['p2_nation'] = arr3_player2
    df['p1_hand'] = arr4_player1
    df['p2_hand'] = arr4_player2
    if not is_fst_time:
    	print("STATIC STATS IMPORTED\n")

    
def fix_age(df, player_num):
    time = []
    date_fx = []
    months = {"Jan": 1, "Feb": 2, "Mar": 3,
              "Apr": 4, "May": 5, "Jun": 6,
              "Jul": 7, "Aug": 8, "Sep": 9,
              "Oct": 10, "Nov": 11, "Dec": 12
             }
    for date in df["p{0}_birth".format(str(player_num))]:
        if type(date) != float and not pd.isnull(date):
            mas = date.split()
            date_fx.append(datetime.date(int(mas[-1]), months[mas[1]], int(mas[0])))
        else:
            date_fx.append(np.nan)
    df["p{0}_birth".format(str(player_num))] = date_fx

def invert_dataframe(df):    
    stats = ['p1_height', 'p1_birth', 'p1_nation', 'p1_hand', 'p1_points', 'p1_rank']
    for x in df.keys():
        if ('player1' in x or x == 'k1') and x != 'player1_win':
            name2 = x[:-1] + '2'
            tmp = df[x].copy()
            df[x]= df[name2]
            df[name2] = tmp
            
    for x in df.keys():
        if x in stats or 'k1_' in x:
            name2 = x.replace('1', '2', 1)
            tmp = df[x].copy()
            df[x]= df[name2]
            df[name2] = tmp
            
            
    for i in range(len(df)):
        if df['player1_win'][i] == 1:
            df['player1_win'][i] = 0
        elif df['player1_win'][i] == 0:
            df['player1_win'][i] = 1
        else:
            df['player1_win'][i] = -1
        
    

def create_aces_per_game(df):
    df['total_score_match_player1'] = df['score_set1_player1'].fillna(0)
    df['total_score_match_player2'] = df['score_set1_player2'].fillna(0)
    for x in range(2, 6):
        df['total_score_match_player1'] += df['score_set{0}_player1'.format(x)].fillna(0)
        df['total_score_match_player2'] += df['score_set{0}_player2'.format(x)].fillna(0)
    df['aces_per_game_player1'] = df['aces_match_player1'] / df['srv_games_player1']
    df['aces_per_game_player2'] = df['aces_match_player2'] / df['srv_games_player2']
    
def create_double_faults_per_game(df):
    df['df_per_game_player1'] = df['double_faults_match_player1'] / df['srv_games_player1']
    df['df_per_game_player2'] = df['double_faults_match_player2'] / df['srv_games_player2']
    
def create_feature_WSP(df):
    ## overall_winning_serve
    W1SP_p1 = df['first_serve_points_prc_match_common_player1']
    W2SP_p1 = df['second_serve_points_prc_match_common_player1']
    FS_p1 = df['first_serve_prc_match_common_player1']
    W1SP_p2 = df['first_serve_points_prc_match_common_player2']
    W2SP_p2 = df['second_serve_points_prc_match_common_player2']
    FS_p2 = df['first_serve_prc_match_common_player2']
    df['overall_winning_serve_prc_player1'] = W1SP_p1 * FS_p1 + W2SP_p1 * (1 - FS_p1)
    df['overall_winning_serve_prc_player2'] = W1SP_p2 * FS_p2 + W2SP_p2 * (1 - FS_p2)
    
def create_feature_WRP(df):
    df['winning_on_return_prc_player1'] = df['receiver_points_won_match_player1'] / df['points_won_match_player1']
    df['winning_on_return_prc_player2'] = df['receiver_points_won_match_player2'] / df['points_won_match_player2']

def create_feature_COMPLETE(df):
    df['complete_player1'] = df['winning_on_return_prc_common_player1'] * df['overall_winning_serve_prc_player1']
    df['complete_player2'] = df['winning_on_return_prc_common_player2'] * df['overall_winning_serve_prc_player2']
    
def create_feature_SERVEADV(df):
    df['serve_advantage_player1'] = df['overall_winning_serve_prc_player1'] - df['winning_on_return_prc_common_player2']
    df['serve_advantage_player2'] = df['overall_winning_serve_prc_player2'] - df['winning_on_return_prc_common_player1']
    
def create_diff_features(df):
    arr = ['first_serve_prc_match_common_player1', 'first_serve_points_prc_match_common_player1',
      'second_serve_points_prc_match_common_player1', 'winning_on_return_prc_common_player1',
      'aces_per_game_common_player1', 'df_per_game_common_player1', 'break_points_prc_match_common_player1',
          'serve_advantage_player1', 'complete_player1', 'winning_on_return_prc_player1', 'overall_winning_serve_prc_player1']
    for stat in arr:
        df[stat.replace('player1', '') + '_dif'] = df[stat] - df[stat.replace('1', '2')]
    

## FINISHED
def create_retirement_stat(df):
    players = list(set(df['player1']) or set(df['player2']))
    print("CREATING STAT RETIREMENT...")
    arr1 = [0 for x in range(len(df))]
    arr2 = [0 for x in range(len(df))]
    ## Progress bar
    progress = IntProgress(min=0, max=len(players), value=0)
    display(progress)
    for k, player in enumerate(players):
        subset = df[(df['player1'] == player) | (df['player2'] == player)]
        for i in range(1, len(subset)):
            if len(subset) > 1:
                player1 = list(subset['player1'])
                status = list(subset['status'])
                player2 = list(subset['player2'])
                fl = list(subset['player1_win'])
                if (player1[i] == player):    
                    if ((status[i - 1] == 'Retired') and (player1[i - 1] == player) and (fl[i - 1] == 0)):
                        arr1[subset.index[i]] = 1
                    if ((status[i - 1] == 'Retired') and (player2[i - 1] == player) and (fl[i - 1] == 1)):
                        arr1[subset.index[i]] = 1
                else:
                    if ((status[i - 1] == 'Retired') and (player1[i - 1] == player) and (fl[i - 1] == 0)):
                        arr2[subset.index[i]] = 1
                    if ((status[i - 1] == 'Retired') and (player2[i - 1] == player) and (fl[i - 1] == 1)):
                        arr2[subset.index[i]] = 1
                        
        ## Progress fill
        if (k % 10 == 0):
            progress.value = k
    df['1st_match_since_retirement_player1'] = arr1
    df['1st_match_since_retirement_player2'] = arr2
    print("STAT RETIREMENT CREATED\n")
    
## FINISHED (df - DataFrame, stats - array of stats, include only player1 stats)
def create_common_stats(df, stats):
    for stat in stats:
        print("CREATING STAT {0}_common...".format(stat.replace('player1', '')))
        arr1 = [np.nan for x in range(len(df))]
        arr2 = [np.nan for x in range(len(df))]
        stat_p1 = stat
        stat_p2 = stat.replace('1', '2')
        df_dropped = df[(df[stat_p1] == df[stat_p1])] ## df after dropping Nan
        
        progress = IntProgress(min=0, max=len(df_dropped), value=0)
        display(progress)
        
        for i in range(len(df_dropped)):
            df_tmp = df_dropped[df_dropped['date'] <= list(df_dropped['date'])[i]]
            players_p1 = set(df_tmp[df_tmp['player1'] == (list(df_tmp['player1'])[i])]['player2']) | set(df_tmp[df_tmp['player2'] == (list(df_tmp['player1'])[i])]['player1'])
            players_p2 = set(df_tmp[df_tmp['player1'] == (list(df_tmp['player2'])[i])]['player2']) | set(df_tmp[df_tmp['player2'] == (list(df_tmp['player2'])[i])]['player1'])
            common_players = players_p1 & players_p2 ## common opponents
            wrp1 = 0
            wrp1_cnt = 0
            wrp2 = 0
            wrp2_cnt = 0
            for p in common_players:
                wrp1 += df_tmp[(df_tmp['player1'] == list(df_tmp['player1'])[i]) & (df_tmp['player2'] == p)][stat_p1].sum()
                wrp1_cnt += len(df_tmp[(df_tmp['player1'] == list(df_tmp['player1'])[i]) & (df_tmp['player2'] == p)])
                wrp1 += df_tmp[(df_tmp['player2'] == list(df_tmp['player1'])[i]) & (df_tmp['player1'] == p)][stat_p2].sum()
                wrp1_cnt += len(df_tmp[(df_tmp['player2'] == list(df_tmp['player1'])[i]) & (df_tmp['player1'] == p)])

                wrp2 += df_tmp[(df_tmp['player1'] == list(df_tmp['player2'])[i]) & (df_tmp['player2'] == p)][stat_p1].sum()
                wrp2_cnt += len(df_tmp[(df_tmp['player1'] == list(df_tmp['player2'])[i]) & (df_tmp['player2'] == p)])
                wrp2 += df_tmp[(df_tmp['player2'] == list(df_tmp['player2'])[i]) & (df_tmp['player1'] == p)][stat_p2].sum()
                wrp2_cnt += len(df_tmp[(df_tmp['player2'] == list(df_tmp['player2'])[i]) & (df_tmp['player1'] == p)])
            if (wrp1_cnt != 0):
                wrp1 /= wrp1_cnt
                wrp2 /= wrp2_cnt
                arr1[df_tmp['player1'].index[i]] = wrp1
                arr2[df_tmp['player2'].index[i]] = wrp2
            
            ## Progress fill
            if (i % 10 == 0):
                progress.value = i

        print("STAT {0}common CREATED".format(stat.replace('player1', '')))
        df[stat_p1.replace('player1', '') + 'common_player1'] = arr1
        df[stat_p2.replace('player2', '') + 'common_player2'] = arr2
    
def percentile(n):
    '''Calculate n - percentile of data'''
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'pctl%s' % n
    return percentile_

def lagged_features(df
    ,target_var = ['aces_match_player1']
    , lags = [1]
    , windows = [28]
    , aggregation_methods = {'mean', 'median', percentile(10), percentile(90)}
    , surface_type_filter = [1, -1]):
    ## with no surface type filter
    players = ['player1', 'player2']
    df = df.reset_index()
    for p in players:
        if -1 in surface_type_filter:
            for l, w, t in product(lags, windows, target_var):
                t1 = t
                if p == 'player2':
                    t1 = t1.replace("player1", "player2")
                lf_df = df.set_index(['player1', 'player2', 'date'])[t1].\
                         groupby(level=p).apply(lambda x: x.rolling(window=w, min_periods = 1).agg(aggregation_methods).shift(l))
                t1 = t1.replace("player1", "").replace("player2", "")
                new_names = {x: "{0}_lag_{1}_{2}_{3}_{4}".
                              format(p.replace("player", "p"), l, t1, x, w) for x in lf_df.columns}

                df = df.merge(lf_df.reset_index().rename(columns = new_names),
                    how='left', on =['player1', 'player2', 'date'] )
        ## with surface type filter
        if 1 in surface_type_filter:
            for l, w, t in product(lags, windows, target_var):
                t1 = t
                if p == 'player2':
                    t1 = t1.replace("player1", "player2")
                df.head()
                lf_df = df.set_index(['player1', 'player2', 'date', 'Surface'])[t1].\
                         groupby(level=[p, 'Surface']).apply(lambda x: x.rolling(window=w, min_periods = 1).agg(aggregation_methods).shift(l))
                t1 = t1.replace("player1", "").replace("player2", "")
                new_names = {x: "{0}_filter_lag_{1}_{2}_{3}_{4}".
                              format(p.replace("player", "p"), l, t1, x, w) for x in lf_df.columns}

                df = df.merge(lf_df.reset_index().rename(columns = new_names),
                    how='left', on =['player1', 'player2', 'date', 'Surface'])
    return df



 ## How to fill missings in k1/k2? ---- Here as a rule, high coef on player1 and no coef on player2
def drop_n_fill_trash(df):
    for k in df.keys():
        if 'k2' in k:
            for i in range(len(df)):
                if '%' in str(df[k][i]):
                    if float(df[k.replace('k2', 'k1')][i]) < 11:
                        df[k][i] = 1.01
                    else:
                        df[k][i] = np.nan
    
    set_ = set()
    for k in df.keys():
        if 'k2' in k:
            for i in range(len(df)):
                if '-' in str(df[k][i]):
                    set_.add(i)
    return set_

def combine(df, df_):
    progress = IntProgress(min=0, max=len(df_), value=0)
    display(progress)

    for i in range(len(df_)):

        player1 = df_['player1'][i]
        player2 = df_['player2'][i]
        date = np.datetime64(df_['date'][i])
        match = df[(df['player1'] == player1) & (df['player2'] == player2) & ((df['date'] == date) | (df['date'] == date + 1) | (df['date'] == date - 1))]

        if len(match) == 1:
            for k in list(df.keys())[3:]: ## k1_1Xbet, ....
                df_.loc[i, k] = float(match[k])

        match = df[(df['player1'] == player2) & (df['player2'] == player1) & ((df['date'] == date) | (df['date'] == date + 1) | (df['date'] == date - 1))]

        if len(match) == 1:
            for k in list(df.keys())[3:]: ## k1_1Xbet, ....
                if 'k1' in k:
                    df_.loc[i, k.replace('k1', 'k2')] = float(match[k])
                else:
                    df_.loc[i, k.replace('k2', 'k1')] = float(match[k])

        if (i % 10 == 0):
            progress.value = i

            
def fix_letters(df_):
    progress = IntProgress(min=0, max=len(df_), value=0)
    print("FIXING SURNAMES...")
    display(progress)
    bug_surnames = {'Hüsler M.': 'Huesler M.', 'Mcdonald M.': 'McDonald M.',
                    'del Potro J.': 'Del Potro J.', 'López-Pérez E.': 'Lopez-Perez E.',
                   'Di Wu.': 'Wu D.', 'Yen-Hsun Lu.': 'Lu Y.H.', 'Mcgee J.': 'McGee J.',
                   'Zhe Li.': 'Li Z.', 'Wolf J.J.': 'Wolf J.', 'Bautista Agut R.': 'Bautista-Agut R.',
                   'Ramos-Viñolas A.': 'Ramos A.', 'Carreño Busta P.': 'Carreno-Busta P.', 'Struff J.': 'Struff J-L.',
                   'Tsonga J.': 'Tsonga J-W.', 'de Minaur A.': 'De Minaur A.', 'Andújar P.': 'Andujar-Alba P.',
                    'Dutra Silva R.': 'Dutra Da Silva D.', 'Smith J.': 'Smith J. P.', 'Estrella Burgos V.': 'Estrella V.',
                    'Popyrin A.': 'Popyrin Al.', 'Londero J.': 'Londero J. I.', 'Harris L.': 'Harris G.',
                    'de Bakker T.': 'De Bakker T.', 'Kwon S.': 'Kwon Soonwoo', 'Galán D.': 'Galan Riveros D. E.',
                    'Lee D.': 'Lee D. H.', 'Muñoz de la Nava D.': 'Munoz-De La Nava D.', 'Ojeda Lara R.': 'Ojeda L. R.',
                    'Kuznetsov A.': 'Kuznetsov Al.', 'Lindell C.': 'Lindell Ch.', 'Vilella Martínez M.': 'Vilella M. M.',
                    'Kwiatkowski T.': 'Kwiatkowski T. S.', 'Moroni G.': 'Moroni M.',
                    'Huta Galung J.': 'Huta-Galung J.', 'Mukund S.': 'Mukund S. K.', 'Ramirez Hidalgo R.': 'Ramirez-H.R.',
                    'Tyurnev E.': 'Tiurnev E.', 'Yecong He.': 'He Y.', 'Statham R.': 'Statham J. R.',
                   'Rigele Te.': 'Te R.', 'Prashanth N.': 'Prashanth V.', 'Yibing W.': 'Wu Y.',
                    'Varillas J.': 'Varillas J. P.', 'Ficovich J.': 'Ficovich J. P.', 'Lipovšek Puches T.': 'Lipovsek P. T.',
                    'Tatlot J.': 'Tatlot J. S.', 'Sorgi J.': 'Sorgi J. P.', 'Zayed M.': 'Zayed M. S.'}
    letters = {'á': 'a', 'ã': 'a', 'ç': 'c',
           'é': 'e', 'í': 'i', 'ñ': 'n',
           'ó': 'o', 'ö': 'o', 'ú': 'u',
          'ü': 'u', 'ý': 'y', 'ć': 'c',
          'č': 'c', 'ě': 'e', 'ı': 'i',
          'ł': 'l', 'ř': 'r', 'š': 's',
          'ž': 'z'}
    for i in range(len(df_)):
        p1 = df_['player1'][i]
        p2 = df_['player2'][i]
        p2.replace('\n', '') ## лишние \n при парсинге oddsportal
        
        if p1 in bug_surnames:
            p1 = bug_surnames[p1]
            
        if p2 in bug_surnames:
            p2 = bug_surnames[p2]

        for c in range(len(p1)):
            if p1[c].lower() in letters:
                if p1[c].islower():
                    p1 = p1.replace(p1[c], letters[p1[c]])
                else:
                    p1 = p1.replace(p1[c], letters[p1[c].lower()].upper())

        for c in range(len(p2)):
            if p2[c].lower() in letters:
                if p2[c].islower():
                    p2 = p2.replace(p2[c], letters[p2[c]])                    
                else:
                    p2 = p2.replace(p2[c], letters[p2[c].lower()].upper())

        df_['player1'][i] = p1
        df_['player2'][i] = p2
        
        if i % 10 == 0:
            progress.value = i

    print("SURNAMES FIXED\n")


def invert(df):
	print("ADDING INVERT MATCHES...")
	df_copy = df.copy()
	invert_dataframe(df_copy)
	df = df.set_index(["player1", "player2"])
	df_copy = df_copy.set_index(["player1", "player2"])
	df = df.append(df_copy)
	df = df.reset_index()
	df = df.set_index(['date', 'player1', 'player2'])
	df = df.sort_index()
	print("INVERT MATCHES ADDED\n")
	return df




def fix_format(df):
	df['p1_age'] = (df.index.get_level_values('date') - df['p1_birth']).dt.days / 365
	df['p2_age'] = (df.index.get_level_values('date') - df['p2_birth']).dt.days / 365

	df['p1_birthday_today'] = \
	    (df['p1_birth'].dt.month == df.index.get_level_values('date').month) & \
	    (df['p1_birth'].dt.day == df.index.get_level_values('date').day)

	df['p2_birthday_today'] = \
	    (df['p2_birth'].dt.month == df.index.get_level_values('date').month) & \
	    (df['p2_birth'].dt.day == df.index.get_level_values('date').day)

	df['hour'] = df['time'].map(lambda x: x.hour)

	df['Surface'] = df['Surface'].fillna('N/A')

	surface_encoder = OrdinalEncoder()
	df['Surface'] = surface_encoder.fit_transform(df['Surface'].values.reshape(-1,1)); ## Clay - 0.0, Grass - 1.0, Hard outdoor - 3.0, Hard court indoor - 2.0 

	df['round'] = df['round'].fillna('N/A')

	round_encoder = OrdinalEncoder()
	df['round'] = round_encoder.fit_transform(df['round'].values.reshape(-1,1));
	df.rename(columns={"match_duration_mnt": "match_dur"}, inplace=True)
	return df


def build_lag_features(df):
	print("CREATING LAG FEATURES...")
	stats = []
	for x in df.keys():
	    if ('match' in x and 'player1' in x and 'common' not in x and 'score' not in x) or ('bp' in x):
	        stats.append(x)

	stats.pop(stats.index('1st_match_since_retirement_player1'))
	df_new = lagged_features(df, target_var=stats, windows=[7, 28], aggregation_methods=['mean', 'median', percentile(90), percentile(10)])
	
	for i, x in enumerate(df_new['match_dur']):
	    if 'after' in str(x):
	        df_new.drop(i, axis='index', inplace=True)

	df_new = lagged_features(df_new, target_var=['match_dur'], windows=[1, 3, 7], aggregation_methods=['mean', 'median', percentile(90), percentile(10)])
	print("LAG FEATURES CREATED\n")
	return df_new

