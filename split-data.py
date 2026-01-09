#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Database splitter
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

import data

def usage(msg = ''):
    print("Usage: {} <database-path> <player-id-list>".format(sys.argv[0]))
    if msg:
        print(msg)
    exit(1)            

if __name__ == '__main__':

    if len(sys.argv) != 3:
        usage()

    datafile = sys.argv[1]
    playersfile = sys.argv[2]

    PLAYERS = data.load_players_index_list(playersfile)
    Players_found = set([])

    with open(datafile) as f:
        for line in f.read().splitlines():
            parts = line.split(',')
            player = parts[data._CSV_PLAYER]
            if player in PLAYERS:
                Players_found.add(player)
                print(line)

    # players not found
    for p in PLAYERS:
        if p not in Players_found:
            print(p, file=sys.stderr)
