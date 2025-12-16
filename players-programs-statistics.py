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

STANDARD_UNITS     = ('Autoborder', 'Stapler')

def usage():
    print('usage: {} <database1.csv> [<database2.csv> ...]'.format(sys.argv[0]))
    exit(1)
    
def calc_statistics(players, stats):
    for player, values in players.items():
        activities, _, _ = values
        stats['players'].add(player)
        for a in activities.values():
            if a['t'] == 'u':
                if 'w' in a and a['w'] > 1:
                    stats['players played'].add(player)                
                if 'ac' in a:
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

    stats = {'players': set([]),
             'players played': set([]),
             'players progs': set([])}
    for p in players_data:
        players = data.read_players_data(p, None, _blacklist_filter)
        calc_statistics(players, stats)
    print()
    print('Players statistics:')
    print('Total players: {}'.format(len(stats['players'])))
    print('Players played: {}'.format(len(stats['players played'])))
    print('Players programmed: {}'.format(len(stats['players progs'])))
    
