#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Weekly summary statistics 
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
import csv

import data

MAX_WEEK = 52

def usage():
    print('usage: {} <database.csv>'.format(sys.argv[0]))
    exit(1)

def calc_statistics(players):

    sheets = {}

    _all_versions = set([])
    _all_levelwaves = set([])

    for player, values in players.items():
        activities, _, _ = values
        for a in activities.values():
            d = a['dpydate']
            year, week = d.isocalendar()[0:2]
            
            if year not in sheets:
                sheets[year] = {}
            if week not in sheets[year]:
                sheets[year][week] = {
                    'players': set([]),
                    'actions': 0,
                    'units': 0,
                    'prunits': 0,
                    'versions': {},
                    'levelwaves': {}
                }
                
            version = a['v']
            _all_versions.add(version)
            if version not in sheets[year][week]['versions']:
                sheets[year][week]['versions'][version] = set([player])
            else:
                sheets[year][week]['versions'][version].add(player)
            sheets[year][week]['players'].add(player)
            sheets[year][week]['actions'] += 1
            if a['t'] == 'u':
                sheets[year][week]['units'] += 1
                if 'ac' in a and a['ac'] is not None:
                    sheets[year][week]['prunits'] += 1

                if a['l'] == 'Polygon':
                    levelwave = 'Poly'
                else:
                    if a['l'] == 'Start':
                        level = '0'
                    else:
                        level = a['l']
                    levelwave = '{}-{:02d}'.format(level, a['w'])
                _all_levelwaves.add(levelwave)
                if levelwave not in sheets[year][week]['levelwaves']:
                    sheets[year][week]['levelwaves'][levelwave] = set([player])
                else:
                    sheets[year][week]['levelwaves'][levelwave].add(player)

    for year, y_sheet in sorted(sheets.items(), key=lambda x: x[0]):
        if year + 1 not in sheets:
            max_week = max(y_sheet.keys())
        else:
            max_week = MAX_WEEK
        for w in range(max_week + 1):
            if w not in y_sheet:
                y_sheet[w] = {
                    'players': set([]),
                    'actions': 0,
                    'units': 0,
                    'prunits': 0,
                    'versions': {},
                    'levelwaves': {}
                }
        for week, w_data in sorted(y_sheet.items(), key=lambda x: x[0]):

            if week == 0 and (year - 1) in sheets:
                prev_week = sheets[year - 1][MAX_WEEK]
            elif week > 0:
                prev_week = y_sheet[week - 1]
            else:
                prev_week = {'players': set([])}

            w_data['all players'] = len(w_data['players'])
            w_data['old players'] = len(w_data['players'] & prev_week['players'])

            w_data['all versions'] = {}
            for v in _all_versions:
                if v in w_data['versions']:
                    w_data['all versions'][v] = len(w_data['versions'][v])
                else:
                    w_data['all versions'][v] = 0

            w_data['all levelwaves'] = {}
            for lw in _all_levelwaves:
                if lw in w_data['levelwaves']:
                    w_data['all levelwaves'][lw] = len(w_data['levelwaves'][lw])
                else:
                    w_data['all levelwaves'][lw] = 0
            
    return sheets

def print_statistics(sheets):

    print()
    for year, y_sheet in sorted(sheets.items(), key=lambda x: x[0]):
        print("YEAR {}:".format(year))
        for week, w_data in sorted(y_sheet.items(), key=lambda x: x[0]):
            print()
            print('  WEEK {}:'.format(week))
            print('  players: {} old: {}'.format(w_data['all players'], w_data['old players']))
            print('  units: {} punits: {}'.format(w_data['units'], w_data['prunits']))
            print('  versions:')
            for v, num in sorted(w_data['all versions'].items(), key=lambda x: x[0]):
                print('    {}: {}'.format(v, num))                
            print('  level+wave:')
            for lw, num in sorted(w_data['all levelwaves'].items(), key=lambda x: x[0]):
                print('    {}: {}'.format(lw, num))

if __name__ == '__main__':

    if len(sys.argv) != 2:
        usage()

    players = data.read_players_data(sys.argv[1])
    sheets = calc_statistics(players)
    print_statistics(sheets)

