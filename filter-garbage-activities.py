#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  The activity filter based on the creation index value
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

def usage():
    print('usage: {} <database1.csv> [database2.csv ...]'.format(sys.argv[0]))
    exit(1)

def filter_players(players_file, stats):
    reader = csv.reader(open(players_file), delimiter=',')
    i = 0
    for row in reader:
        i += 1
        if len(row) != 3: continue
        aid, player, ci = row
        if aid == 'id': continue
        ci = int(ci)
        if player not in stats:
            stats[player] = {}
        if ci not in stats[player]:
            stats[player][ci] = [aid]
        else:
            stats[player][ci].append(aid)

if __name__ == '__main__':

    players_data = []
    for i, arg in enumerate(sys.argv):
        if i == 0: continue
        players_data.append(arg)

    if len(players_data) == 0:
        usage()

    Start_players = {}
    for pfile in players_data:
        filter_players(pfile, Start_players)

    for player,indexes in Start_players.items():
        for i,acts in indexes.items():
            if len(acts) > 1:
                for a in acts[1:]:
                    print(a)
