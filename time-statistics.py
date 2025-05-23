#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Datetime players' activities statistics 
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

def usage():
    print('usage: {} <database.csv> <players-output.csv> <actions-output.csv>'.format(sys.argv[0]))
    exit(1)

def save_csv(fname, data):
    with open(fname, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(data)

if __name__ == '__main__':

    if len(sys.argv) != 4:
        usage()
    
    players_stats, actions_stats = data.read_time_statistics(sys.argv[1])
    pl_output_file = sys.argv[2]
    a_output_file = sys.argv[3]

    save_csv(pl_output_file, sorted(players_stats.items(), key=lambda x: x[0]))
    save_csv(a_output_file, sorted(actions_stats.items(), key=lambda x: x[0]))
