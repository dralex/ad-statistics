#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Database splitter
# 
#  Copyright (C) 2025-2026 Alexey Fedoseev <aleksey@fedoseev.net>
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

import data

def usage(msg = ''):
    print("Usage: {} <database-path> [<more-database-paths> ...] <player-id-list>".format(sys.argv[0]))
    if msg:
        print(msg)
    exit(1)            

if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage()

    datafiles = []
    for i, a in enumerate(sys.argv):
        if i == 0 or i == len(sys.argv) - 1:
            continue
        datafiles.append(a)
    playersfile = sys.argv[-1]

    PLAYERS = data.load_players_index_list(playersfile)
    Players_found = set([])

    for datafile in datafiles:
        with open(datafile) as f:
            for line in f.readlines():
                parts = line.split(',')
                player = parts[data._CSV_PLAYER]
                if player in PLAYERS:
                    Players_found.add(player)
                    print(line, end='')

    # players not found
    for p in PLAYERS:
        if p not in Players_found:
            print(p, file=sys.stderr)
