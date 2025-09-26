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
    Start_players = set([])
    
    for player, values in Players.items():        
        activities, _, sessions = values
        if not (MIN_PLAYING_SESSIONS <= len(sessions) <= MAX_PLAYING_SESSIONS):
            continue
        max_level = 0
        programmed_units = 0
        start_time = datetime.datetime.now().timestamp()
        finish_time = 0
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
        duration = (finish_time - start_time) / 3600.0
        if not (MIN_PLAYING_DURATION <= duration <= MAX_PLAYING_DURATION):
            continue
        if not (MIN_PROGRAMM_UNITS <= programmed_units <= MAX_PROGRAMM_UNITS):
            continue
        Start_players.add(player)

    print('total players: {}'.format(len(Players)))
    print('players: {}'.format(len(Start_players)))

    # for player, values in Players.items():                
    #     data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
    #     for s in sessions:
    #         for artefact, unit_data in s['art'].items():
    #             if artefact in Programs:
    #                 phash = Programs[artefact]
    #                 uniq_artefact, uniq_program, _ = Unique_programs[phash]
    #                 unit, dmg, enemies = unit_data
    #                 key = uniq_artefact + ':' + player
    #                 if uniq_artefact not in Best_Programs:
    #                     Best_Programs[uniq_artefact] = {}
    #                 if player not in Best_Programs[uniq_artefact]:
    #                     Best_Programs[uniq_artefact][player] = [unit, dmg, enemies]
    #                 else:
    #                     Best_Programs[uniq_artefact][player][1] += dmg
    #                     Best_Programs[uniq_artefact][player][2] += enemies

    #                 if uniq_artefact not in Best_Uniq_Programs:
    #                     Best_Uniq_Programs[uniq_artefact] = [unit, dmg, enemies]
    #                 else:
    #                     Best_Uniq_Programs[uniq_artefact][1] += dmg
    #                     Best_Uniq_Programs[uniq_artefact][2] += enemies

    #                 if key not in Best_Player_Programs:
    #                     Best_Player_Programs[key] = [unit, dmg, enemies]
    #                 else:
    #                     Best_Player_Programs[key][1] += dmg
    #                     Best_Player_Programs[key][2] += enemies

    # i = 1
    # print()
    # print('Best {} unique programs (by damage):'.format(LIMIT))
    # for art, data in sorted(Best_Uniq_Programs.items(), key=lambda x: x[1][1], reverse=True):
    #     unit, dmg, enemies = data
    #     if dmg == 0.0:
    #         break
    #     print('{:10} {} {:10.1f} {:6}'.format(unit, art, dmg, enemies))
    #     i += 1
    #     if i == LIMIT:
    #         break
