import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import make_scorer
from sklearn.model_selection import cross_validate
import warnings
warnings.filterwarnings('ignore')


def my_accuracy(y_true, y_pred):
    y_pred = np.where(y_pred > 0.5, 1, 0)
    return accuracy_score(y_true, y_pred)

def create_data1(df):
	features_from = '2015-01-01'
	cols2keep = set(['Surface', 'hour', 'round', 'p1_win',
	    'p1_age', 'p2_age', 'p1_height', 'p2_height',
	    'p1_birthday_today', 'p2_birthday_today', 'overall_winning_serve_prc_player1',
	    'overall_winning_serve_prc_player2', 'complete_player1', 'complete_player2',
	    'serve_advantage_player1', 'serve_advantage_player2', '1st_match_since_retirement_player1', 
	    '1st_match_since_retirement_player2'])

	for x in df.keys():
	    if 'lag' in x:
	        cols2keep.add(x)

	for stat in df.keys():
	    if 'common' in stat:
	        cols2keep.add(stat)
	data = df.loc[df.index.get_level_values('date') > features_from, list(cols2keep)] \
	    .dropna(subset=['p1_win'])

	return data

def build_model_classifier(data, startdate):
	startdate = '2019-01-01'
	y = data['p1_win'].astype(int)
	X = data.drop(['p1_win'], axis=1)
	date_idx = X.index.get_level_values('date')

	X_train = X[(date_idx < startdate)]
	y_train = y[(date_idx < startdate)]
	X_test = X[(date_idx >= startdate)]
	y_test = y[(date_idx >= startdate)]

	metric_accuracy = make_scorer(my_accuracy)

	grid_params = {
	    'learning_rate': [0.04], 
	    'max_depth': [4],
	    'subsample': [0.8],
	    'colsample_bytree': [0.8],
	    'n_estimators': [70],
	    'eval_metric': ['logloss']
	}
	cv = TimeSeriesSplit(n_splits=10)
	model = GridSearchCV(xgb.XGBClassifier(n_jobs=3), grid_params, scoring=my_accuracy, cv=cv)
	model.fit(X_train,y_train, verbose=True)
	y_pred = model.predict_proba(X_test)
	return y_pred
		




