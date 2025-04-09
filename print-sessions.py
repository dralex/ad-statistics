#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Player sessions printer
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

DEFAULT_PLAYERS_DATA = 'test.csv'

def usage(msg = ''):
    print("Usage: {} [database-path] <player-id> [<start-index> <finish-index>]".format(sys.argv[0]))
    if msg:
        print(msg)
    exit(1)            

if __name__ == '__main__':

    if len(sys.argv) < 2 or len(sys.argv) > 5:
        usage()
        
    start_index = finish_index = None
    if len(sys.argv) == 2:
        Players_data = DEFAULT_PLAYERS_DATA
        Player = sys.argv[1]        
    elif len(sys.argv) == 3:
        Players_data = sys.argv[1]
        Player = sys.argv[2]
    else:
        Players_data = sys.argv[1]
        Player = sys.argv[2]
        start_index = int(sys.argv[3])
        finish_index = int(sys.argv[4])

    if start_index is None:
        data.read_players_sessions(Players_data, {Player.lower(): None}, True)
    else:
        data.read_players_sessions(Players_data, {Player.lower(): [(start_index, finish_index)]}, True)
