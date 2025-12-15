#!/usr/bin/python3
# -----------------------------------------------------------------------------
#  The Berloga Apiary Defence statistics analysis tool
# 
#  Programs archive collector
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
import urllib.request
import data

FILTER_PLAYERS_FILE = None #'select_players.txt'
FILTER_PLAYERS = None # ['player-id-1', 'player-id-2']
ARTEFACT_URL = 'https://storage.yandexcloud.net/berloga-artefacts/{}/{}.xml'

Hashes = {}

def download_artefact(player_id, artefact):

    if not os.path.isdir(data.PROGRAMS_DIR):
        os.mkdir(data.PROGRAMS_DIR)
    player_dir = os.path.join(data.PROGRAMS_DIR, player_id)
    if not os.path.isdir(player_dir):
        os.mkdir(player_dir)

    artefact_id, checksum, _, _, _ = artefact 

    if checksum not in Hashes:
        Hashes[checksum] = (player_id, artefact_id)
        artefact_file = data.get_artefact_file(player_id, artefact_id)
        if not os.path.isfile(artefact_file):
            path = ARTEFACT_URL.format(player_id, artefact_id)
            print('downloading {}...'.format(path), end='')
            try: 
                artefact = urllib.request.urlopen(path)
                with open(artefact_file, 'wb') as output:
                    output.write(artefact.read())
                print(' done')
            except urllib.error.HTTPError:
                print(' FAILED!')
    else:
        old_player_id, old_artefact_id = Hashes[checksum]
        link_from = os.path.abspath(data.get_artefact_file(old_player_id, old_artefact_id))
        link_to = os.path.abspath(data.get_artefact_file(player_id, artefact_id))
        if os.path.isfile(link_from) and not os.path.islink(link_to) and not os.path.isfile(link_to):
            print('link {} -> {}'.format(link_from, link_to))
            os.symlink(link_from, link_to)

if __name__ == '__main__':
    if FILTER_PLAYERS_FILE:
        with open(FILTER_PLAYERS_FILE) as f:
            Players_filter = set(f.read().splitlines())
    else:
        Players_filter = None

    if FILTER_PLAYERS is not None:
        Filter = FILTER_PLAYERS
    elif FILTER_PLAYERS_FILE is not None:
        Filter = Players_filter
    else:
        Filter = None


    for i, players_data in enumerate(sys.argv):
        if i == 0:
            continue
        
        Players = data.read_players_data(players_data, Filter)
        p_size = len(Players)
        i = 0
        for player, d in Players.items():
            if FILTER_PLAYERS is not None and player not in FILTER_PLAYERS:
                continue
            if Players_filter and player not in Players_filter:
                continue
            i += 1
            if i % 10 == 0:
                print('Collected {} of {}'.format(i, p_size))
            activities = d[0]
            for a in activities.values():
                if 'ac' in a:
                    artefact = a['ac']
                    if artefact:
                        download_artefact(player, artefact)
