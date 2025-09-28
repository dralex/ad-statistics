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

DAMAGE_FILTER      = True          # skip programs w/o damage
STANDARD_FILTER    = True          # skip programs based on the standard example

PROGRAMS_LIMIT     = 50            # most used programs limit
STANDARD_PATH      = 'standard_programs'
STANDARD_PATH_NEW  = os.path.join('standard_programs', '1.6')
STANDARD_UNITS     = ('Autoborder', 'Stapler')

FIND_ACTION        = 'entry/МодульДвижения.ДвигатьсяПоКоординатам();Диод.Включить(зеленый);Таймер.ТаймерЗапуск(6)'

if __name__ == '__main__':

    if len(sys.argv) < 2:
        Players_data = DEFAULT_PLAYERS_DATA
    else:
        Players_data = sys.argv[1]

    Units = data.load_default_programs(False)
    Units16 = data.load_default_programs(True)
    Standard_units = {}
    Standard_units16 = {}
    for u in STANDARD_UNITS:
        Standard_units[u] = data.load_program_path(STANDARD_PATH, u)
        Standard_units16[u] = data.load_program_path(STANDARD_PATH_NEW, u)
    Unique_programs = {}
    Unique_programs_with_names = {}
    Programs = {}
    Players = data.read_players_sessions(Players_data, None, False)
    Start_players = {}
    Start_programs = {}
    Programs_words = {}
    Programs_stats = {}
    Players_programs_distribution = {}
    Popular_actions = {}
    Programs_with_standards = {}
    Players_found = set([])

    for player, values in Players.items():        
        _, _, sessions = values
        data.load_player_programs(player, Programs, Unique_programs, Unique_programs_with_names)
        player_programs = []
        for s in sessions:
            for artefact, unit_data in s['art'].items():
                if artefact in Programs:
                    phash = Programs[artefact]
                    uniq_artefact, uniq_program, _ = Unique_programs[phash]
                    unit, dmg, _, d, version = unit_data
                    if DAMAGE_FILTER and dmg == 0:
                        continue
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
                        
                    if STANDARD_FILTER and unit in STANDARD_UNITS:
                        if new_found:
                            s_unit = Standard_units16[unit]
                        else:
                            s_unit = Standard_units[unit]
                        isom_stats = data.check_isomorphic_programs(s_unit, uniq_program)
                        if isom_stats['isomorphic to default'] or isom_stats['extended default']:
                            if player not in Programs_with_standards:
                                Programs_with_standards[player] = set([uniq_artefact])
                            else:
                                Programs_with_standards[player].add(uniq_artefact)
                            continue

                    if uniq_artefact not in Start_programs:
                        if player not in Popular_actions:
                            Popular_actions[player] = {}
                        isom_stats = data.check_isomorphic_programs(the_unit, uniq_program, None, False, Popular_actions[player])
                        for k, v in isom_stats.items():
                            if k not in Programs_stats:
                                Programs_stats[k] = 0
                            if v:
                                Programs_stats[k] += 1
                        Start_programs[uniq_artefact] = [unit, set([]), 0, isom_stats]
                        if len(player_programs) == 0 or str(player_programs[-1][3]) != str(uniq_program):
                            player_programs.append((d, the_unit, isom_stats, uniq_program))
                    else:
                        isom_stats = Start_programs[uniq_artefact][3]
                        if len(player_programs) == 0 or str(player_programs[-1][3]) != str(uniq_program): 
                            player_programs.append((d, the_unit, isom_stats, uniq_program))
                    if player not in Start_programs[uniq_artefact][1]:
                        Start_programs[uniq_artefact][1].add(player)
                    Start_programs[uniq_artefact][2] += 1

        if len(player_programs) > 0:
            player_programs = sorted(player_programs, key=lambda x: x[0])
            Start_players[player] = player_programs
            n = len(player_programs) % 10
            if n not in Players_programs_distribution:
                Players_programs_distribution[n] = 1
            else:
                Players_programs_distribution[n] += 1

    n2 = 0
    Used_programs_stats = {}
    for v in Start_programs.values():
        _, _, units, isom_stats = v
        if units < 2: continue
        n2 += 1
        for k, v in isom_stats.items():
            if k not in Used_programs_stats:
                Used_programs_stats[k] = 0
            if v:
                Used_programs_stats[k] += 1

    n3 = 0
    First_programs_stats = {}
    for v in Start_players.values():
        _, _, isom_stats, _ = v[0]
        n3 += 1
        for k, v in isom_stats.items():
            if k not in First_programs_stats:
                First_programs_stats[k] = 0
            if v:
                First_programs_stats[k] += 1

    n4 = 0
    Second_programs_stats = {}
    FS_popular_actions = {}
    for programs in Start_players.values():
        p1 = None
        p2 = None
        for p in programs:
            if p1 is None:
                p1 = p[-1]
            elif p2 is None and str(p1) != str(p[-1]):
                p2 = p[-1]
                break
        if p1 is None or p2 is None: continue
        n4 += 1
        isom_stats = data.check_isomorphic_programs(p1, p2, None, False, FS_popular_actions)
        for k, v in isom_stats.items():
            if k not in Second_programs_stats:
                Second_programs_stats[k] = 0
            if v:
                Second_programs_stats[k] += 1

    Players_popular_actions = {}
    for pl, actions in Popular_actions.items():
        for a, n in actions.items():
            a = a.replace('\n', ';')
            if a not in Players_popular_actions:
                Players_popular_actions[a] = [set([pl,]), n] 
            else:
                Players_popular_actions[a][0].add(pl)
                Players_popular_actions[a][1] += n

    print()
    print('total players: {}'.format(len(Players)))
    print('players: {}'.format(len(Start_players)))
    print('players with standards: {}'.format(len(Programs_with_standards)))
    n = len(Start_programs)
    print('player programs: {}'.format(n))
    print('programs with standards: {}'.format(sum(map(len, Programs_with_standards.values()))))

    print()
    print('Players with programs distribution:')
    for k,v in sorted(Players_programs_distribution.items(), key=lambda x: x[0]):
        print("<{:3} {:3}".format((k + 1) * 10, v))

    print()
    print('Full scripts statistics ({}):'.format(n))
    for k,v in sorted(Programs_stats.items(), key=lambda x: (x[1] / n, x[0]), reverse=True):
        print("{:45} {:6} {:5.1f}%".format(k, v, 100.0 * v / n))
    print()
    print('Used scripts statistics ({}):'.format(n2))
    for k,v in sorted(Used_programs_stats.items(), key=lambda x: (x[1] / n2, x[0]), reverse=True):
        print("{:45} {:6} {:5.1f}%".format(k, v, 100.0 * v / n2))
    print()
    print('First program statistics ({}):'.format(n3))
    for k,v in sorted(First_programs_stats.items(), key=lambda x: (x[1] / n3, x[0]), reverse=True):
        print("{:45} {:6} {:5.1f}%".format(k, v, 100.0 * v / n3))
    print()
    print('First-to-Second program statistics ({}):'.format(n4))
    for k,v in sorted(Second_programs_stats.items(), key=lambda x: (x[1] / n4, x[0]), reverse=True):
        print("{:45} {:6} {:5.1f}%".format(k, v, 100.0 * v / n4))

    print()
    print('Top {} popular actions in new/diff nodes by players:'.format(PROGRAMS_LIMIT))
    i = 1 
    for k,v in sorted(Players_popular_actions.items(), key=lambda x: (len(x[1][0]), x[1][1]), reverse=True):
        print("{:5} {:5} '{}'".format(len(v[0]), v[1], k))
        i += 1
        if i == PROGRAMS_LIMIT:
            break
    print()
    print('Top {} popular actions in new/diff nodes (first-to-second program):'.format(PROGRAMS_LIMIT))
    i = 1 
    for k,v in sorted(FS_popular_actions.items(), key=lambda x: x[1], reverse=True):
        print("{:5} '{}'".format(v, k.replace('\n', ';')))
        i += 1
        if i == PROGRAMS_LIMIT:
            break

    i = 1
    print()
    print('Top {} start programs (by usage):'.format(PROGRAMS_LIMIT))
    print('                                                   pls  units I No Ed Ac a o D O R M')
    for art, data in sorted(Start_programs.items(), key=lambda x: (len(x[1][1]), x[1][2]), reverse=True):
        unit, pl, units, isom = data
        print('{:10} {} {:6} {:6} {} {}  {} {} {} {} {} {} {} {}'.format(unit, art, len(pl), units,
                                                                            ('E' if isom['extended default'] else
                                                                             ('I' if isom['isomorphic to default'] else ' ')),
                                                                            ('1e' if isom['single empty new node'] else
                                                                             ('1-' if isom['single new node with default state name'] else
                                                                              (' 1' if isom['single new node'] else
                                                                               ('+-' if isom['new nodes with default state name'] else
                                                                                ('++' if isom['new nodes'] else '  '))))),
                                                                            '+' if isom['new edges'] else ' ',
                                                                            (' 1' if isom['single diff action'] else
                                                                             ('++' if isom['diff actions'] else '  ')),
                                                                            '+' if isom['diff actions args'] else ' ',
                                                                            '+' if isom['diff actions order'] else ' ',
                                                                            '+' if isom['debug actions'] else ' ',
                                                                            '+' if isom['overdrive actions'] else ' ',
                                                                            '+' if isom['repair actions'] else ' ',
                                                                            '+' if isom['movefrom actions'] else ' '))
        i += 1
        if i == PROGRAMS_LIMIT:
            break

    if FIND_ACTION and FIND_ACTION in Players_popular_actions:
        players = Players_popular_actions[FIND_ACTION][0]
        print('Found {} players with action "{}"'.format(len(players), FIND_ACTION))
        for p in players:
            print()
            print('------------------ player ', p, ' ----------------------')
            for pr in Start_players[p]:
                print(pr[3])
