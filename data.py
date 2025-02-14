#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Data utilities
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

import os
import csv
import urllib.request
import datetime
import hashlib

import CyberiadaML

DEFAULT_PROGRAMS_DIR = 'default_programs'
PROGRAMS_DIR = 'programs'
LAST_WAVE_METRICS = 'last_wave'
LEVEL_START = 'Start'
LEVEL_INFINITY = 'Infinity'
LEVELS = [LEVEL_START, '1', '2', '3', LEVEL_INFINITY]
UNITS = ['Autoborder', 'Stapler', 'Smoker', 'Generator']
TRADITIONS = ['Constructor', 'Beekeeper', 'Programmer']
DEFAULT_STATE_NAME = 'Состояние'

def get_artefact_file(player_id, artefact_id):
    return os.path.join(PROGRAMS_DIR, player_id, artefact_id) + ".graphml"

def read_players_data(csv_file, player_filter = None, delimiter=','):
    players = {}
    print('read from file {}'.format(csv_file))
    reader = csv.reader(open(csv_file), delimiter=delimiter)
    i = 0
    for row in reader:
        i += 1
        if len(row) != 20:
            print("Cannot read players' database from CSV: bad row {}".format(i))
            exit(1)
        if row[0] == 'id':
            continue
        if len(row[11]) == 0:
            continue
        
        try:
            if row[1].find('.'):
                d = datetime.datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%S.%f+03:00').timestamp()
            else:
                d = datetime.datetime.strptime(row[1], '%Y-%m-%dT%H:%M:%S+03:00').timestamp()
        except ValueError:
            print("Cannot read players' database from CSV: bad data {} at row {}".format(row[1], i))
            continue

        activity_id = row[0]
        player_id = row[3]
        if player_filter and player_id not in player_filter:
            continue
        if player_id not in players:
            players[player_id] = ({}, [], [])

        if activity_id not in players[player_id][0]:
            players[player_id][0][activity_id] = {}

        a = players[player_id][0][activity_id]

        metrics_id = int(row[11])
        a['i'] = metrics_id
        
        if 'd' not in a:
            a['d'] = d
            players[player_id][1].append((d, metrics_id, a))

        metrics_key = row[12]
        if metrics_key == 'last_wave' or metrics_key == 'wave':
            metrics_value = int(float(row[13])+1)
        else:
            metrics_value = float(row[13])

        if 'm' not in a:
            a['m'] = {}
        a['m'][metrics_key] = metrics_value
            
        if 'type' not in a:
            if row[10].find('Level') == 0:
                _, level, origin = row[10].split('_')
                if level not in LEVELS:
                    print("Cannot read players' database from CSV: bad stat level {} at row {}".format(level, i))
                    exit(1)
                a['l'] = level
                if origin in UNITS:
                    a['t'] = 'u'
                    a['u'] = origin
                    uploaded = (row[19] == 'true')
                    if uploaded:
                        a['ac'] = (row[7], row[18])
                elif origin in TRADITIONS:
                    a['t'] = 't'
                    a['p'] = origin
                else:
                    print("Cannot read players' database from CSV: bad stat origin {} at row {}".format(origin, i))
                    exit(1)
            else:
                a['t'] = 'f'

        if metrics_key == 'try' and a['t'] == 'f':
            a['y'] = int(float(metrics_value))
        if metrics_key == 'level' and a['t'] == 'f':
            level = int(float(metrics_value))
            if level < 0 or level >= len(LEVELS):
                print("Cannot read players' database from CSV: bad final level {} at row {}".format(level, i))
                exit(1)
            a['l'] = LEVELS[level]
        if (metrics_key == 'last_wave' or metrics_key == 'wave') and 'w' not in a:
            a['w'] = metrics_value

    print(i, "lines loaded")
    print('recinstruct sessions...')

    def avg_sum_session(session):
        total_tries = 0
        total_units = 0
        total_progs = 0
        avg_units = 0.0
        avg_progs = 0.0
        avg_dmg = 0.0
        for w, tries in session['ws'].items():
            for t, v in tries.items():
                units, progs, dmg = v
                if units == 0:
                    continue
                total_tries += 1
                total_units += units
                total_progs += progs
                avg_units += units
                avg_progs += float(progs) / units
                avg_dmg += dmg / units
        if total_tries > 0:
            avg_units /= float(total_tries)
            avg_progs /= float(total_tries)
            avg_dmg /= float(total_tries)
        session['tries'] = total_tries
        session['units'] = total_units
        session['punits'] = total_progs
        session['avg_u'] = avg_units
        session['avg_p'] = avg_progs
        session['avg_d'] = avg_dmg
    
    for player, values in players.items():
        activities, datetable, sessions = values

        cur_session = None
        cur_try = 1

        for d, _, a in sorted(datetable, key = lambda x: (x[0], x[1])):
            level = a['l']
            if 'w' not in a: 
                continue
            wave = a['w']
            
            unit = a['u'] if a['t'] == 'u' else None
            tradition = a['p'] if a['t'] == 't' else None
            art_cs = a['ac'] if 'ac' in a else None

            if cur_session is not None and wave not in cur_session['ws']:
                cur_try = 1
                cur_session['ws'][wave] = {cur_try: [0, 0, 0.0]}

            if cur_session is not None and level == cur_session['l'] and wave >= cur_session['w']:
                if unit is not None:
                    if unit not in cur_session['u']:
                        cur_session['u'].append(unit)
                    if art_cs is not None:
                        cur_session['art'][art_cs[0]] = unit
                        #else:
                        #    print('program {} is already in session, orig: {}'.format(art_cs[0], cur_session['art'][art_cs[1]]))
                        cur_session['ws'][wave][cur_try][1] += 1
                    cur_session['ws'][wave][cur_try][0] += 1
                    if 'drone_damage' in a['m']: 
                        cur_session['ws'][wave][cur_try][2] += a['m']['drone_damage']
                if tradition is not None and cur_session['t'] is None:
                    cur_session['t'] = tradition
                if a['t'] == 'f' and a['y'] > cur_try:
                    cur_try += 1
                    cur_session['ws'][wave][cur_try] = [0, 0, 0.0]
                cur_session['w'] = wave
                cur_session['fd'] = d
                cur_session['a'].append(a)
            else:
                if cur_session is not None:
                    avg_sum_session(cur_session)
                    sessions.append(cur_session)

                cur_try = 1
                cur_session = {'l': level, 'w': wave, 'ws': {wave: {cur_try: [0, 0, 0.0]}}, 'sd': d, 'fd': d, 'a': [a],
                               'u': [], 't': tradition, 'art': {}}
                if unit is not None:
                    cur_session['u'].append(unit)
                    cur_session['ws'][wave][cur_try][0] += 1
                    if art_cs is not None:
                        cur_session['art'][art_cs[0]] = unit
                        cur_session['ws'][wave][cur_try][1] += 1
                    if 'drone_damage' in a['m']:
                        cur_session['ws'][wave][cur_try][2] += a['m']['drone_damage']
        if cur_session is not None:
            avg_sum_session(cur_session)
            sessions.append(cur_session)

    # for player, values in players.items():
    #     _, _, sessions = values
    #     for s in sessions:
    #         print("level: {}, last wave: {}, waves(tries): {}, date from: {}, to: {}, activities: {}, tradition: {}, unit types: ({}), uniq progs: {}, avg units: {:5.2f}, avg prog percent: {:5.2f}%, avg dmg: {:6.1f}".format(
    #             s['l'], s['w'], s['tries'],
    #             datetime.datetime.fromtimestamp(s['sd']).strftime('%Y-%m-%d %H:%M:%S'),
    #             datetime.datetime.fromtimestamp(s['fd']).strftime('%Y-%m-%d %H:%M:%S'),
    #             len(s['a']),
    #             s['t'],
    #             ', '.join(s['u']),
    #             len(s['art']),
    #             s['avg_u'], s['avg_p'] * 100.0, s['avg_d']))

    return players

def load_default_programs():
    print('Loading default programs...')
    programs = {}
    for u in UNITS:
        d = CyberiadaML.LocalDocument()
        d.open(os.path.join(DEFAULT_PROGRAMS_DIR, u + '.graphml'), CyberiadaML.formatDetect, CyberiadaML.geometryFormatNone)
        p = CyberiadaML.StateMachine(d.get_state_machines()[0])
        p.set_name('SM')
        programs[u] = p
        # print(u, programs[u])
    return programs

def load_program(artefact_id):
    for u in os.listdir(PROGRAMS_DIR):
        dir_path = os.path.join(PROGRAMS_DIR, u)
        filepath = os.path.join(dir_path, artefact_id + '.graphml')
        if os.path.isfile(filepath):
            d = CyberiadaML.LocalDocument()
            d.open(filepath, CyberiadaML.formatDetect, CyberiadaML.geometryFormatNone)
            program = CyberiadaML.StateMachine(d.get_state_machines()[0])
            return program
    return None

def load_player_programs(player_id, programs, hashes, hashes_with_name):
    file_hashes = {}
    dir_path = os.path.join(PROGRAMS_DIR, player_id)
    if not os.path.isdir(dir_path):
        return 
    for f in os.listdir(dir_path):
        filepath = os.path.join(dir_path, f)
        artefact = f.split('.')[0]
        h = hashlib.md5(open(filepath,'rb').read()).hexdigest()
        if h in file_hashes:
            programs[artefact] = file_hashes[h]
            continue
        try:
            d = CyberiadaML.LocalDocument()
            d.open(filepath, CyberiadaML.formatDetect, CyberiadaML.geometryFormatNone)
            p = CyberiadaML.StateMachine(d.get_state_machines()[0])
            phash_with_name = hash(str(p))    
            p.set_name('SM')
            phash = hash(str(p))
            #print(hash(str(p)),str(p))
        except CyberiadaML.CybMLException:
            print('Bad program:', filepath)
            continue
        except CyberiadaML.XMLException:
            print('Bad program file:', filepath)
            continue
        file_hashes[h] = phash
        programs[artefact] = phash
        if phash_with_name not in hashes_with_name:
            hashes_with_name[phash_with_name] = True
        if phash in hashes:
            hashes[phash][2] += 1
            continue
        hashes[phash] = [artefact, p, 1]

def check_isomorphic_programs(unit_program, program, diff = False):
    initial = ''
    diff_nodes = []
    diff_nodes_flags = []
    new_nodes = []
    missing_nodes = []
    diff_edges = []
    diff_edges_flags = []
    new_edges = []
    missing_edges = []
    res = unit_program.check_isomorphism(program, True, False, initial,
					 diff_nodes, diff_nodes_flags, new_nodes, missing_nodes,
					 diff_edges, diff_edges_flags, new_edges, missing_edges)
    if diff:
        diff_arrays = {}
        diff_arrays['res'] = res
        diff_arrays['diff_nodes'] = diff_nodes
        diff_arrays['diff_nodes_flags'] = diff_nodes_flags
        diff_arrays['new_nodes'] = new_nodes
        diff_arrays['missing_nodes'] = missing_nodes
        diff_arrays['diff_edges'] = diff_edges
        diff_arrays['diff_edges_flags'] = diff_edges_flags
        diff_arrays['new_edges'] = new_edges
        diff_arrays['missing_edges'] = missing_edges
        return diff_arrays
    else:
        diff_names = 0
        diff_actions = 0
        default_names = 0
        for n in diff_nodes_flags:
            if n & CyberiadaML.smiNodeDiffFlagTitle:
                diff_names += 1        
            if n & CyberiadaML.smiNodeDiffFlagActions:
                diff_actions += 1

        for n in new_nodes:
            e = program.find_element_by_id(n)
            if e.get_name() == DEFAULT_STATE_NAME:
                default_names += 1

        return {'isomorphic to default': res == CyberiadaML.smiIsomorphic,
                'extended default': ((len(new_nodes) > 0 or len(new_edges) > 0 or diff_actions > 0) and
                                     len(missing_nodes) == 0 and len(missing_edges) == 0),
                'new nodes': len(new_nodes) > 0,
                'new nodes with default state name': default_names > 0,
                'missing nodes': len(missing_nodes) > 0,
                'detached nodes': (len(new_nodes) > 0 and len(missing_nodes) == 0 and
                                   len(missing_edges) == 0 and len(new_edges) == 0),
                'diff names': diff_names > 0,
                'diff actions': diff_actions > 0,
                'diff edges': len(diff_edges) > 0,
                'new edges': len(new_edges) > 0,
                'missing edges': len(missing_edges) > 0}
