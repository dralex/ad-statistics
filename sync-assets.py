#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Arena roster files synchronizer
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
import shutil
import subprocess

SOURCE_DIR = 'remote-s3/talent'
ROSTER_TARGET_DIR = 'arena-rosters'
PROGRAMS_TARGET_DIR = 'arena-programs'

ROSTER_EXT = '.zip'
PROGRAM_EXT = '.graphml'

UNZIP_COMMAND = 'unzip'

MAX_SIZE = 1024 * 1024 # 1 MiB

if __name__ == '__main__':

    total_programs = total_rosters = 0
    copied_programs = copied_rosters = 0 
    
    for f in os.listdir(SOURCE_DIR):
        path = os.path.join(SOURCE_DIR, f)
        if f.find(PROGRAM_EXT) > 0:
            total_programs += 1
            target = os.path.join(PROGRAMS_TARGET_DIR)
            if not os.path.exists(target):
                sutils.copyfile(path, target)
                print(f)
                copied_programs += 1
        else:
            pos = f.find(ROSTER_EXT)
            if pos > 0:
                if os.path.getsize(path) > MAX_SIZE:
                    # skip non-roster archives
                    continue
                total_rosters += 1
                asset = f[0:pos]
                target = os.path.join(ROSTER_TARGET_DIR, asset)
                if not os.path.exists(target):
                    print(asset)
                    subprocess.run([UNZIP_COMMAND, path, '-d', target])
                    subproccess.run([RM_COMMAND, '-f', os.path.join(target, '*.jpg')])
                    copied_rosters += 1

    print()
    print('Summary:')
    print('Programs: {} / {}'.format(copied_programs, total_programs))
    print('Rosters: {} / {}'.format(copied_rosters, total_rosters))
