#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Players summary statistics 
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

def usage():
    print('usage: {} <database1.csv> [<database2.csv> ...]'.format(sys.argv[0]))
    exit(1)

def calc_statistics(players, stats, _blacklist_filter):
    for player, values in players.items():

        if _blacklist_filter is not None and player in _blacklist_filter:
            continue

        activities, _, _ = values
        if player not in stats:
            stats[player] = 0
        stats[player] += len(activities)

def print_statistics(stats, top):

    print()
    i = 0
    for pl, num in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print('{}: {}'.format(pl, num))
        i += 1
        if i == top:
            break

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

    stats = {}
    for p in players_data:
        players = data.read_players_data(p)
        calc_statistics(players, stats, _blacklist_filter)
    print_statistics(stats, 100)

