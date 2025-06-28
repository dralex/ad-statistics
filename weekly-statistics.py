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
HTML_TEMPLATE_FILE = 'web/weekly-table-tmpl.html'
HTML_TEMPLATE_STRING = '##DATA_'
HTML_TABLE_CLASS = 'tabtable'
HTML_HEADER_CLASS = 'tabheader'
HTML_ROW_CLASS = 'tabrow'
HTML_CELL_NAME_CLASS = 'tabcellname'
HTML_CELL_WEEK_CLASS = 'tabcellweek'
HTML_CELL_0_CLASS = 'tabcell0'
HTML_CELL_25_CLASS = 'tabcell25'
HTML_CELL_50_CLASS = 'tabcell50'
HTML_CELL_75_CLASS = 'tabcell75'
HTML_CELL_100_CLASS = 'tabcell100'

def usage():
    print('usage: {} <database.csv> [output.html]'.format(sys.argv[0]))
    exit(1)

def calc_statistics(players):

    sheets = {}

    _all_versions = set([])
    
    _all_levelwaves = set([])
    for level in ('0', '1', '2', '3', '4'):
        if level == '0' or level == '4':
            level_range = 10
        else:
            level_range = 15
        for w in range(level_range):
            levelwave = '{}-{:02d}'.format(level, w + 1)
            _all_levelwaves.add(levelwave)
    _all_levelwaves.add('Poly')

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

                if 'l' not in a or 'w' not in a:
                    continue
                if a['l'] == 'Polygon':
                    levelwave = 'Poly'
                else:
                    if a['l'] == 'Start':
                        level = '0'
                    elif a['l'] == 'Infinity':
                        level = '4'
                    else:
                        level = a['l']
                    levelwave = '{}-{:02d}'.format(level, a['w'])
                if levelwave not in _all_levelwaves:
                    print('Unknown level+wave {} in year {} week {}'.format(levelwave, year, week))
                    sys.exit(1)
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

            if week == 0 and (year - 1) in sheets:
                prevprev_week = sheets[year - 1][MAX_WEEK - 1]
            elif week == 1 and (year - 1) in sheets:
                prevprev_week = sheets[year - 1][MAX_WEEK]
            elif week > 1:
                prevprev_week = y_sheet[week - 2]
            else:
                prevprev_week = {'players': set([])}

            w_data['all players'] = len(w_data['players'])
            w_data['prev players'] = len(w_data['players'] & prev_week['players'])
            w_data['2week players'] = len(w_data['players'] & (prev_week['players'] | prevprev_week['players']))
            w_data['3week players'] = len(w_data['players'] & prev_week['players'] & prevprev_week['players'])

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

        max_actions = 0
        max_units = 0
        max_prunits = 0
        max_all_players = 0
        max_prev_players = 0
        max_2week_players = 0
        max_3week_players = 0

        for w_data in y_sheet.values():
            if w_data['all players'] > max_all_players: max_all_players = w_data['all players']
            if w_data['prev players'] > max_prev_players: max_prev_players = w_data['prev players']
            if w_data['2week players'] > max_2week_players: max_2week_players = w_data['2week players']
            if w_data['3week players'] > max_3week_players: max_3week_players = w_data['3week players']
            if w_data['actions'] > max_actions: max_actions = w_data['actions']
            if w_data['units'] > max_units: max_units = w_data['units']
            if w_data['prunits'] > max_units: max_units = w_data['prunits']

        for week, w_data in sorted(y_sheet.items(), key=lambda x: x[0]):
            print()
            print('  WEEK {}:'.format(week + 1))
            print('  actions: {} [{}]'.format(w_data['actions'], 100 * w_data['actions'] / max_actions))
            print('  players: {} [{}] 2w: {} 2-3w: {} 3w: {}'.format(w_data['all players'],
                                                                     100 * w_data['all players'] / max_all_players,
                                                                     w_data['prev players'],
                                                                     w_data['2week players'],
                                                                     w_data['3week players']))
            print('  units: {} punits: {}'.format(w_data['units'], w_data['prunits']))
            print('  versions:')
            for v, num in sorted(w_data['all versions'].items(), key=lambda x: x[0]):
                print('    {}: {}'.format(v, num))                
            print('  level+wave:')
            for lw, num in sorted(w_data['all levelwaves'].items(), key=lambda x: x[0]):
                print('    {}: {}'.format(lw, num))

def print_html_key_row(f, y_sheet, param, k, maximum):
    f.write('  <tr class="{}">\n'.format(HTML_ROW_CLASS))
    f.write('    <td class="{}">{}</td>\n'.format(HTML_CELL_NAME_CLASS, k))    
    for _, w_data in sorted(y_sheet.items(), key=lambda x: x[0]):
        if w_data[param][k] > 0 and maximum > 0:
            percent = int(100.0 * w_data[param][k] / maximum)
            if percent <= 25:
                cell_class = HTML_CELL_25_CLASS
            elif percent <= 50:
                cell_class = HTML_CELL_50_CLASS
            elif percent <= 75:
                cell_class = HTML_CELL_75_CLASS
            else:
                cell_class = HTML_CELL_100_CLASS
        else:
            cell_class = HTML_CELL_0_CLASS
        f.write('    <td class="{}">{}</td>\n'.format(cell_class, w_data[param][k]))
    f.write('  </tr>\n')
                
def print_html_row(f, y_sheet, name, param, maximum):
    f.write('  <tr class="{}">\n'.format(HTML_ROW_CLASS))
    f.write('    <td class="{}">{}</td>\n'.format(HTML_CELL_NAME_CLASS, name))    
    for _, w_data in sorted(y_sheet.items(), key=lambda x: x[0]):
        if w_data[param] > 0 and maximum > 0:
            percent = int(100.0 * w_data[param] / maximum)
            if percent <= 25:
                cell_class = HTML_CELL_25_CLASS
            elif percent <= 50:
                cell_class = HTML_CELL_50_CLASS
            elif percent <= 75:
                cell_class = HTML_CELL_75_CLASS
            else:
                cell_class = HTML_CELL_100_CLASS
        else:
            cell_class = HTML_CELL_0_CLASS
        f.write('    <td class="{}">{}</td>\n'.format(cell_class, w_data[param]))
    f.write('  </tr>\n')

def print_html_table(f, sheets, year):

    y_sheet = sheets[year]
    
    max_actions = 0
    max_units = 0
    max_prunits = 0
    max_all_players = 0
    max_prev_players = 0
    max_2week_players = 0
    max_3week_players = 0
    max_levelwaves_players = 0
    max_versions_players = 0

    all_levelwaves = None
    all_versions = None

    for w_data in y_sheet.values():
        if w_data['all players'] > max_all_players: max_all_players = w_data['all players']
        if w_data['prev players'] > max_prev_players: max_prev_players = w_data['prev players']
        if w_data['2week players'] > max_2week_players: max_2week_players = w_data['2week players']
        if w_data['3week players'] > max_3week_players: max_3week_players = w_data['3week players']
        if w_data['actions'] > max_actions: max_actions = w_data['actions']
        if w_data['units'] > max_units: max_units = w_data['units']
        if w_data['prunits'] > max_prunits: max_prunits = w_data['prunits']
        if not all_levelwaves:
            all_levelwaves = tuple(sorted(w_data['all levelwaves'].keys()))
        if not all_versions:
            all_versions = tuple(sorted(w_data['all versions'].keys()))
        for lw_players in w_data['all levelwaves'].values():
            if lw_players > max_levelwaves_players: max_levelwaves_players = lw_players
        for v_players in w_data['all versions'].values():
            if v_players > max_versions_players: max_versions_players = v_players
    
    f.write('<table class="{}">\n'.format(HTML_TABLE_CLASS))
    f.write('  <tr class="{}">\n'.format(HTML_ROW_CLASS))
    f.write('    <th class="{}">Неделя</td>\n'.format(HTML_CELL_NAME_CLASS))
    for week, w_data in sorted(y_sheet.items(), key=lambda x: x[0]):
        f.write('    <th class="{}">{}</td>\n'.format(HTML_CELL_WEEK_CLASS, week + 1))
    f.write('  </tr>\n')
    print_html_row(f, y_sheet, 'Активности', 'actions', max_actions)
    f.write('  <tr class="{}"><td class={} colspan="{}">ПОЛЬЗОВАТЕЛИ</td></tr>\n'.format(HTML_ROW_CLASS,
                                                                                         HTML_CELL_NAME_CLASS,
                                                                                         len(y_sheet.keys()) + 1))  
    print_html_row(f, y_sheet, 'Пользователи', 'all players', max_all_players)
    print_html_row(f, y_sheet, 'Пользователи (+ пред.нед.)', 'prev players', max_prev_players)
    print_html_row(f, y_sheet, 'Пользователи (+ 2 пред.нед.)', '2week players', max_2week_players)
    print_html_row(f, y_sheet, 'Пользователи (обе пред.нед.)', '3week players', max_3week_players)
    f.write('  <tr class="{}"><td class={} colspan="{}">ДРОНЫ</td></tr>\n'.format(HTML_ROW_CLASS,
                                                                                  HTML_CELL_NAME_CLASS,
                                                                                  len(y_sheet.keys()) + 1))  
    print_html_row(f, y_sheet, 'Дроны', 'units', max_units)
    print_html_row(f, y_sheet, 'Прогр. дроны', 'prunits', max_prunits)
    f.write('  <tr class="{}"><td class={} colspan="{}">УРОВНИ</td></tr>\n'.format(HTML_ROW_CLASS,
                                                                                   HTML_CELL_NAME_CLASS,
                                                                                   len(y_sheet.keys()) + 1))  
    for lw in all_levelwaves:
        print_html_key_row(f, y_sheet, 'all levelwaves', lw, max_levelwaves_players)
    f.write('  <tr class="{}"><td class={} colspan="{}">ВЕРСИИ</td></tr>\n'.format(HTML_ROW_CLASS,
                                                                                   HTML_CELL_NAME_CLASS,
                                                                                   len(y_sheet.keys()) + 1))  
    for v in all_versions:
        print_html_key_row(f, y_sheet, 'all versions', v, max_versions_players)
    f.write('</table>\n')

def save_statistics_to_html(sheets, filename):
    html_output = open(filename, 'w')
    html_template = open(HTML_TEMPLATE_FILE)
    for line in html_template.read().splitlines():
        if line.find(HTML_TEMPLATE_STRING) == 0:
            year = int(line.split('_')[1])
            if year in sheets:
                print_html_table(html_output, sheets, year)
        else:
            html_output.write(line + "\n")
    html_output.close()

if __name__ == '__main__':

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()

    players = data.read_players_data(sys.argv[1])
    sheets = calc_statistics(players)
    if len(sys.argv) == 2:
        print_statistics(sheets)
    else:
        save_statistics_to_html(sheets, sys.argv[2])

