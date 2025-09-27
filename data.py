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
NEW_VERSION = '1.6'
PROGRAMS_DIR = 'programs'
LAST_WAVE_METRICS = 'last_wave'
LEVEL_START = 'Start'
LEVEL_INFINITY = 'Infinity'
LEVEL_POLYGON = 'Polygon'
LEVELS = [LEVEL_START, '1', '2', '3', LEVEL_INFINITY, LEVEL_POLYGON]
UNITS = ['Autoborder', 'Stapler', 'Smoker', 'Generator']
TRADITIONS = ['Constructor', 'Beekeeper', 'Programmer']
DEFAULT_STATE_NAME = 'Состояние'
BASIC_STATE_NAMES = ('Скан', 'Атака', 'Сближение','Бой')
DEBUG_ACTION = 'Диод'

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

def pack_player(player, idx):
    return "{}:{}".format(player, idx)
def unpack_player(player):
    if player.find(':') > 0:
        return player.split(':')[0]
    else:
        return player

def read_players_data(csv_file, player_filter = None, blacklist_filter = None, delimiter=','):
    players = {}
    print('read from file {}'.format(csv_file))
    the_file = open(csv_file)
    reader = csv.reader(the_file, delimiter=delimiter)
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

        player_id = row[_CSV_PLAYER]
        if player_filter: 
            if player_id not in player_filter:
                continue
        if blacklist_filter: 
            if player_id in blacklist_filter:
                continue

        try:
            if row[_CSV_DATETIME].find('.') > 0:
                d = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f+03')
            else:
                d = datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S+03')
            d_pydate = d
            d_date = datetime.datetime.strftime(d, '%Y-%m-%d')
            d = d.timestamp()
        except ValueError:
            print("Cannot read players' database from CSV: bad data {} at row {}".format(row[_CSV_DATETIME], i))
            continue

        activity_id = row[_CSV_ID]

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
            a['ddate'] = d_date
            a['dpydate'] = d_pydate
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
                print("Bad final level {} at row {}".format(level, i))
                level = len(LEVELS) - 1
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
            
    # split multi-players
    if player_filter:
        to_delete = set([])
        to_add = {}
        for pl, pl_values in players.items():
            if player_filter[pl] is None:
                continue
            for indexes in player_filter[pl]:
                if indexes is None: continue
                first_index, last_index = indexes
                activities, _, _ = pl_values
                for aid, a in activities.items():
                    if first_index <= a['c'] <= last_index:
                        new_player = pack_player(pl, first_index)
                        to_delete.add(pl)
                        if new_player not in to_add:
                            to_add[new_player] = {}
                        to_add[new_player][aid] = a
        for p in to_delete:
            del players[p]
        for p, v in to_add.items():
            players[p] = (v, [], [])
    the_file.close()

    # build date table
    for pl, pl_values in players.items():
        activities, datetable, _ = pl_values
        for a in activities.values():
            datetable.append([a['d'], a['c'], a['i'], a])

    print(i, "lines loaded")
    return players

def read_players_sessions(csv_file, player_filter=None, print_sessions=False, delimiter=','):
    players = read_players_data(csv_file, player_filter, None, delimiter)
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
        session['avg_es'] = 0.0
        if len(session['es']) > 0:
            total_es = sum(session['es'])
            session['avg_es'] = total_es / len(session['es'])
        session['edits'] = total_es
        session['avg_pls'] = 0.0
        if len(session['pls']) > 0:
            total_pls = sum(session['pls'])
            session['avg_pls'] = total_pls / len(session['pls'])
        session['places'] = total_pls - total_es

    for player, values in players.items():
        activities, datetable, sessions = values

        cur_session = None
        cur_try = 1
        cur_start_game = None
        cur_games = []
        cur_placements = []
        cur_editings = []
        pre_sd = pre_smid = pre_sidx = None

        for d, cindex, metrics_id, a in sorted(datetable, key = lambda x: (x[1], x[2], x[0])):
            if cindex == 0 and a['v'].find('1.5.3') == 0:
                print('bad creation index for modern AD version: {}', a)
                exit(1)
            act_type = a['t']
            tradition = a['p'] if act_type == 't' else None

            save = 0
            if act_type in ('fp', 'sg', 'fg', 'fe', 's'):
                
                if pre_sd is None:
                    pre_sd = d
                if pre_smid is None:
                    pre_smid = metrics_id
                if pre_sidx is None:
                    pre_sidx = cindex

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
                            cur_session['art'][art_cs[0]] = (unit, art_cs[2], art_cs[3], d, version)
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

                    if len(sessions) > 0:
                        pre_sd = d
                        pre_smid = metrics_id
                        pre_sidx = cindex
                    cur_try = 1
                    cur_session = {'v': set([a['v']]), 'l': level, 'w': wave, 'ws': {wave: {cur_try: [0, 0, 0.0]}},
                                   'sd': d if pre_sd is None else pre_sd, 'fd': d,
                                   'smid': metrics_id if pre_smid is None else pre_smid, 'fmid': metrics_id,
                                   'sidx': cindex if pre_sidx is None else pre_sidx, 'fidx': cindex,
                                   'a': [a], 'u': [], 't': tradition, 'art': {}, 'gs': [], 'pls': [], 'es': [], 'sa': save, 'ma': manual}
                    if unit is not None:
                        cur_session['u'].append(unit)
                        cur_session['ws'][wave][cur_try][0] += 1
                        if art_cs is not None:
                            cur_session['art'][art_cs[0]] = (unit, art_cs[2], art_cs[3], d)
                            cur_session['ws'][wave][cur_try][1] += 1
                            cur_session['wp'] = wave
                        if 'drone_damage' in a['m']:
                            cur_session['ws'][wave][cur_try][2] += a['m']['drone_damage']
            else:
                if cur_session is not None:
                    cur_session['sa'] += save
                    save = 0
                    if d > cur_session['fd']:
                        cur_session['fd'] = d
                    if metrics_id > cur_session['fmid']:
                        cur_session['fmid'] = metrics_id
                    if cindex > cur_session['fidx']:
                        cur_session['fidx'] = cindex

        if cur_session is not None:
            cur_session['sa'] += save
            save = 0
            if d > cur_session['fd']:
                cur_session['fd'] = d
            if metrics_id > cur_session['fmid']:
                cur_session['fmid'] = metrics_id
            if cindex > cur_session['fidx']:
                cur_session['fidx'] = cindex
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
                print("versions: ({}), level: {}, last wave: {}, waves(tries): {}, date from: {}, to: {}, metrics from: {}, to: {}, cindex from: {}, to: {}, activities: {}, tradition: {}, unit types: ({}), units: {}, pr.units: {}, uniq progs: {}, manual use: {}, saves: {}, avg units: {:5.2f}, avg prog percent: {:5.2f}%, avg dmg: {:6.1f}, avg g.s.: {:5.2f}, avg pl.s.: {:5.2f}, avg ed.s.: {:5.2f}, pls: {:6.2f}, eds: {:6.2f}".format(
                    ', '.join(sorted(s['v'])),
                    s['l'], s['w'], s['tries'],
                    datetime.datetime.fromtimestamp(s['sd']).strftime('%Y-%m-%d %H:%M:%S'),
                    datetime.datetime.fromtimestamp(s['fd']).strftime('%Y-%m-%d %H:%M:%S'),
                    s['smid'], s['fmid'],
                    s['sidx'], s['fidx'],
                    len(s['a']),
                    s['t'],
                    ', '.join(s['u']),
                    s['units'], s['punits'],
                    len(s['art']),
                    s['ma'], s['sa'],
                    s['avg_u'], s['avg_p'] * 100.0, s['avg_d'],
                    s['avg_gs'], s['avg_pls'], s['avg_es'],
                    s['places'], s['edits']))

    return players

def read_time_statistics(csv_file, player_filter=None):
    players = read_players_data(csv_file, player_filter)

    players_stats = {}
    actions_stats = {}

    for player, values in players.items():
        activities, _, _ = values
        for a in activities.values():
            d = a['ddate']
            if d not in players_stats:
                players_stats[d] = set([player])
            else:
                players_stats[d].add(player)
            if d not in actions_stats:
                actions_stats[d] = 1
            else:
                actions_stats[d] += 1
    for d, v in players_stats.items():
        players_stats[d] = len(v)

    return players_stats, actions_stats

def load_default_programs(version = False):
    print('Loading default programs {}...'.format(NEW_VERSION if version else ''))
    programs = {}
    if version:
        default_programs_dir = os.path.join(DEFAULT_PROGRAMS_DIR, NEW_VERSION)
    else:
        default_programs_dir = DEFAULT_PROGRAMS_DIR
    for u in UNITS:
        d = CyberiadaML.LocalDocument()
        d.open(os.path.join(default_programs_dir, u + '.graphml'),
               CyberiadaML.formatDetect,
               CyberiadaML.geometryFormatNone,
               False, False, True)
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
            d.open(filepath, CyberiadaML.formatDetect, CyberiadaML.geometryFormatNone, False, False, True)
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
            d.open(filepath, CyberiadaML.formatDetect, CyberiadaML.geometryFormatNone, False, False, True)
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

def load_players_index_list(filename):
    players = {}
    with open(filename) as f:
        for line in f.read().splitlines():
            if line.find(',') > 0:
                pl_id, index_from, index_to = line.split(',')
                index_pair = (int(index_from), int(index_to))
            else:
                pl_id = line
                index_pair = None
            pl_id = pl_id.lower()
            if pl_id not in players:
                players[pl_id] = [index_pair]
            else:
                players[pl_id].append(index_pair)
    return players

def check_isomorphic_programs(unit_program, program, words = None, diff = False):
    initial = ''
    diff_nodes1 = []
    diff_nodes2 = []
    diff_nodes_flags = []
    new_nodes = []
    missing_nodes = []
    diff_edges1 = []
    diff_edges2 = []
    diff_edges_flags = []
    new_edges = []
    missing_edges = []
    res = unit_program.check_isomorphism(program, True, False, initial,
					 diff_nodes1, diff_nodes2, diff_nodes_flags, new_nodes, missing_nodes,
					 diff_edges1, diff_edges2, diff_edges_flags, new_edges, missing_edges)
    if words is not None:
        index = 0
        for n in diff_nodes_flags:
            if n & CyberiadaML.smiNodeDiffFlagTitle:
                node = diff_nodes2[index]
                e = program.find_element_by_id(node)
                name = e.get_name()
                if len(name) == 0 and e.get_type() == CyberiadaML.elementInitial:
                    # initial node
                    continue
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

    diod_flag = False
    for nid in diff_nodes2 + new_nodes:
        if diod_flag: break
        n = program.find_element_by_id(nid)
        if n.get_type() != CyberiadaML.elementSimpleState and n.get_type() != CyberiadaML.elementCompositeState:
            continue
        for a in n.get_actions():
            if a.has_behavior():
                behav = a.get_behavior()
                if behav.find(DEBUG_ACTION) > 0:
                    diod_flag = True
                    break
    if not diod_flag:
        for e in program.find_elements_by_type(CyberiadaML.elementTransition):
            if e.has_action():
                a = e.get_action()
                if a.has_behavior():
                    behav = a.get_behavior()
                    if behav.find(DEBUG_ACTION) > 0:
                        diod_flag = True
                        break
    if diff:
        diff_arrays = {}
        diff_arrays['res'] = res
        diff_arrays['diff_nodes_orig'] = diff_nodes1
        diff_arrays['diff_nodes'] = diff_nodes2
        diff_arrays['diff_nodes_flags'] = diff_nodes_flags
        diff_arrays['new_nodes'] = new_nodes
        diff_arrays['missing_nodes'] = missing_nodes
        diff_arrays['diff_edges_orig'] = diff_edges1
        diff_arrays['diff_edges'] = diff_edges2
        diff_arrays['diff_edges_flags'] = diff_edges_flags
        diff_arrays['new_edges'] = new_edges
        diff_arrays['missing_edges'] = missing_edges
        return diff_arrays
    else:
        diff_names = 0
        diff_actions = 0
        diff_actions_num = 0
        diff_actions_args = 0
        diff_actions_order = 0
        default_names = 0
        empty_names = 0
        nontrivial_names = 0
        for i, f in enumerate(diff_nodes_flags):
            if f & CyberiadaML.smiNodeDiffFlagTitle:
                diff_names += 1
            if f & CyberiadaML.smiNodeDiffFlagActions:
                diff_actions += 1
                id1 = diff_nodes1[i]
                node1 = unit_program.find_element_by_id(id1)
                id2 = diff_nodes2[i]
                node2 = program.find_element_by_id(id2)
                f2 = node1.compare_actions(node2)
                if f2 != 0:
                    if f2 & CyberiadaML.adiffArguments: diff_actions_args += 1
                    if f2 & CyberiadaML.adiffOrder: diff_actions_order += 1
                    if f2 & CyberiadaML.adiffNumber: diff_actions_num += 1

        for n in new_nodes:
            e = program.find_element_by_id(n)
            name = e.get_name()
            if name == DEFAULT_STATE_NAME:
                default_names += 1
            elif len(name) == 0:
                empty_names += 1
            elif name not in BASIC_STATE_NAMES:
                nontrivial_names += 1

        return {'isomorphic to default': res == CyberiadaML.smiIsomorphic,
                'extended default': ((len(new_nodes) > 0 or len(new_edges) > 0 or diff_actions > 0) and
                                     len(missing_nodes) == 0 and len(missing_edges) == 0),
                'new nodes': len(new_nodes) > 0,
                'new nodes with default state name': default_names > 0,
                'new nodes with empty state name': empty_names > 0,
                'missing nodes': len(missing_nodes) > 0,
                'detached nodes': (len(new_nodes) > 0 and len(missing_nodes) == 0 and
                                   len(missing_edges) == 0 and len(new_edges) == 0),
                'diff names': diff_names > 0,
                'non-trivial names': nontrivial_names > 0,
                'debug actions': diod_flag,
                'diff actions': diff_actions > 0,
                'diff edges': len(diff_edges2) > 0,
                'new edges': len(new_edges) > 0,
                'missing edges': len(missing_edges) > 0,
                'diff actions args': diff_actions_args > 0,
                'diff actions order': diff_actions_order > 0,
                'diff actions num': diff_actions_num > 0}

def inspect_program(unit_type, default_units, program):
    isom_results = (CyberiadaML.smiIdentical,
		    CyberiadaML.smiEqual,
		    CyberiadaML.smiIsomorphic,
		    CyberiadaML.smiDiffStates,
		    CyberiadaML.smiDiffInitial,
		    CyberiadaML.smiDiffEdges)
    diff_flags = (CyberiadaML.smiNodeDiffFlagID,
		  CyberiadaML.smiNodeDiffFlagType,
		  CyberiadaML.smiNodeDiffFlagTitle,
		  CyberiadaML.smiNodeDiffFlagActions,
		  CyberiadaML.smiNodeDiffFlagSMLink,
		  CyberiadaML.smiNodeDiffFlagChildren,
		  CyberiadaML.smiNodeDiffFlagEdges,
		  CyberiadaML.smiEdgeDiffFlagID,
		  CyberiadaML.smiEdgeDiffFlagAction)
    words = {}
    default_program = default_units[unit_type]
    isom_stats = check_isomorphic_programs(default_program, program, words, True)
    nodes_to_print = []
    edges_to_print = []
    diff_nodes_to_print = []
    for key,value in isom_stats.items():
        if key == 'res':
            flags = []
            if value & CyberiadaML.smiIdentical:
                flags.append('identical')
            if value & CyberiadaML.smiEqual:
                flags.append('equal')
            if value & CyberiadaML.smiIsomorphic:
                flags.append('isomorphic')
            if value & CyberiadaML.smiDiffStates:
                flags.append('diff states')
            if value & CyberiadaML.smiDiffInitial:
                flags.append('diff initial')
            if value & CyberiadaML.smiDiffEdges:
                flags.append('diff edges')
            print("{:20}: {}".format('Flags:', ', '.join(flags)))
        elif key.find('flags') > 0:
            flags = []
            for v in value:
                if v & CyberiadaML.smiNodeDiffFlagID:
                    flags.append('id')
                if v & CyberiadaML.smiNodeDiffFlagType:
                    flags.append('type')
                if v & CyberiadaML.smiNodeDiffFlagTitle:
                    flags.append('title')
                if v & CyberiadaML.smiNodeDiffFlagActions:
                    flags.append('actions')
                if v & CyberiadaML.smiNodeDiffFlagSMLink:
                    flags.append('sm link')
                if v & CyberiadaML.smiNodeDiffFlagChildren:
                    flags.append('children')
                if v & CyberiadaML.smiNodeDiffFlagEdges:
                    flags.append('edges')
                if v & CyberiadaML.smiEdgeDiffFlagID:
                    flags.append('id')
                if v & CyberiadaML.smiEdgeDiffFlagAction:
                    flags.append('action')
            print("{:20}: {}".format(key, flags))
        else:
            if key.find('node') > 0:
                nodes_to_print += value
            if key.find('edge') > 0:
                edges_to_print += value
            print("{:20}: {}".format(key, value))

    diff_node_actions = []
    for i,flags in enumerate(isom_stats['diff_nodes_flags']):
         if flags & CyberiadaML.smiNodeDiffFlagActions:
             id1 = isom_stats['diff_nodes_orig'][i]
             node1 = default_program.find_element_by_id(id1)
             id2 = isom_stats['diff_nodes'][i]
             node2 = program.find_element_by_id(id2)
             f = node1.compare_actions(node2)
             if f != 0:
                 diff_string = ''
                 if f & CyberiadaML.adiffArguments: diff_string += 'a'
                 if f & CyberiadaML.adiffOrder: diff_string += 'O'
                 if f & CyberiadaML.adiffGuards: diff_string += 'G'
                 if f & CyberiadaML.adiffActions: diff_string += 'A'
                 if f & CyberiadaML.adiffNumber: diff_string += 'N'
                 if f & CyberiadaML.adiffTypes: diff_string += 'T'
                 diff_node_actions.append((diff_string, node1, node2))

    diff_edge_actions = []
    for i,flags in enumerate(isom_stats['diff_edges_flags']):
         if flags & CyberiadaML.smiEdgeDiffFlagAction:
             id1 = isom_stats['diff_edges_orig'][i]
             edge1 = default_program.find_element_by_id(id1)
             id2 = isom_stats['diff_edges'][i]
             edge2 = program.find_element_by_id(id2)
             f = edge1.compare_actions(edge2)
             if f != 0:
                 diff_string = ''
                 if f & CyberiadaML.adiffArguments: diff_string += 'a'
                 if f & CyberiadaML.adiffOrder: diff_string += 'O'
                 if f & CyberiadaML.adiffGuards: diff_string += 'G'
                 if f & CyberiadaML.adiffActions: diff_string += 'A'
                 if f & CyberiadaML.adiffNumber: diff_string += 'N'
                 if f & CyberiadaML.adiffTypes: diff_string += 'T'
                 diff_edge_actions.append((diff_string, edge1, edge2))
                 
    print()
    print('Popular state names:')
    for k, v in sorted(words.items(), key=lambda x: x[1], reverse=True):
        print(k, v)
    print()
    for n in nodes_to_print:
        node = program.find_element_by_id(n)
        print('Node {}: {}'.format(n, node))
    print()
    for f, node1, node2 in diff_node_actions:
        print('Node diff actions {}:\n{}\n{}'.format(f, node1, node2))
    print()
    for e in edges_to_print:
        edge = program.find_element_by_id(e)
        print('Edge {}: {}'.format(e, edge))
    print()
    for f, edge1, edge2 in diff_edge_actions:
        print('Edge diff actions {}:\n{}\n{}'.format(f, edge1, edge2))
