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

MIN_PLAYING_DURATION = 1             # one hour
MAX_PLAYING_DURATION = 24 * 7        # one week
MIN_PLAYING_SESSIONS = 1             # at least one session
MAX_PLAYING_SESSIONS = 5             # several sessions
MAX_LEVEL =            1             # maximum level
MIN_PROGRAMM_UNITS =   1             # at least one program
MAX_PROGRAMM_UNITS =   20            # no more than 20 programmed units
VERSIONS           =   '1.5'

PROGRAMS_LIMIT     =   20            # most used programs limit

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
    Start_players = {}
    Start_programs = {}
    Programs_words = {}
    Programs_stats = {}

    for player, values in Players.items():        
        activities, _, sessions = values
        if not (MIN_PLAYING_SESSIONS <= len(sessions) <= MAX_PLAYING_SESSIONS):
            continue
        max_level = 0
        programmed_units = 0
        start_time = datetime.datetime.now().timestamp()
        finish_time = 0
        wrong_versions = False
        for s in sessions:
            programmed_units += s['punits']
            level = s['l']
            index = data.LEVELS.index(level)
            if max_level < index < 4:
                max_level = index
            if s['sd'] < start_time:
                start_time = s['sd']
            if s['fd'] > finish_time:
                finish_time = s['sd']
            for v in s['v']:
                if v.find(VERSIONS) != 0:
                    wrong_versions = True
        if wrong_versions:
            continue
        duration = (finish_time - start_time) / 3600.0
        if not (MIN_PLAYING_DURATION <= duration <= MAX_PLAYING_DURATION):
            continue
        if not (MIN_PROGRAMM_UNITS <= programmed_units <= MAX_PROGRAMM_UNITS):
            continue
        if len(s['art']) == 0:
            continue
        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
        player_programs = {}
        for artefact, unit_data in s['art'].items():
            if artefact in Programs:
                phash = Programs[artefact]
                uniq_artefact, uniq_program, _ = Unique_programs[phash]
                unit, _, _, _ = unit_data
                if str(uniq_program) == str(Units[unit]):
                    # skip programs equal to default
                    continue
                player_programs[uniq_artefact] = uniq_program
                if uniq_artefact not in Start_programs:
                    isom_stats = data.check_isomorphic_programs(Units[unit], uniq_program, Programs_words)
                    for k, v in isom_stats.items():
                        if k not in Programs_stats:
                            Programs_stats[k] = 0
                        if v:
                            Programs_stats[k] += 1
                    Start_programs[uniq_artefact] = (unit, set([]), isom_stats)
                if player not in Start_programs[uniq_artefact][1]:
                    Start_programs[uniq_artefact][1].add(player)
                
        if len(player_programs) > 0:
            Start_players[player] = player_programs

    print()
    print('total players: {}'.format(len(Players)))
    print('players: {}'.format(len(Start_players)))
    n = len(Start_programs)
    print('player programs: {}'.format(n))

    print()
    print('Scripts statistics:')
    for k, v in Programs_stats.items():
        print("{:30} {:3} {:4.2}".format(k, v, v / n))
    
    i = 1
    print()
    print('Top {} start programs (by usage):'.format(PROGRAMS_LIMIT))
    for art, data in sorted(Start_programs.items(), key=lambda x: len(x[1][1]), reverse=True):
        unit, pl, isom = data
        print('{:10} {} {:6} {} {:3}'.format(unit, art, len(pl),
                                             'I' if isom['isomorphic to default'] else ' ',
                                             isom['new nodes']))
        i += 1
        if i == PROGRAMS_LIMIT:
            break
