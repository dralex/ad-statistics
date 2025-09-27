#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  The statistics of beginner programmers
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

NEW_VERSIONS = ('1.6', '1.7')

PROGRAMS_LIMIT     =   30            # most used programs limit

if __name__ == '__main__':

    if len(sys.argv) < 2:
        Players_data = DEFAULT_PLAYERS_DATA
    else:
        Players_data = sys.argv[1]

    Units = data.load_default_programs(False)
    Units16 = data.load_default_programs(True)
    Unique_programs = {}
    Unique_programs_with_names = {}
    Programs = {}
    Players = data.read_players_sessions(Players_data, None, False)
    Start_players = {}
    Start_programs = {}
    Programs_words = {}
    Programs_stats = {}

    for player, values in Players.items():        
        _, _, sessions = values
        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
        player_programs = {}
        for s in sessions:
            for artefact, unit_data in s['art'].items():
                if artefact in Programs:
                    phash = Programs[artefact]
                    uniq_artefact, uniq_program, _ = Unique_programs[phash]
                    unit, _, _, _, version = unit_data
                    
                    new_found = False
                    for v in NEW_VERSIONS:
                        if version.find(v) == 0:
                            new_found = True
                            break
                    if new_found:
                        the_unit = Units16[unit]
                    else:
                        the_unit = Units[unit]
                    
                    if str(uniq_program) == str(the_unit):
                        # skip programs equal to default
                        continue
                    player_programs[uniq_artefact] = uniq_program
                    if uniq_artefact not in Start_programs:
                        isom_stats = data.check_isomorphic_programs(the_unit, uniq_program, Programs_words)
                        for k, v in isom_stats.items():
                            if k not in Programs_stats:
                                Programs_stats[k] = 0
                            if v:
                                Programs_stats[k] += 1
                        print(isom_stats)
                        Start_programs[uniq_artefact] = [unit, set([]), 0, isom_stats]
                    if player not in Start_programs[uniq_artefact][1]:
                        Start_programs[uniq_artefact][1].add(player)
                    Start_programs[uniq_artefact][2] += 1

        if len(player_programs) > 0:
            Start_players[player] = player_programs

    print()
    print('total players: {}'.format(len(Players)))
    print('players: {}'.format(len(Start_players)))
    n = len(Start_programs)
    print('player programs: {}'.format(n))

    print()
    print('Scripts statistics:')
    for k in sorted(Programs_stats):
        v = Programs_stats[k]
        print("{:40} {:3} {:5.1f}%".format(k, v, 100.0 * v / n))
    
    i = 1
    print()
    print('Top {} start programs (by usage):'.format(PROGRAMS_LIMIT))
    print('                                                   pls  units I No Ed nu o d')
    for art, data in sorted(Start_programs.items(), key=lambda x: (len(x[1][1]), x[1][2]), reverse=True):
        unit, pl, units, isom = data
        print('{:10} {} {:6} {:6} {}  {}  {}  {} {} {}'.format(unit, art, len(pl), units,
                                              'E' if isom['extended default'] else ('I' if isom['isomorphic to default'] else ' '),
                                              'e' if isom['new nodes with default state name'] else ('+' if isom['new nodes'] else ' '),
                                              '+' if isom['new edges'] else ' ',
                                              '+' if isom['diff actions num'] else ' ',
                                              '+' if isom['diff actions order'] else ' ',
                                              '+' if isom['debug actions'] else ' '))
        i += 1
        if i == PROGRAMS_LIMIT:
            break
