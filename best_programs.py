#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  The best programs statistics
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
LIMIT = 15

if __name__ == '__main__':

    if len(sys.argv) < 2:
        Players_data = DEFAULT_PLAYERS_DATA
    else:
        Players_data = sys.argv[1]

    Units = data.load_default_programs()
    Unique_programs = {}
    Unique_programs_with_names = {}
    Programs = {}    
    Players = data.read_players_sessions(Players_data, None, False)
    Best_Programs = {}
    Best_Uniq_Programs = {}
    
    for player, values in Players.items():        
        activities, _, sessions = values
        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
        for s in sessions:
            for artefact, unit_data in s['art'].items():
                if artefact in Programs:
                    phash = Programs[artefact]
                    uniq_artefact, uniq_program, _ = Unique_programs[phash]
                    unit, dmg, enemies = unit_data

                    if uniq_artefact not in Best_Programs:
                        Best_Programs[uniq_artefact] = {}
                    if player not in Best_Programs[uniq_artefact]:
                        Best_Programs[uniq_artefact][player] = [unit, dmg, enemies]
                    else:
                        Best_Programs[uniq_artefact][player][1] += dmg
                        Best_Programs[uniq_artefact][player][2] += enemies

                    if uniq_artefact not in Best_Uniq_Programs:
                        Best_Uniq_Programs[uniq_artefact] = [unit, dmg, enemies]
                    else:
                        Best_Uniq_Programs[uniq_artefact][1] += dmg
                        Best_Uniq_Programs[uniq_artefact][2] += enemies 

    i = 1
    print()
    print('Best {} unique programs (by damage):'.format(LIMIT))
    for art, data in sorted(Best_Uniq_Programs.items(), key=lambda x: x[1][1], reverse=True):
        unit, dmg, enemies = data
        if dmg == 0.0:
            break
        print('{:10} {} {:10.1f} {:6}'.format(unit, art, dmg, enemies))
        i += 1
        if i == LIMIT:
            break
    print()
    print('Best {} unique programs with players\' programs (by damage):'.format(LIMIT))
    for art, art_data in sorted(Best_Uniq_Programs.items(), key=lambda x: x[1][1], reverse=True):
        unit, art_dmg, art_enemies = art_data
        if art_dmg == 0.0:
            break
        players = Best_Programs[art]
        for player, data in sorted(players.items(), key=lambda x: x[1][1], reverse=True):
            _, dmg, enemies = data
            print('{:10} {} {} {:10.1f} {:6}  ({:10.1f} {:6})'.format(unit, art, player, dmg, enemies, art_dmg, art_enemies))
            break
        i += 1
        if i == LIMIT:
            break
