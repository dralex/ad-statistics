#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  The program inspector
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
    print("Usage: {} <unit-type> <artefact-id> [<new>]".format(sys.argv[0]))
    if msg:
        print(msg)
    exit(1)            

if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage()

    new_units = False
    if len(sys.argv) == 4:
        if sys.argv[3] == 'new':
            new_units = True
        else:
            usage()

    unit_type = sys.argv[1]
    if unit_type not in data.UNITS:
        usage('Bad unit type {}'.format(unit_type))
    program = data.load_program(sys.argv[2])
    if program is None:
        usage('Cannot load program')
    units = data.load_default_programs(new_units)
    data.inspect_program(unit_type, units, program)
    print()
    print('The program:')
    print(str(program))

