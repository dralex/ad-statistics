#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Programs archive collector
# 
#  Copyright (C) 2025 Alexey Fedoseev <aleksey@fedoseev.net>
# 
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program. If not, see https://www.gnu.org/licenses/
#  ----------------------------------------------------------------------------- 

import os
import csv

import data
import datetime

FILTER_PLAYERS_FILE = None # 'file name'
FILTER_PLAYERS = None # ['player-id-1', 'player-id-2', ...]
PLAYERS_DATA = 'test.csv' 
PLAYERS_LIMIT = None # number if needed

if __name__ == '__main__':

    Players_n = 0
    Sessions_n = 0
    Levels_n = {}
    Traditions_n = {}
    Unit_types_n = {}
    Waves_n = 0

    Units_n = 0
    Units_programs_n = 0
    Units_with_broken_artefacts_n = 0
    Units_isomorphic_stats = {} 
    
    Units = data.load_default_programs()
    Unique_programs = {}
    Unique_programs_n = 0
    Unique_programs_with_names = {}
    Programs = {}
    Programs_stats = {}

    if FILTER_PLAYERS_FILE:
        with open(FILTER_PLAYERS_FILE) as f:
            Players_filter = set(f.read().splitlines())
    else:
        Players_filter = None

    if FILTER_PLAYERS is not None:
        Filter = FILTER_PLAYERS
    elif FILTER_PLAYERS_FILE is not None:
        Filter = Players_filter
    else:
        Filter = None
        
    Players = data.read_players_data(PLAYERS_DATA, Filter)

    print()
    print('Players statistics:')
    print('------------------')
    for player, values in Players.items():        
        if FILTER_PLAYERS is not None and player not in FILTER_PLAYERS:
            continue
        if FILTER_PLAYERS_FILE is not None and player not in Players_filter:
            continue

        Players_n += 1
        activities, _, sessions = values
        
        #print("Load player's {} programs... ".format(player), end='')
        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
        #print('done')        

        Max_Level = 0
        Avg_Units = 0.0
        Avg_Prog = 0.0
        Avg_Dmg = 0.0
        Uniq_Prog = 0
        Player_Units = 0
        Player_Progs = 0

        for s in sessions:
            Sessions_n += 1
            Waves_n += s['w']
            
            level = s['l']
            if not level in Levels_n:
                Levels_n[level] = 0
            Levels_n[level] += 1

            if level == data.LEVEL_INFINITY:
                Max_Level = 4
            elif level != data.LEVEL_START:
                Max_Level = int(level)
            
            tradition = s['t']
            if tradition is None:
                tradition = 'Unknown'
            if not tradition in Traditions_n:
                Traditions_n[tradition] = 0
            Traditions_n[tradition] += 1

            for unit_type in s['u']:
                if unit_type not in Unit_types_n:
                    Unit_types_n[unit_type] = 0
                Unit_types_n[unit_type] += 1

            Avg_Units += s['avg_u']
            Avg_Prog += s['avg_p']
            Avg_Dmg += s['avg_d']

            Player_Units += s['units']

            for artefact, unit in s['art'].items():
                if artefact in Programs:
                    phash = Programs[artefact]
                    uniq_artefact, uniq_program, _ = Unique_programs[phash]
                    if str(uniq_program) == str(Units[unit]):
                        # skip programs equal to default
                        continue
                    Player_Progs += 1
                    if uniq_artefact not in Programs_stats:
                        Programs_stats[uniq_artefact] = [1, set([player]), unit]
                    else:
                        Programs_stats[uniq_artefact][0] += 1
                        Programs_stats[uniq_artefact][1].add(player)
                    if uniq_artefact == artefact:
                        Uniq_Prog += 1
                        # print('isomorphic check type {} artefact {}...'.format(unit_type, artefact))
                        isom_stats = data.check_isomorphic_programs(Units[unit_type], uniq_program)
                        # print('done')
                        for key,value in isom_stats.items():
                            if key not in Units_isomorphic_stats:
                                Units_isomorphic_stats[key] = 0
                            if value:
                                Units_isomorphic_stats[key] += 1
                else:
                    Units_with_broken_artefacts_n += 1

        Units_n += Player_Units
        Units_programs_n += Player_Progs
        Unique_programs_n += Uniq_Prog

        Avg_Units /= len(sessions)
        if Player_Units > 0:
            Avg_Prog = 100.0 * float(Player_Progs) / float(Player_Units)
        else:
            Avg_Prog = 0.0
        Avg_Dmg /= len(sessions)
        #print("Player {} - sessions {}, max level {}, avg units: {:5.2f}, avg prog: {:5.2f}%, avg dmg: {:6.1f}, uniq progs: {}".format(player,
        #                                                                                                                               len(sessions),
        #                                                                                                                               Max_Level,
        #                                                                                                                               Avg_Units,
        #                                                                                                                               Avg_Prog,
        #                                                                                                                               Avg_Dmg,
        #                                                                                                                               Uniq_Prog))
        if PLAYERS_LIMIT is not None and Players_n == PLAYERS_LIMIT:
            break

    print()
    print('Total statistics:')
    print('-----------------')
    print('Players: {}'.format(Players_n))
    print('Sessions: {}'.format(Sessions_n))
    print('Levels by sessions:')
    for l in data.LEVELS:
        if l in Levels_n:
            print('{:8}: {}'.format(l, Levels_n[l]))
        else:
            print('{:8}: {}'.format(l, 0))
    print()
    print('Traditions by sessions:')
    for t in sorted(Traditions_n.keys()):
        print('{:11}: {}'.format(t, Traditions_n[t]))
    print()
    print('Unit types by sessions:')
    for u in sorted(Unit_types_n.keys()):
        print('{:10}: {}'.format(u, Unit_types_n[u]))
    print()    
    print('Waves: {}'.format(Waves_n))
    print('Units used: {}'.format(Units_n))
    print('Units used with new programs: {}'.format(Units_programs_n))
    print('Broken unit programs: {}'.format(Units_with_broken_artefacts_n))
    print('Unique unit diagrams: {}'.format(Unique_programs_n))
    print()
    print('Isomorphic programs statistics:')
    for key,value in Units_isomorphic_stats.items():
        print('  {}: {}'.format(key, value))
    print()
    print('Most popular programs:')
    i = 0
    for p, v in sorted(Programs_stats.items(), key = lambda x: (len(x[1][1]), x[1][0]), reverse = True):
        i += 1
        if i > 15:
            break
        print("{:3}. {:10} {:3}: units {} players {}".format(i, v[2], p, v[0], len(v[1])))
