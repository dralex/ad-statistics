#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Players with and w/o programs statistics 
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
import csv
import data

BLACKLIST_PLAYERS_FILE = 'blacklist.txt'

NEW_VERSIONS = ('1.6', '1.7')
STANDARD_PATH      = 'standard_programs'
STANDARD_PATH_NEW  = os.path.join('standard_programs', '1.6')
STANDARD_UNITS     = ('Autoborder', 'Stapler')

def usage():
    print('usage: {} <database1.csv> [<database2.csv> ...]'.format(sys.argv[0]))
    exit(1)

def check_program(art, unit, progs, su):
    
    
def calc_statistics(players, stats, su, su16):
    Programs = {}
    Unique_programs = {}
    Unique_programs_with_names = {}
    for player, values in players.items():
        activities, _, _ = values
        stats['players'].add(player)
        for a in activities.values():
            if player in stats['players played'] and player in stats['players progs']:
                break
            if a['t'] == 'u':
                if 'w' in a and a['w'] > 1:
                    stats['players played'].add(player)                
                if 'ac' in a and 'u' in a:
                    art = a['ac'][0]
                    unit = a['u']
                    new_found = False
                    for v in NEW_VERSIONS:
                        if a['v'].find(v) == 0:
                            new_found = True
                            break
                    data.load_player_programs(player, progs, Unique_programs, Unique_programs_with_names)
                    
                    if check_program(art, unit, progs, su if not_found else su16):
                        stats['players progs'].add(player)

if __name__ == '__main__':

    players_data = []
    for i, arg in enumerate(sys.argv):
        if i == 0: continue
        players_data.append(arg)

    if len(players_data) == 0:
        usage()
    
    _blacklist_filter = None
    if BLACKLIST_PLAYERS_FILE is not None:
        _blacklist_filter = data.load_players_list(BLACKLIST_PLAYERS_FILE)

    Standard_units = {}
    Standard_units16 = {}
    for u in STANDARD_UNITS:
        Standard_units[u] = data.load_program_path(STANDARD_PATH, u)
        Standard_units16[u] = data.load_program_path(STANDARD_PATH_NEW, u)

    progs = {}
    stats = {'players': set([]),
             'players played': set([]),
             'players progs': set([])}
    for p in players_data:
        players = data.read_players_data(p, None, _blacklist_filter)
        calc_statistics(players, stats, progs, Standard_units, Standard_units16)
    print()
    print('Players statistics:')
    print('Total players: {}'.format(len(stats['players'])))
    print('Players played: {}'.format(len(stats['players played'])))
    print('Players programmed: {}'.format(len(stats['players progs'])))
    
