#!/usr/bin/python3

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

def calc_statistics(players, stats):
    for player, values in players.items():
        _, datetable, _ = values
        date, _, _, a = datetable[-1]
        day = a['ddate']
        if player not in stats:
            stats[player] = (date, day)
        elif stats[player][0] > date:
            stats[player] = (date, day)

def calc_histogram(stats):
    hist = {}
    for player, dates in stats.items():
        day = dates[1]
        if day not in hist:
            hist[day] = 1
        else:
            hist[day] += 1
    return hist

def print_histogram(hist, year):

    print()
    total = 0
    for day, num in sorted(hist.items(), key=lambda x: x[0]):
        if day.find(year) != 0:
            continue
        print('{}: {}'.format(day, num))
        total += num
    print('Total: {}'.format(total))

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
        players = data.read_players_data(p, None, _blacklist_filter)
        calc_statistics(players, stats)

    hist = calc_histogram(stats)
        
    print_histogram(hist, '2025')

