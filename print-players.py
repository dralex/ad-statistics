#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Players' list statistics 
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
import datetime
import csv

import data

def usage():
    print('usage: {} <database.csv> <players-indexes-filter.txt> <output.csv>'.format(sys.argv[0]))
    exit(1)

def save_csv(fname, data):
    with open(fname, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)

if __name__ == '__main__':

    if len(sys.argv) != 4:
        usage()
    
    Programs = {}
    Unique_programs = {}
    Unique_programs_with_names = {}
    Units = data.load_default_programs()
    Filter = data.load_players_index_list(sys.argv[2])
    Players = data.read_players_sessions(sys.argv[1], Filter, False)
    output_file = sys.argv[3]
    
    Data = []
    
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

        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)

        Waves_n = 0
        Max_Level = 0
        Avg_Units = 0.0
        Avg_Prog = 0.0
        Avg_Dmg = 0.0
        Uniq_Prog = 0
        Player_Units = 0
        Player_Progs = 0
        Traditions = set([])
        Unit_types = set([])
        Programs_with_non_trivial_names = 0
        Programs_with_debugging = 0
    
        for s in sessions:
            Waves_n += s['w']
            
            level = s['l']

            if level == data.LEVEL_INFINITY:
                Max_Level = 4
            elif level != data.LEVEL_START and level != data.LEVEL_POLYGON:
                Max_Level = int(level)
            
            tradition = s['t']
            if tradition is not None:
                Traditions.add(tradition)

            for unit_type in s['u']:
                Unit_types.add(unit_type)

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
                    if uniq_artefact == artefact:
                        Uniq_Prog += 1
                        # print('isomorphic check type {} artefact {}...'.format(unit_type, artefact))
                        isom_stats = data.check_isomorphic_programs(Units[unit_type], uniq_program)                        
                        # print('done')
                        for key,value in isom_stats.items():
#                            if key not in Units_isomorphic_stats:
#                                Units_isomorphic_stats[key] = 0
#                            if value:
#                                Units_isomorphic_stats[key] += 1
                            if key == 'non-trivial names' and value:
                                Programs_with_non_trivial_names += 1
                            if key == 'debug actions' and value:
                                Programs_with_debugging += 1
                else:
                    Units_with_broken_artefacts_n += 1

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

        Traditions_str = ''
        for t in Traditions:
            Traditions_str += t[0]
        Unit_types_str = ''
        for ut in Unit_types:
            Unit_types_str += ut[0:2]

        player_data = [
            len(sessions),
            Waves_n,
            Max_Level,
            Traditions_str,
            Unit_types_str,
            Player_Units,
            Player_Progs,
            Uniq_Prog,
            Avg_Units,
            Avg_Prog,
            Avg_Dmg,
            Uniq_Prog,
            Programs_with_non_trivial_names,
            Programs_with_debugging
        ]

        Data.append(player_data)

    save_csv(output_file, Data)


