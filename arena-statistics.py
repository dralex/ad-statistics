#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence: Arena statistics analysis tool
# 
#  Base statistics tool
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
import adata

TOP_PROGRAMS = 20

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('usage: {} <rosters-database.csv>'.format(sys.argv[0]))
        sys.exit(1)

    default_programs, default_hashes = adata.load_default_programs()
    uniq_programs = {}

    players = None
    stat_players_n = 0
    stat_players_with_programs = 0
    stat_drones = 0
    stat_programmed_drones = 0
    stat_broken_programs = 0
    stat_units = {}
    stat_prog_units = {}
    for u in adata.UNITS:
        stat_units[u] = stat_prog_units[u] = 0
    stat_rosters = 0

    players = adata.read_rosters(sys.argv[1], default_hashes, uniq_programs)

    for p, r in players.items():
        stat_players_n += 1
        has_programs = True
        for roster in r.values():
            stat_rosters += 1
            if not has_programs and len(roster['programs']) > 0:
                has_programs = True
            for u in roster['units']:
                stat_drones += 1
                stat_units[u['type']] += 1
                if not u['default']:
                    if u['broken']:
                        stat_broken_programs += 1
                    else:
                        stat_programmed_drones += 1
                        stat_prog_units[u['type']] += 1
        if has_programs:
            stat_players_with_programs += 1

    print()
    print('Players: {}'.format(stat_players_n))
    print('Players with programs: {} ({:.2f}%)'.format(stat_players_with_programs,
                                                      100.0 * stat_players_with_programs / stat_players_n))
    print()
    print('Total drones: {}'.format(stat_drones))
    print('Drones with programs: {} ({:.2f}%)'.format(stat_programmed_drones,
                                                      100.0 * stat_programmed_drones / stat_drones))
    print('Broken programs: {} ({:.2f}%)'.format(stat_broken_programs,
                                                 100.0 * stat_broken_programs / stat_drones))
    print('Drone types:')
    for u, count in sorted(stat_units.items(), key=lambda k: k[1], reverse=True):
        print('{:11}: {:5} ({:4.1f}%), programmed: {:5} ({:4.1f}%)'.format(u, count, 100.0 * count / stat_drones,
                                                       stat_prog_units[u], 100 * stat_prog_units[u] / stat_programmed_drones))
    print()
    print('Unique programs: {}'.format(len(uniq_programs)))
    i = 0
    print('Top {} start programs (by usage):'.format(TOP_PROGRAMS))
    print('                                                       pls          units I No Ed Ac a o D O R M')
    for pstr, pvalues in sorted(uniq_programs.items(), key=lambda k: (len(k[1][4]), k[1][3]), reverse=True):
        utype, graph_id, program, count, players = pvalues
        isom = adata.check_isomorphic_programs(default_programs[utype], program)
        print('{:15} {} {:5} {:5} ({:5.1f}%) {} {}  {} {} {} {} {} {} {} {}'.format(utype,
                                                                                    graph_id, 
                                                                                    len(players),
                                                                                    count,
                                                                                    100 * count / stat_programmed_drones,
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
        if i == TOP_PROGRAMS: break
    print()
    print('Rosters: {}'.format(stat_rosters))
