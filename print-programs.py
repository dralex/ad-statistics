#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Print player's programs
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

def usage(msg = ''):
    print("Usage: {} <database-path> <player-id|player-id-with-comma-separated-indexes> [index-from index-to]".format(sys.argv[0]))
    if msg:
        print(msg)
    exit(1)            

if __name__ == '__main__':

    if len(sys.argv) != 3 and len(sys.argv) != 5:
        usage()

    Players_data = sys.argv[1]
    Player_id = sys.argv[2].lower()
    
    if Player_id.find(',') > 0:
        Player_id, index_from, index_to = Player_id.split(',')
        indexes = (int(index_from), int(index_to))
    elif len(sys.argv) == 5:
        indexes = (int(sys.argv[3]), int(sys.argv[4]))
    else:
        indexes = None

    Units = data.load_default_programs()
    Unique_programs = {}
    Unique_programs_with_names = {}
    Programs = {}    
    Players = data.read_players_sessions(Players_data, {Player_id: (indexes,)}, False)

    Player_defaults = {}
    Player_programs = {}
    
    for player, values in Players.items():        
        activities, _, sessions = values
        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
        for s in sessions:
            for artefact, unit in s['art'].items():
                unit_type, unit_dmg, unit_enemies = unit
                
                if artefact in Programs:
                    phash = Programs[artefact]
                    uniq_artefact, uniq_program, _ = Unique_programs[phash]
                    if str(uniq_program) == str(Units[unit_type]):
                        # programs equal to default
                        if unit_type not in Player_defaults:
                            Player_defaults[unit_type] = [1, unit_dmg, unit_enemies]
                        else:
                            Player_defaults[unit_type][0] += 1
                            Player_defaults[unit_type][1] += unit_dmg
                            Player_defaults[unit_type][2] += unit_enemies
                    else:
                        if uniq_artefact not in Player_programs:
                            Player_programs[uniq_artefact] = [1, unit_dmg, unit_enemies, unit_type, uniq_program]
                        else:
                            Player_programs[uniq_artefact][0] += 1
                            Player_programs[uniq_artefact][1] += unit_dmg
                            Player_programs[uniq_artefact][2] += unit_enemies

    print('Default programs ({}):'.format(len(Player_defaults)))
    for unit_type in sorted(Player_defaults.keys()):
        unit_count, unit_dmg, unit_enemies = Player_defaults[unit_type]
        print('{}: {:5} {:5.2f} {:5}'.format(unit_type, unit_count, unit_dmg, unit_enemies))

    print()
    print()
    print('Unique programs ({}):'.format(len(Player_programs)))
    for artefact in sorted(Player_programs.keys()):
        unit_count, unit_dmg, unit_enemies, unit_type, program = Player_programs[artefact]
        print('-----------------------------------------------------------------------------------------------------')
        print('{}: {:5} {:5.2f} {:5}'.format(unit_type, unit_count, unit_dmg, unit_enemies))
        print(str(program))
        print()
        print('Diff with the default {}:'.format(unit_type))
        data.inspect_program(unit_type, Units, program)
        print()

