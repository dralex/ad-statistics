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
MAX_PROGRAMM_UNITS =   100            # no more than 50 programmed units

if __name__ == '__main__':

    if len(sys.argv) < 2:
        Players_data = DEFAULT_PLAYERS_DATA
    else:
        Players_data = sys.argv[1]

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
        if len(s['art']) == 0:
            continue
        Start_players.add(player)

    for p in sorted(Start_players):
        print(p)
