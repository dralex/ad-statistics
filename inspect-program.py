#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Program inspector
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
import data
import CyberiadaML

def usage(msg = ''):
    print("Usage: {} <unit-type> <artefact-id>".format(sys.argv[0]))
    if msg:
        print(msg)
    exit(1)            

if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage()

    unit_type = sys.argv[1]
    if unit_type not in data.UNITS:
        usage('Bad unit type {}'.format(unit_type))
    program = data.load_program(sys.argv[2])
    if program is None:
        usage('Cannot load program')
    units = data.load_default_programs()
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
    isom_stats = data.check_isomorphic_programs(units[unit_type], program, True)
    nodes_to_print = []
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
            print("{:20}: {}".format(key, value))

    print()
    for n in nodes_to_print:
        node = program.find_element_by_id(n)
        print('Node {}: {}'.format(n, node))
