
from time import sleep
import pandas as pd
import numpy as np
import copy
import ast
import csv
import datetime
import random
import time

need_to_convert = ["First serve", "Second serve", "Break points",
                   "First serve points", "Second serve points"]


## Считает prc и cnt
def create_features(feature, matches, match, set_num):
    stat1 = [0, 0]
    stat2 = [0, 0]
    stat_list = [stat1, stat2]
    player1 = matches[match]["sets_stat"][set_num][feature][0].split(" ")[0].split("/")
    player2 = matches[match]["sets_stat"][set_num][feature][1].split(" ")[0].split("/")
    if int(player1[1]) != 0:
        stat1[0] = int(player1[0]) / int(player1[1])
    if int(player2[1]) != 0:
        stat1[1] = int(player2[0]) / int(player2[1])
    stat_list[1] = [player1[0], player2[0]]
    return stat_list

## Меняет название признка
def convert_stat(set_num, set_name, temp_list_matches, x, matches_copy, match):
    stat_list = create_features(x, matches_copy, match, set_num)
    name_prc = (x + "_prc_" + set_name).lower().replace(" ", "_")
    name_cnt = (x + "_cnt_" + set_name).lower().replace(" ", "_")
    temp_list_matches[match][name_prc] = stat_list[0]
    temp_list_matches[match][name_cnt] = stat_list[1]
    
## Переносит все матчи в новой записи в другой массив
def unpack_and_change(matches):
    temp_list_matches = []
    for match in range(len(matches)):
        temp_list_matches.append({})
        if matches[match]["status"] != "Walkover":
            for stat in matches[match]:
                if stat == "sets_stat" and matches[match][stat] != None:
                    for set_num in matches[match][stat]:
                        for x in matches[match][stat][set_num]:
                            names = {"ALL": "match", "1ST": "set1", "2ND": "set2", "3RD": "set3", "4TH": "set4", "5TH": "set5"}
                            if x in need_to_convert: ## Проверка на то, что статистика нуждается в конвертации
                                    convert_stat(set_num, names[set_num], temp_list_matches, x, matches, match)
                            else:
                                ## Запись статистик с новым именем, которые не нуждаются в конвертации
                                name = ((x + "_" + names[set_num]).replace(" ", "_")).lower()
                                temp_list_matches[match][name] = matches[match][stat][set_num][x] 
                elif stat == "match_info":
                    for x in matches[match][stat]:
                        temp_list_matches[match][x] = matches[match][stat][x]
                elif stat == "match_duration":
                    if matches[match][stat] != None:
                        if matches[match][stat] != "Walkover":
                            hrs = int(matches[match][stat].split(" ")[-2][:-1])
                            mnt = int(matches[match][stat].split(" ")[-1][:-1])
                            temp_list_matches[match][stat + "_mnt"] = str(hrs * 60 + mnt)
                        else:
                            temp_list_matches[match][stat + "_mnt"] = None
                else:
                    temp_list_matches[match][stat] = matches[match][stat] ## Запись остальных статистик   
        
        ## Если матч был Walkover, переносим статистики
        else:
            for stat in matches[match]:
                if stat != "sets_stat":
                    if stat == "match_info":
                        for el in matches[match][stat]:
                            temp_list_matches[match][el] = matches[match][stat][el]
                    elif stat == "match_duration":
                        temp_list_matches[match][stat + "_mnt"] = matches[match][stat]
                    else:
                        temp_list_matches[match][stat] = matches[match][stat]
            
    return temp_list_matches


def to_csv(matches, filename):
    columns = list()
    for match in matches:
        for stat in match:
            if stat not in columns:
                columns.append(stat)
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for i in range(len(matches)):
            writer.writerow(matches[i])

def csv_to_list(file):
    matches = []
    with open(file, 'r') as f:
        reader = csv.DictReader(f, delimiter=',')
        for line in reader:
            matches.append(line)
    return matches

def delete_trash(matches):
    arr = []
    for match in matches:
        if match['score_sets'] != "":
            tmp = ast.literal_eval(match['score_sets'])
            for set_ in tmp:
                if "255" in set_:
                    arr.append(matches.index(match))

        if '/' in match['player1']:
            arr.append(matches.index(match))
    arr.sort(reverse=True)
    for x in arr:
        del matches[x]
                    

def split_sets_and_dur(matches):
    for i in range(len(matches)):
        if matches[i]['score_sets'] != "":
            matches[i]['score_sets'] = ast.literal_eval(matches[i]['score_sets'])
            for j in range(len(matches[i]['score_sets'])):
                matches[i]['score_set' + str(j + 1)] = list(matches[i]['score_sets'][j])
            matches[i].pop('score_sets')
            for t in range(j + 1, 5):
                matches[i]['score_set' + str(t + 1)] = None
        else:
            for t in range(5):
                matches[i]['score_set' + str(t + 1)] = None
        
        if matches[i]['sets_duration'] != "":
            matches[i]['sets_duration'] = ast.literal_eval(matches[i]['sets_duration'])
            for j in range(len(matches[i]['sets_duration'])):
                matches[i]['duration_set' + str(j + 1)] = matches[i]['sets_duration'][j]
            matches[i].pop('sets_duration')
            for t in range(j + 1, 5):
                matches[i]['duration_set' + str(t + 1)] = None
        else:
            for t in range(0, 5):
                matches[i]['duration_set' + str(t + 1)] = None
            matches[i].pop('sets_duration')
                

                
def fix_set_score(matches):
    stats = ['score_set' + str(x + 1) for x in range(5)]
    for i in range(len(matches)):
        for j in range(len(stats)):
            if matches[i][stats[j]] != None:
                if len(matches[i][stats[j]][0]) > 1:
                    if ((matches[i][stats[j]][0][0] == "6" and matches[i][stats[j]][1][0] == "7") or (matches[i][stats[j]][0][0] == "7" and matches[i][stats[j]][1][0] == "6")):
                        matches[i]['tie_break_set' + str(j + 1)] = str([matches[i][stats[j]][0][1:], matches[i][stats[j]][1][1:]])
                        matches[i][stats[j]] = str([matches[i][stats[j]][0][0], matches[i][stats[j]][1][0]])
                    else:
                        matches[i]['tie_break_set' + str(j + 1)] = None
                        matches[i][stats[j]] = str(matches[i][stats[j]])
                elif len(matches[i][stats[j]][0]) == 1:
                    matches[i][stats[j]] = str(matches[i][stats[j]])
                    matches[i]['tie_break_set' + str(j + 1)] = None
            else:
                 matches[i]['tie_break_set' + str(j + 1)] = None   
                    
def split_stats(matches):
    stats = list(matches[0].keys())
    unused_stats = ['match_url','player1','player2',
              'status','Surface','date',
              'sets_duration','score_pbp','serving_idxs',
              'k1','k2','player1_win','round',
              'match_duration_mnt','Location','sets_stat', 'score_sets',
                   'duration_set1', 'duration_set2', 'duration_set3',
                   'duration_set4', 'duration_set5']
    for stat in unused_stats:
        if stat in stats:
            stats.remove(stat)

    for i in range(len(matches)):
        for stat in stats:
            x = matches[i][stat]
            if x != None:
                if x != "":
                    x = ast.literal_eval(x)
                    if len(x) == 2:
                        matches[i][stat + "_player1"] = float(x[0])
                        matches[i][stat + "_player2"] = float(x[1])
                    else:
                        matches[i][stat + "_player1"] = None
                        matches[i][stat + "_player2"] = None
                else:
                    matches[i][stat + "_player1"] = None
                    matches[i][stat + "_player2"] = None
            else:
                matches[i][stat + "_player1"] = None
                matches[i][stat + "_player2"] = None
            del matches[i][stat]
            
def create_srv_games(matches):
    for i in range(len(matches)):
        cnt_p1 = 0
        cnt_p2 = 0
        if matches[i]['serving_idxs'] != '':
            idxs = ast.literal_eval(matches[i]['serving_idxs'])
            for x in idxs.values():
                cnt_p1 += x.count(1)
                cnt_p2 += x.count(0)
            matches[i]['srv_games_player1'] = cnt_p1
            matches[i]['srv_games_player2'] = cnt_p2
        else:
            matches[i]['srv_games_player1'] = None
            matches[i]['srv_games_player2'] = None

## create break_point_stat
def create_bp_stat(matches):
    for i in range(len(matches)):
        bp_back_cnt_player1 = 0
        bp_back_cnt_player2 = 0
        if matches[i]['score_pbp'] != '':
            match = ast.literal_eval(matches[i]['score_pbp'][28:-1])
            idxs = ast.literal_eval(matches[i]['serving_idxs'])
            for set_ in match.keys():
                for j in range(len(match[set_])):
                    for t in range(len(match[set_][j])):
                        if idxs[set_][j] == 0:
                            if ((match[set_][j][t][0] == '30' or (match[set_][j][t][0] == '15') or (match[set_][j][t][0] == '0')) and match[set_][j][t][1] == '40' and t != len(match[set_][j]) - 1) or (match[set_][j][t][0] == '40' and match[set_][j][t][1] == 'A' and t != len(match[set_][j]) - 1): ## Подает player1
                                bp_back_cnt_player1 += 1
                        if idxs[set_][j] == 1 and ((match[set_][j][t][0] == '40' and (match[set_][j][t][1] == '30' or (match[set_][j][t][1] == '15') or (match[set_][j][t][1] == '0')) and t != len(match[set_][j]) - 1) or (match[set_][j][t][0] == 'A' and match[set_][j][t][1] == '40' and t != len(match[set_][j]) - 1)): ## Подает player2
                            bp_back_cnt_player2 += 1
            matches[i]['bp_saved_cnt_player1'] = bp_back_cnt_player1 
            matches[i]['bp_saved_cnt_player2'] = bp_back_cnt_player2
        del matches[i]['score_pbp']
        del matches[i]['serving_idxs']
        if "score_sets" in matches[i]:
            del matches[i]['score_sets']
        
def make_csv(matches, filename):
    columns = list()
    for match in matches:
        for stat in match:
            if stat not in columns:
                columns.append(stat)
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for i in range(len(matches)):
            writer.writerow(matches[i])

