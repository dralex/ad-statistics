#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence: Arena statistics analysis tool
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

import sys
import os
import csv
import json
import datetime
import CyberiadaML

DEFAULT_PROGRAMS_DIR = 'default_arena_programs'
ROSTERS_DIR = 'arena-rosters'
PROGRAMS_DIR = 'arena-programs'
UNITS = ['autoboarder', 'stapler', 'smoker', 'generator']
ROSTER_FILE = 'roster.json'

# Roster CSV file format:

_CSV_ROSTER_ID = 0
_CSV_ASSET_ID = 1
_CSV_PLAYER = 2
_CSV_DATETIME = 3
_CSV_NAME = 4
_CSV_FILE = 5
_CSV_SIZE = 6

DEFAULT_STATE_NAME = 'Состояние'
BASIC_STATE_NAMES = ('Скан', 'Атака', 'Сближение','Бой')
DEBUG_ACTIONS = ('Диод', 'LED')
REPAIR_ACTIONS = ('ЧинитьСебя', 'Self')
OVERDRIVE_ACTIONS = ('СпособностьНаМаксимум', 'Overdrive')
MOVEFROM_ACTIONS = ('ДвигатьсяОтЦели', 'MoveFromTarget')
AD_MODULES = {
    'navi': ('МодульДвижения', 'Navigation'),
    'timer': ('Таймер', 'Timer'),
    'counter': ('Счетчик', 'Counter'),
    'scaner': ('Сенсор', 'Scaner'),
    'analyz': ('АнализаторЦели', 'TargetAnalyser'),
    'self': ('Самодиагностика', 'SelfDiagnostics'),
    'weapon': ('ОружиеЦелевое', 'Weapon'),
    'mass_w': ('ОружиеМассовое', 'MassWeapon'),
    'base': ('СвязьСБазой', 'BaseCom'),
    'diod': ('Диод', 'LED'),
    'repair': ('СпособностьПочинка', 'Repair'),
    'overdr': ('СпособностьНаМаксимум', 'Overdrive'),
    'smoke': ('СтруяДыма', 'Smoke'),
    'charge': ('Зарядка', 'Charger'),
    'deton': ('Самоуничтожение', 'Detonation')
}

def error(s):
    print(s)
    sys.exit(1)

def load_program_path(graph_dir, graph_id):
    # print('Loading program {}...'.format(graph_id))
    try:
        graph_path = os.path.join(graph_dir, graph_id + '.graphml')
        d = CyberiadaML.LocalDocument()
        d.open(graph_path,
               CyberiadaML.formatDetect,
               CyberiadaML.geometryFormatNone,
               False, False, True, True)
        p = CyberiadaML.StateMachine(d.get_state_machines()[0])
        p.set_name('SM')
    except CyberiadaML.CybMLException as e:
        print('Cannot open program {}: {}'.format(graph_path, str(e)))
        return None
    return p

def load_default_programs():
    print('Loading default programs...')
    programs = {}
    program_hashes = {}
    for u in UNITS:
         prg = load_program_path(DEFAULT_PROGRAMS_DIR, u)
         programs[u] = prg
         program_hashes[hash(str(prg))] = u
    return programs, program_hashes

def load_program(graph_dir, graph_id, unit, default_hashes):
    program = load_program_path(graph_dir, graph_id)
    if program is None:
        return None, None
    pstr = str(program)
    phash = hash(pstr)
    if phash in default_hashes:
        return 'def', default_hashes[phash]
    else:
        return pstr, program

def read_roster_files(asset, player_id, default_hashes = {}, uniq_programs = {}):
    the_roster = {}
    asset_dir = os.path.join(ROSTERS_DIR, asset)
    filepath = os.path.join(asset_dir, ROSTER_FILE)
    if os.path.exists(filepath):
        with open(filepath) as f:
            js = json.load(f)
            if 'ID' not in js:
                error('Bad roster JSON {}: no ID'.format(filepath))
            roster_id = js['ID']
            units = []
            pl_uniq_programs = []
            for d in js['DronesPlacement']:
                dtype = d['DroneTypeID']
                if dtype not in UNITS:
                    error('Bad roster JSON {}: unknown drone type {}'.format(filepath, dtype))
                graph = d['GraphID']
                program_string, program = load_program(asset_dir, graph, dtype, default_hashes)
                u = { 'type': dtype }
                if program_string is None:
                    u['default'] = False
                    u['broken'] = True
                elif program_string == 'def':
                    u['default'] = True
                    u['broken'] = False
                else:
                    u['default'] = False
                    u['broken'] = False
                    u['pstr'] = program_string
                    if program_string in uniq_programs:
                        uniq_programs[program_string][3] += 1
                        uniq_programs[program_string][4].add(player_id)
                    else:
                        uniq_programs[program_string] = [dtype, graph, program, 1, set([player_id])]
                    pl_uniq_programs.append(program_string)
                units.append(u)
            if 'assets' not in the_roster:
                the_roster['assets'] = set([asset])
            else:
                the_roster['assets'].add(asset)
            the_roster['units'] = units
            the_roster['programs'] = pl_uniq_programs
    return the_roster

def read_rosters(csv_file, default_hashes = {}, uniq_programs = {}, delimiter=','):
    players = {}
    rosters = 0
    print('read from file {}'.format(csv_file))
    the_file = open(csv_file)
    reader = csv.reader(the_file, delimiter=delimiter)
    i = 0
    for row in reader:
        i += 1
        if len(row) != _CSV_SIZE:
            print("Cannot read players' database from CSV: bad row {}".format(i))
            exit(1)
        if row[_CSV_ASSET_ID] == 'filePathId':
            # skip possible header
            continue
        roster_id = row[_CSV_ROSTER_ID]
        asset = row[_CSV_ASSET_ID]
        player_id = row[_CSV_PLAYER]
        name = row[_CSV_NAME]
        try:
            if row[_CSV_DATETIME].find('.') > 0:
                d = datetime.datetime.strptime(row[_CSV_DATETIME], '%Y-%m-%d %H:%M:%S.%f')
            else:
                d = datetime.datetime.strptime(row[_CSV_DATETIME], '%Y-%m-%d %H:%M:%S')
            d_date = datetime.datetime.strftime(d, '%Y-%m-%d')
            d = d.timestamp()
        except ValueError:
            print("Cannot read players' database from CSV: bad date {} at row {}".format(row[_CSV_DATETIME], i))
            continue
        roster = {
            'last_asset': asset,
            'd': d,
            'dd': d_date,
            'n': name
        }
        asset_data = read_roster_files(asset, player_id, default_hashes, uniq_programs)
        for k, v in asset_data.items():
            roster[k] = v
        if player_id not in players:
            players[player_id] = {}
        players[player_id][roster_id] = roster
        rosters += 1
        
    the_file.close()
    print('{} lines, {} players, {} rosters loaded'.format(i, len(players), rosters))

    return players

def check_isomorphic_programs(unit_program, program, diff = False):
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
        empty_new_nodes = 0
        new_edged_nodes_link = 0
        
        diod_flag = False
        repair_flag = False
        overdrive_flag = False
        movefrom_flag = False
        for nid in diff_nodes2 + new_nodes:
            n = program.find_element_by_id(nid)
            if n.get_type() != CyberiadaML.elementSimpleState and n.get_type() != CyberiadaML.elementCompositeState:
                continue
            for a in n.get_actions():
                if a.has_behavior():
                    behav = a.get_behavior()
                    if not diod_flag:
                        for d in DEBUG_ACTIONS:
                            if behav.find(d) >= 0:
                                diod_flag = True
                                break
                    if not repair_flag:
                        for d in REPAIR_ACTIONS:
                            if behav.find(d) >= 0:
                                repair_flag = True
                                break
                    if not overdrive_flag:
                        for d in OVERDRIVE_ACTIONS:
                            if behav.find(d) >= 0:
                                overdrive_flag = True
                                break
                    if not movefrom_flag:
                        for d in MOVEFROM_ACTIONS:
                            if behav.find(d) >= 0:
                                movefrom_flag = True
                                break
                            
        if not diod_flag or not repair_flag or not overdrive_flag or not movefrom_flag:
            for e in program.find_elements_by_type(CyberiadaML.elementTransition):
                if e.has_action():
                    a = e.get_action()
                    if a.has_behavior():
                        behav = a.get_behavior()
                        if not diod_flag:
                            for d in DEBUG_ACTIONS:
                                if behav.find(d) >= 0:
                                    diod_flag = True
                                    break
                        if not repair_flag:
                            for d in REPAIR_ACTIONS:
                                if behav.find(d) >= 0:
                                    repair_flag = True
                                    break
                        if not overdrive_flag:
                            for d in OVERDRIVE_ACTIONS:
                                if behav.find(d) >= 0:
                                    overdrive_flag = True
                                    break
                        if not movefrom_flag:
                            for d in MOVEFROM_ACTIONS:
                                if behav.find(d) >= 0:
                                    movefrom_flag = True
                                    break

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

        new_node_flags = {}
        for n in new_nodes:
            e = program.find_element_by_id(n)
            name = e.get_name()
            if name == DEFAULT_STATE_NAME:
                default_names += 1
            elif len(name) == 0:
                empty_names += 1
            elif name not in BASIC_STATE_NAMES:
                nontrivial_names += 1
            if not e.has_actions():
                empty_new_nodes += 1
            else:
                for m, names in AD_MODULES.items():
                    for name in names:
                        for a in e.get_actions():
                            if a.has_behavior() and a.get_behavior().find(name) >= 0:
                                new_node_flags[m] = True

        edge_to_new_node_event_flags = {}
        for _id in new_edges:
            e = program.find_element_by_id(_id)
            source_id = e.get_source_element_id()
            target_id = e.get_target_element_id()
            if source_id in new_nodes or target_id in new_nodes:
                new_edged_nodes_link += 1
            if target_id in new_nodes and e.has_action():
                trigger = e.get_action().get_trigger()
                for m, names in AD_MODULES.items():
                    for name in names:
                        if trigger.find(name) >= 0:
                            edge_to_new_node_event_flags[m] = True
                            
        results =  {'isomorphic to default': res == CyberiadaML.smiIsomorphic,
                    'extended default': ((len(new_nodes) > 0 or len(new_edges) > 0) and
                                         len(missing_nodes) == 0 and len(missing_edges) == 0),
                    'new nodes': len(new_nodes) > 0,
                    'single new node': len(new_nodes) == 1,
                    'empty new nodes': empty_new_nodes > 0,
                    'single empty new node': empty_new_nodes == 1,
                    'new nodes with default state name': default_names > 0,
                    'single new node with default state name': len(new_nodes) == 1 and default_names > 0,
                    'new nodes with empty state name': empty_names > 0,
                    'missing nodes': len(missing_nodes) > 0,
                    'detached nodes': (len(new_nodes) > 0 and len(missing_nodes) == 0 and
                                       len(missing_edges) == 0 and len(new_edges) == 0),
                    'new nodes and edges linked': new_edged_nodes_link > 0,
                    'diff names': diff_names > 0,
                    'non-trivial names': nontrivial_names > 0,
                    'debug actions': diod_flag,
                    'repair actions': repair_flag,
                    'overdrive actions': overdrive_flag,
                    'movefrom actions': movefrom_flag,
                    'diff actions': diff_actions > 0,
                    'single diff action': diff_actions == 1,
                    'diff edges': len(diff_edges2) > 0,
                    'single diff edge': len(diff_edges2) == 1,
                    'new edges': len(new_edges) > 0,
                    'single new edge': len(new_edges) == 1,
                    'missing edges': len(missing_edges) > 0,
                    'diff actions args': diff_actions_args > 0,
                    'diff actions order': diff_actions_order > 0,
                    'diff actions num': diff_actions_num > 0}

        for m in new_node_flags:
            results['new nodes with {} module'.format(m)] = True
        for m in edge_to_new_node_event_flags:
            results['new nodes and edges linked with {} event'.format(m)] = True

        return results
