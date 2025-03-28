
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
LEVEL_POLYGON = 'Polygon'
LEVELS = [LEVEL_START, '1', '2', '3', LEVEL_INFINITY, LEVEL_POLYGON]
UNITS = ['Autoborder', 'Stapler', 'Smoker', 'Generator']
TRADITIONS = ['Constructor', 'Beekeeper', 'Programmer']
DEFAULT_STATE_NAME = 'Состояние'

# CSV file format:
# id,created_at,player,app_version,context,metrics_id,metrics_key,metrics_value,artefact,checksum

_CONTEXT_LEVEL = 'Level'
_CONTEXT_RESULTS = 'Итоги волны'
_CONTEXT_RESULTS_POLYGON = 'Polygon_wave_results'
_CONTEXT_START_PL = 'Start_placement'
_CONTEXT_FINISH_PL = 'Finish_placement'
_CONTEXT_START_GAME = 'Launch_game'
_CONTEXT_CLOSE_GAME = 'Closing_game'
_CONTEXT_OPEN_EDITOR = 'Оpening_editor'
_CONTEXT_CLOSE_EDITOR = 'Closing_editor'
_CONTEXT_SAVE_PROGRAM = 'Save_program'
_CONTEXT_POLYGON = 'Polygon_Start'
_CONTEXT_POLYGON_AB = 'Polygon_Autoborder'
_CONTEXT_POLYGON_SM = 'Polygon_Smoker'

_CSV_ID = 0
_CSV_DATETIME = 1
_CSV_PLAYER = 2
_CSV_APP_VERSION = 3
_CSV_CONTEXT = 4
_CSV_METRICS_ID = 5
_CSV_METRICS_KEY = 6
_CSV_METRICS_VALUE = 7
_CSV_ARTEFACT = 8
_CSV_CHECKSUM = 9
_CSV_SIZE = 10

_MAX_SESSION_LENGTH = 6 * 3600.0

def get_artefact_file(player_id, artefact_id):
    return os.path.join(PROGRAMS_DIR, player_id, artefact_id) + ".graphml"

def pack_player(player, d):
    return "{}:{}".format(player, int(d))
def unpack_player(player):
    if player.find(':') > 0:
        return player.split(':')[0]
    else:
        return player

def read_players_data(csv_file, player_filter = None, delimiter=','):
    players = {}
    print('read from file {}'.format(csv_file))
    reader = csv.reader(open(csv_file), delimiter=delimiter)
    i = 0
    for row in reader:
        i += 1
        if len(row) != _CSV_SIZE:
            print("Cannot read players' database from CSV: bad row {}".format(i))
            exit(1)
        if row[_CSV_ID] == 'id':
            # skip header
            continue
        if len(row[_CSV_METRICS_ID]) == 0:
            # skip empty metrics
            continue
        
        try:
            if row[_CSV_DATETIME].find('.') > 0:
                d = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f+03').timestamp()
            else:
                d = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S+03').timestamp()
        except ValueError:
            print("Cannot read players' database from CSV: bad data {} at row {}".format(row[_CSV_DATETIME], i))
            continue

        activity_id = row[_CSV_ID]
        player_id = row[_CSV_PLAYER]
        if player_filter: 
            if player_id not in player_filter:
                continue
            dates = player_filter[player_id]
            if dates is not None:
                found = False
                for dates_pair in dates:
                    date_from, date_to = dates_pair
                    if date_from <= d <= date_to:
                        player_id = pack_player(player_id, date_from)
                        found = True
                        break
                if not found:
                    continue                 

        if player_id not in players:
            players[player_id] = ({}, [], [])

        if activity_id not in players[player_id][0]:
            players[player_id][0][activity_id] = {}

        a = players[player_id][0][activity_id]

        app_version = row[_CSV_APP_VERSION]
        a['v'] = app_version
        
        metrics_id = int(row[_CSV_METRICS_ID])
        a['i'] = metrics_id
        
        if 'd' not in a:
            a['d'] = d
            #players[player_id][1].append([d, 0, metrics_id, a])

        metrics_key = row[_CSV_METRICS_KEY]
        metrics_value = float(row[_CSV_METRICS_VALUE])

        if 'm' not in a:
            a['m'] = {}
        a['m'][metrics_key] = metrics_value
            
        if 't' not in a:
            context = row[_CSV_CONTEXT]
            if (context.find(_CONTEXT_LEVEL) == 0 or context.find(_CONTEXT_POLYGON) == 0 or
                context == _CONTEXT_POLYGON_AB or context == _CONTEXT_POLYGON_SM):
                if context.find(_CONTEXT_LEVEL) == 0:
                    _, level, origin = row[_CSV_CONTEXT].split('_')
                elif context == _CONTEXT_POLYGON_AB or context == _CONTEXT_POLYGON_SM:
                    level = LEVEL_POLYGON
                    if context == _CONTEXT_POLYGON_AB:
                        origin = UNITS[0]
                    else:
                        origin = UNITS[2]
                else:
                    origin = row[_CSV_CONTEXT].split('_')[2]
                    level = LEVEL_POLYGON
                if level not in LEVELS:
                    print("Cannot read players' database from CSV: bad stat level {} at row {}".format(level, i))
                    exit(1)
                a['l'] = level
                if origin in UNITS:
                    a['t'] = 'u'
                    a['u'] = origin
                    if len(row[_CSV_ARTEFACT]) > 0 and 'ac' not in a:
                        a['ac'] = [row[_CSV_ARTEFACT], row[_CSV_CHECKSUM], 0.0, 0, 0]
                elif origin in TRADITIONS:
                    a['t'] = 't'
                    a['p'] = origin
                else:
                    print("Cannot read players' database from CSV: bad stat origin {} at row {}".format(origin, i))
                    exit(1)
            elif context.find(_CONTEXT_RESULTS) == 0:
                a['t'] = 'f'
            elif context == _CONTEXT_RESULTS_POLYGON:
                a['t'] = 'p'
            elif context == _CONTEXT_START_PL:
                a['t'] = 'sp'
            elif context == _CONTEXT_FINISH_PL:
                a['t'] = 'fp'
            elif context == _CONTEXT_START_GAME:
                a['t'] = 'sg'
            elif context == _CONTEXT_CLOSE_GAME:
                a['t'] = 'fg'
            elif context == _CONTEXT_OPEN_EDITOR:
                a['t'] = 'se'
            elif context == _CONTEXT_CLOSE_EDITOR:
                a['t'] = 'fe'
            elif context == _CONTEXT_SAVE_PROGRAM:
                a['t'] = 's'
            else:
                print("Cannot read players' database from CSV: unknown context {} at row {}".format(context, i))
                exit(1)                

        if metrics_key == 'creation_index':
            index = int(metrics_value)
            a['c'] = index
            #players[player_id][1][-1][1] = index
        elif 'c' not in a:
            a['c'] = 0

        if metrics_key == 'try' and a['t'] == 'f':
            a['y'] = int(metrics_value)
        elif metrics_key == 'level' and a['t'] == 'f':
            level = int(metrics_value)
            if level < 0 or level >= len(LEVELS):
                print("Cannot read players' database from CSV: bad final level {} at row {}".format(level, i))
                exit(1)
            a['l'] = LEVELS[level]
        elif (metrics_key == 'last_wave' or metrics_key == 'wave') and 'w' not in a:
            a['w'] = int(metrics_value) + 1
        elif metrics_key == 'drone_damage':
            if 'ac' in a:
                a['ac'][2] += metrics_value
        elif metrics_key == 'enemies_destroyed':
            if 'ac' in a:
                a['ac'][3] += int(metrics_value)
        elif metrics_key == 'manual_activation':
            a['ma'] = int(metrics_value)
        elif metrics_key == 'program_activation':
            if 'ac' in a:
                a['ac'][4] += int(metrics_value)            
        elif metrics_key == 'placement_time':
            a['pls_t'] = metrics_value
        elif metrics_key == 'session_time':
            a['gs_t'] = metrics_value
        elif metrics_key == 'editing_time':
            a['es_t'] = metrics_value

    for pl, pl_values in players.items():
        activities, datetable, _ = pl_values
        for a in activities.values():
            datetable.append([a['d'], a['c'], a['i'], a])

    print(i, "lines loaded")
    return players

def read_players_sessions(csv_file, player_filter=None, print_sessions=False, delimiter=','):
    players = read_players_data(csv_file, player_filter, delimiter)
    print('reconstruct sessions...')
    
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

        total_gs = 0.0
        total_pls = 0.0
        total_es = 0.0
        if len(session['gs']) > 0:
            for t in session['gs']:
                total_gs += t
            total_gs /= len(session['gs'])
        else:
            diff = session['fd'] - session['sd']
            if diff < _MAX_SESSION_LENGTH:
                total_gs = diff
        session['avg_gs'] = total_gs
        if len(session['pls']) > 0:
            for t in session['pls']:
                total_pls += t
            total_pls /= len(session['pls'])
        session['avg_pls'] = total_pls
        if len(session['es']) > 0:
            for t in session['es']:
                total_es += t
            total_es /= len(session['es'])
        session['avg_es'] = total_es

    for player, values in players.items():
        activities, datetable, sessions = values

        cur_session = None
        cur_try = 1
        cur_start_game = None
        cur_games = []
        cur_placements = []
        cur_editings = []
        
        for d, cindex, metrics_id, a in sorted(datetable, key = lambda x: (x[1], x[2], x[0])):
            if cindex == 0 and a['v'].find('1.5.3') == 0:
                print('bad creation index for modern AD version: {}', a)
                exit(1)
            act_type = a['t']
            tradition = a['p'] if act_type == 't' else None

            save = 0
            if act_type == 'fp':
                cur_placements.append(a['pls_t'])
            elif act_type == 'sg':
                cur_start_game = d
            elif act_type == 'fg':
                cur_games.append(a['gs_t'])
                cur_start_game = None
            elif act_type == 'fe':
                cur_editings.append(a['es_t'])
            elif act_type == 's':
                save = 1

            if cur_session is not None:
                cur_session['v'].add(a['v'])

            if 'ma' in a:
                manual = a['ma']
            else:
                manual = 0
                
            if act_type in ('f', 'u', 't'):
                level = a['l']
                if 'w' not in a: 
                    continue
                wave = a['w']
                version = a['v']
            
                unit = a['u'] if a['t'] == 'u' else None
                art_cs = a['ac'] if 'ac' in a else None

                if cur_session is not None and wave not in cur_session['ws']:
                    cur_try = 1
                    cur_session['ws'][wave] = {cur_try: [0, 0, 0.0]}
                
                if cur_session is not None and level == cur_session['l'] and wave >= cur_session['w']:
                    if unit is not None:
                        if unit not in cur_session['u']:
                            cur_session['u'].append(unit)
                        if art_cs is not None:
                            cur_session['art'][art_cs[0]] = (unit, art_cs[2], art_cs[3])
                            #else:
                            #    print('program {} is already in session, orig: {}'.format(art_cs[0], cur_session['art'][art_cs[1]]))
                            cur_session['ws'][wave][cur_try][1] += 1
                            if 'wp' not in cur_session:
                                cur_session['wp'] = wave
                        cur_session['ws'][wave][cur_try][0] += 1
                        if 'drone_damage' in a['m']: 
                            cur_session['ws'][wave][cur_try][2] += a['m']['drone_damage']
                        cur_session['ma'] += manual
                    if tradition is not None and cur_session['t'] is None:
                        cur_session['t'] = tradition
                    if act_type == 'f' and a['y'] > cur_try:
                        cur_try += 1
                        cur_session['ws'][wave][cur_try] = [0, 0, 0.0]
                    cur_session['w'] = wave
                    cur_session['a'].append(a)
                    if d > cur_session['fd']:
                        cur_session['fd'] = d
                    cur_session['sa'] += save
                else:
                    if cur_session is not None:
                        cur_session['gs'] = cur_games
                        if cur_start_game is not None:
                            cur_session['gs'].append(cur_session['fd'] - cur_start_game)
                        cur_session['pls'] = cur_placements
                        cur_session['es'] = cur_editings
                        cur_games = []
                        cur_placements = []
                        cur_editings = []
                        avg_sum_session(cur_session)
                        sessions.append(cur_session)

                    cur_try = 1
                    cur_session = {'v': set([a['v']]), 'l': level, 'w': wave, 'ws': {wave: {cur_try: [0, 0, 0.0]}},
                                   'sd': d, 'fd': d, 'smid': metrics_id, 'fmid': metrics_id, 'sidx': cindex, 'fidx': cindex,
                                   'a': [a], 'u': [], 't': tradition, 'art': {}, 'gs': [], 'pls': [], 'es': [], 'sa': save, 'ma': manual}
                    if unit is not None:
                        cur_session['u'].append(unit)
                        cur_session['ws'][wave][cur_try][0] += 1
                        if art_cs is not None:
                            cur_session['art'][art_cs[0]] = (unit, art_cs[2], art_cs[3])
                            cur_session['ws'][wave][cur_try][1] += 1
                            cur_session['wp'] = wave
                        if 'drone_damage' in a['m']:
                            cur_session['ws'][wave][cur_try][2] += a['m']['drone_damage']
            else:
                if cur_session is not None:
                    cur_session['sa'] += save
                    if d > cur_session['fd']:
                        cur_session['fd'] = d
                    if metrics_id > cur_session['fmid']:
                        cur_session['fmid'] = metrics_id
                    if cindex > cur_session['fidx']:
                        cur_session['fidx'] = cindex

        if cur_session is not None:
            cur_session['gs'] = cur_games
            if cur_start_game is not None:
                cur_session['gs'].append(cur_session['fd'] - cur_start_game)
            cur_session['pls'] = cur_placements
            cur_session['es'] = cur_editings
            cur_games = []
            cur_placements = []
            cur_editings = []
            avg_sum_session(cur_session)
            sessions.append(cur_session)

    if print_sessions:
        for player, values in players.items():
            print(player, ':')
            _, _, sessions = values
            for s in sessions:
                print("versions: ({}), level: {}, last wave: {}, waves(tries): {}, date from: {}, to: {}, metrics from: {}, to: {}, cindex from: {}, to: {}, activities: {}, tradition: {}, unit types: ({}), uniq progs: {}, manual use: {}, saves: {}, avg units: {:5.2f}, avg prog percent: {:5.2f}%, avg dmg: {:6.1f}, avg g.s.: {:5.2f}, avg pl.s.: {:5.2f}, avg ed.s.: {:5.2f}".format(
                    ', '.join(sorted(s['v'])),
                    s['l'], s['w'], s['tries'],
                    datetime.datetime.fromtimestamp(s['sd']).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.datetime.fromtimestamp(s['fd']).strftime('%Y-%m-%d %H:%M:%S'),
                    s['smid'], s['fmid'],
                    s['sidx'], s['fidx'],
                    len(s['a']),
                    s['t'],
                    ', '.join(s['u']),
                    len(s['art']),
                    s['ma'], s['sa'],
                    s['avg_u'], s['avg_p'] * 100.0, s['avg_d'],
                    s['avg_gs'], s['avg_pls'], s['avg_es']))

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
    dir_path = os.path.join(PROGRAMS_DIR, unpack_player(player_id))
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
            print('Bad program CyberiadaML file:', filepath)
            continue
        except CyberiadaML.XMLException:
            print('Bad program xml file:', filepath)
            continue
        except CyberiadaML.FileException:
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

def load_players_list(filename):
    players = {}
    with open(filename) as f:
        for line in f.read().splitlines():
            players[line.lower()] = None
    return players

def load_players_date_list(filename):
    players = {}
    with open(filename) as f:
        for line in f.read().splitlines():
            pl_id, date_from, date_to = line.split(',')
            pl_id = pl_id.lower()
            date_pair = (datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S').timestamp(),
                         datetime.datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S').timestamp())
            if pl_id not in players:
                players[pl_id] = [date_pair]
            else:
                players[pl_id].append(date_pair) 
        return players
    return players

def check_isomorphic_programs(unit_program, program, words, diff = False):
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
    
    index = 0
    for n in diff_nodes_flags:
        if n & CyberiadaML.smiNodeDiffFlagTitle:
            node = diff_nodes[index]
            e = program.find_element_by_id(node)
            name = e.get_name()
            if name not in words:
                words[name] = 1
            else:
                words[name] += 1
        index += 1
    for n in new_nodes:
        e = program.find_element_by_id(n)
        name = e.get_name()
        if name not in words:
            words[name] = 1
        else:
            words[name] += 1

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
            name = e.get_name()
            if name == DEFAULT_STATE_NAME:
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
