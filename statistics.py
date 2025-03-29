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

import sys
import os
import csv

import data
import datetime

if len(sys.argv) > 1:
    PLAYERS_DATA = sys.argv[1]
else:
    # default database
    PLAYERS_DATA = 'test.csv'

FILTER_POSSIBLE_MULTIPLAYER = False
FILTER_PLAYERS_INDEX_FILE = None #'player_id_index_list.txt'
FILTER_PLAYERS_FILE = None #'player_id_list.txt'
FILTER_PLAYERS = None # {'player-id-1': (date1, date2), 'player-id-2': None, ...}
BLACKLIST_PLAYERS_FILE = None # 'blacklist.txt'
DAY_THRESHOLD = 350
PLAYERS_LIMIT = None # number if needed

if __name__ == '__main__':

    Players_n = 0
    Players_wo_programs = 0
    Players_less_programs = 0
    
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
    Unique_programs_units = {}
    
    Programs = {}
    Programs_stats = {}
    Programs_words = {}

    if FILTER_PLAYERS_FILE:
        Players_filter = data.load_players_list(FILTER_PLAYERS_FILE)
    else:
        Players_filter = None

    if FILTER_PLAYERS_INDEX_FILE:
        Players_index_filter = data.load_players_index_list(FILTER_PLAYERS_INDEX_FILE)
    else:
        Players_index_filter = None

    if BLACKLIST_PLAYERS_FILE:
        Blacklist_filter = data.load_players_list(BLACKLIST_PLAYERS_FILE)
    else:
        Blacklist_filter = {}
   
    if FILTER_PLAYERS is not None:
        Filter = FILTER_PLAYERS
    elif FILTER_PLAYERS_INDEX_FILE is not None:
        Filter = Players_index_filter
    elif FILTER_PLAYERS_FILE is not None:
        Filter = Players_filter
    else:
        Filter = None
  
    Players = data.read_players_sessions(PLAYERS_DATA, Filter, False)
    
    Dates = {}
    Hist_Sessions = {}
    Hist_Start_Levels = {}
    Hist_Max_Levels = {}
    Hist_Duration = {}
    Hist_Duration_1h = {}
    Hist_Prog_Units = {}
    Hist_Prog_Percent_Units = {}
    Hist_First_Program = {}
    Hist_Places_Duration = {}
    Hist_Edits_Duration = {}
    Hist_Places_Percent_Duration = {}
    Hist_Edits_Percent_Duration = {}
    Hist_Max_Program = {}
    Hist_Uniq_Programs = {}
    Players_selected = set([])
    Super_Max_Level_Wave = None
    Super_Max_Level_Wave_Player = None
    
    for player, values in Players.items():        

        activities, _, sessions = values

        if len(sessions) == 0:
            continue
        
        Player_sessions = 0        
        Start_sessions = 0
        Sessions_start = datetime.datetime.now().timestamp()
        Sessions_finish = 0
        Player_units = 0
        Player_punits = 0
        Player_level = 0
        Player_uniq_programs = set([])

        #print("Load player's {} programs... ".format(player), end='')
        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
        #print('done')
        
        challenge = False
        first_program_level = 5
        first_program_wave = 16
        max_program_level = 0
        max_program_wave = 0

        Session_places = 0.0
        Session_edits = 0.0
        
        for s in sessions:
            Player_sessions += 1
            Player_units += s['units']
            Player_punits += s['punits']
            if s['sd'] < Sessions_start:
                Sessions_start = s['sd']
            if s['fd'] > Sessions_finish:
                Sessions_finish = s['fd']
            level = s['l']
            nlevel = 0
            if level == data.LEVEL_POLYGON:
                pass
            elif level == data.LEVEL_START:            
                Start_sessions += 1
            elif level == data.LEVEL_INFINITY:
                nlevel = Player_level = 4
            else:
                nlevel = int(level)
                if nlevel > Player_level:
                    Player_level = nlevel
            fdate = datetime.datetime.fromtimestamp(s['fd']).strftime('%Y-%m-%d')
            if fdate not in Dates:
                Dates[fdate] = 1
            else:
                Dates[fdate] += 1
                if Dates[fdate] >= DAY_THRESHOLD:
                    challenge = True
            if max_program_level < nlevel:
                max_program_level = nlevel
                max_program_wave = s['w']
            elif max_program_level == nlevel and max_program_wave < s['w']:
                max_program_wave = s['w']
            if 'wp' in s:
                if first_program_level > nlevel:
                    first_program_level = nlevel
                    first_program_wave = s['wp']
                elif first_program_level == nlevel and first_program_wave > s['wp']:
                    first_program_wave = s['wp']
            Session_places += s['places']
            Session_edits += s['edits']
            for artefact, unit_data in s['art'].items():
                if artefact in Programs:
                    phash = Programs[artefact]
                    uniq_artefact, uniq_program, _ = Unique_programs[phash]
                    unit = unit_data[0]
                    if str(uniq_program) == str(Units[unit]):
                        # skip programs equal to default
                        continue
                    Player_uniq_programs.add(uniq_artefact)

        if Player_units == 0 or Player_punits == 0:
            prog_percent = 0
        elif Player_units == Player_punits:
            prog_percent = 101
        else:
            prog_percent = (int(100.0 * float(Player_punits) / float(Player_units)) // 10 + 1) * 10 if Player_units > 0 else 0.0
        duration_min = (Sessions_finish - Sessions_start) / 60.0
        duration = (Sessions_finish - Sessions_start) / 3600.0
        uniq_prog = len(Player_uniq_programs)

        places_mins = int(Session_places / 60.0)
        edits_mins = int(Session_edits / 60.0)
        if duration == 0 or Session_places == 0:
            places_percent = 0
        elif Session_places >= duration_min:
            places_percent = 101
        else:
            places_percent = (int(100.0 * float(Session_places) / float(duration_min)) // 10 + 1) * 10 if duration_min > 0 else 0.0
        if duration == 0 or Session_edits == 0:
            edits_percent = 0
        elif Session_edits >= duration_min:
            edits_percent = 101
        else:
            edits_percent = (int(100.0 * float(Session_edits) / float(duration_min)) // 10 + 1) * 10 if duration_min > 0 else 0.0
        
        if FILTER_POSSIBLE_MULTIPLAYER:
            if (challenge or
                Start_sessions < 1 or Start_sessions > 3 or
                duration > 72 or
                Player_units == 0 or
                uniq_prog > 30 or
                Player_sessions > 50 or
                Player_punits > 1000):
                continue

        if prog_percent not in Hist_Prog_Percent_Units:
            Hist_Prog_Percent_Units[prog_percent] = 1
        else:
            Hist_Prog_Percent_Units[prog_percent] += 1
        if Player_punits not in Hist_Prog_Units:
            Hist_Prog_Units[Player_punits] = 1
        else:
            Hist_Prog_Units[Player_punits] += 1
        if duration < 1:
            minutes = int(duration * 60.0)
            if minutes not in Hist_Duration_1h:
                Hist_Duration_1h[minutes] = 1
            else:
                Hist_Duration_1h[minutes] += 1
        hours = int(duration)
        if hours not in Hist_Duration:
            Hist_Duration[hours] = 1
        else:
            Hist_Duration[hours] += 1
        
        if places_mins not in Hist_Places_Duration:
            Hist_Places_Duration[places_mins] = 1
        else:
            Hist_Places_Duration[places_mins] += 1
        if places_percent not in Hist_Places_Percent_Duration:
            Hist_Places_Percent_Duration[places_percent] = 1
        else:
            Hist_Places_Percent_Duration[places_percent] += 1
        if edits_mins not in Hist_Edits_Duration:
            Hist_Edits_Duration[edits_mins] = 1
        else:
            Hist_Edits_Duration[edits_mins] += 1
        if edits_percent not in Hist_Edits_Percent_Duration:
            Hist_Edits_Percent_Duration[edits_percent] = 1
        else:
            Hist_Edits_Percent_Duration[edits_percent] += 1
    
        if Player_level not in Hist_Max_Levels:
            Hist_Max_Levels[Player_level] = 1
        else:
            Hist_Max_Levels[Player_level] += 1
        if Start_sessions not in Hist_Start_Levels:
            Hist_Start_Levels[Start_sessions] = 1
        else:
            Hist_Start_Levels[Start_sessions] += 1
        if first_program_level < 5 and first_program_wave < 16:
            #if first_program_level == 0 and first_program_wave == 10:
            #    Players_selected.add(player)
            first_program = "{}-{:02}".format(first_program_level, first_program_wave)
            if first_program not in Hist_First_Program:
                Hist_First_Program[first_program] = 1
            else:
                Hist_First_Program[first_program] += 1
        if max_program_level < 5 and max_program_wave < 16:
            max_program = "{}-{:02}".format(max_program_level, max_program_wave)
            if Super_Max_Level_Wave is None or (Super_Max_Level_Wave[0] < max_program_level or
                                                Super_Max_Level_Wave[0] == max_program_level and Super_Max_Level_Wave[1] < max_program_wave): 
                Super_Max_Level_Wave = (max_program_level, max_program_wave)
                Super_Max_Level_Wave_Player = player
            if max_program not in Hist_Max_Program:
                Hist_Max_Program[max_program] = 1
            else:
                Hist_Max_Program[max_program] += 1
        if uniq_prog not in Hist_Uniq_Programs:
            Hist_Uniq_Programs[uniq_prog] = 1
        else:
            Hist_Uniq_Programs[uniq_prog] += 1
        if Player_sessions not in Hist_Sessions:
            Hist_Sessions[Player_sessions] = 1
        else:
            Hist_Sessions[Player_sessions] += 1

            #print(player, ', level: ', Player_level, ', sessions: ', Player_sessions, ', days: ', duration,
            #      ', units: ', Player_punits, "/", Player_units)

        Max_Level = 0
        Avg_Units = 0.0
        Avg_Prog = 0.0
        Avg_Dmg = 0.0
        Uniq_Prog = 0
        Player_Units = 0
        Player_Progs = 0
            
        Players_n += 1
        
        for s in sessions:
            Sessions_n += 1
            Waves_n += s['w']
            
            level = s['l']
            if not level in Levels_n:
                Levels_n[level] = 0
            Levels_n[level] += 1

            if level == data.LEVEL_INFINITY:
                Max_Level = 4
            elif level != data.LEVEL_START and level != data.LEVEL_POLYGON:
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

            for artefact, unit_data in s['art'].items():
                if artefact in Programs:
                    phash = Programs[artefact]
                    uniq_artefact, uniq_program, _ = Unique_programs[phash]
                    unit = unit_data[0]
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
                        if unit_type not in Unique_programs_units:
                            Unique_programs_units[unit_type] = 1
                        else:
                            Unique_programs_units[unit_type] += 1
                        # print('isomorphic check type {} artefact {}...'.format(unit_type, artefact))
                        isom_stats = data.check_isomorphic_programs(Units[unit_type], uniq_program, Programs_words)
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

        if Player_Progs == 0:
            Players_wo_programs += 1
        if Player_Units > 0 and float(Player_Progs) / Player_Units < 0.1:
            Players_less_programs += 1

        if len(sessions) > 0:
            Avg_Units /= len(sessions)
            Avg_Dmg /= len(sessions)
        else:
            Avg_Units = 0.0
            Avg_Dmg = 0.0            
                
        if Player_Units > 0:
            Avg_Prog = 100.0 * float(Player_Progs) / float(Player_Units)
        else:
            Avg_Prog = 0.0
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
    print('Berloga statistics:')
    print('------------------')
    print()
    print('Excluded challenge dates statistics:')
    print('-----------------------------------')
    for d, v in sorted(Dates.items(), key = (lambda x: x[1]), reverse=True):
        if v < DAY_THRESHOLD:
            break
        print(d, v)
    print()
    print('Player sessions distribution:')
    print('------------------------')
    for l, v in sorted(Hist_Sessions.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Start level distribution:')
    print('------------------------')
    for l, v in sorted(Hist_Start_Levels.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Max level distribution:')
    print('----------------------')
    for l, v in sorted(Hist_Max_Levels.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Playing time distribution:')
    print('-------------------------')
    for l, v in sorted(Hist_Duration.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Playing time distribution (< 1h):')
    print('--------------------------------')
    for l, v in sorted(Hist_Duration_1h.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Placement time distribution (minutes):')
    print('-------------------------------------')
    for l, v in sorted(Hist_Places_Duration.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Placement time distribution (%):')
    print('--------------------------------')
    for l, v in sorted(Hist_Places_Percent_Duration.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Programs edit time distribution (minutes):')
    print('------------------------------------------')
    for l, v in sorted(Hist_Edits_Duration.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Programs edit time distribution (%):')
    print('------------------------------------')
    for l, v in sorted(Hist_Edits_Percent_Duration.items(), key = (lambda x: x[0])):
        print(l, v)
    print()

    print('Programmed units percent distribution:')
    print('-------------------------------------')
    for l, v in sorted(Hist_Prog_Percent_Units.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Programmed units distribution:')
    print('------------------------------')
    for l, v in sorted(Hist_Prog_Units.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Programming start distributions:')
    print('-------------------------------')
    for lw, v in sorted(Hist_First_Program.items(), key = (lambda x: x[0])):
        print(lw, v)
    print()
    print('Maximum level distribution:')
    print('---------------------------')
    for lw, v in sorted(Hist_Max_Program.items(), key = (lambda x: x[0])):
        print(lw, v)
    if Super_Max_Level_Wave is not None:
        print('Top level-wave: {}-{:02}, top player: {}'.format(Super_Max_Level_Wave[0],
                                                                Super_Max_Level_Wave[1],
                                                                Super_Max_Level_Wave_Player))
    print()
    print('Programming unique programs distribution:')
    print('----------------------------------------')
    for k, v in sorted(Hist_Uniq_Programs.items(), key=lambda x: x[0]):
        print(k, v)
    print()
    print('Selected players:')
    for p in Players_selected:
        print(p)

    print()
    print('Total statistics:')
    print('-----------------')
    print('Players: {}'.format(Players_n))
    print('Players w/o programs: {}'.format(Players_wo_programs))
    print('Players with <10% programs: {}'.format(Players_less_programs))
    print()
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
    print('Unique programs by unit:')
    for k, v in sorted(Unique_programs_units.items(), key=lambda x: x[1], reverse=True):
        print(k, v)
    print()
    print('Isomorphic programs statistics:')
    for key,value in Units_isomorphic_stats.items():
        print('  {}: {}'.format(key, value))
    print()
    print('Popular new/updated state names:')
    for k, v in sorted(Programs_words.items(), key=lambda x: x[1], reverse=True):
        print('{}: {}'.format(k, v))
#        if v < 40:
#            break
    print()
    print('Most popular programs:')
    i = 0
    for p, v in sorted(Programs_stats.items(), key = lambda x: (len(x[1][1]), x[1][0]), reverse = True):
        i += 1
        if i > 15:
            break
        print("{:3}. {:10} {:3}: units {} players {}".format(i, v[2], p, v[0], len(v[1])))
