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

def usage(msg = ''):
    print("Usage: {} <artefact-id>".format(sys.argv[0]))
    if msg:
        print(msg)
    exit(1)            

if __name__ == '__main__':

    if len(sys.argv) != 2:
        usage()
    
    Artefact = sys.argv[1]
    Units = data.load_default_programs()
    Unique_programs = {}
    Unique_programs_with_names = {}
    Programs = {}    
    Players = data.read_players_data(PLAYERS_DATA, None, False)
    Found = set([])
    
    for player, values in Players.items():        
        activities, _, sessions = values
        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
        for s in sessions:
            for artefact, unit in s['art'].items():
                if artefact in Programs:
                    phash = Programs[artefact]
                    uniq_artefact, uniq_program, _ = Unique_programs[phash]
                    if str(uniq_program) == str(Units[unit]):
                        # skip programs equal to default
                        continue
                    if uniq_artefact == Artefact: 
                        Found.add(player)

    for p in Found:
        print(p)
