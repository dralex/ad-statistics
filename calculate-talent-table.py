#!/usr/bin/python3

import sys
import csv
import data

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print('usage: {} <database.csv> <talent-table.csv>')
        exit(1)

    DB_FILE = sys.argv[1]
    TALENT_FILE = sys.argv[2]
        
    Talents = {}
    Players_talents = {}
    Player_filter = {}

    Hist_regions = {}
    Hist_towns = {}
    Hist_sex = {}
    Hist_class = {}
    
    reader = csv.reader(open(TALENT_FILE), delimiter=',')
    for row in reader:
        if len(row) != 7:
            continue
        talent_id, name, town, region, sex, cls, player_id = row

        if talent_id not in Talents:
            Talents[talent_id] = {'n': name, 's': sex, 'c': cls, 'r': region, 't': town, 'p': {player_id: None}}
            if region not in Hist_regions:
                Hist_regions[region] = 1
            else:
                Hist_regions[region] += 1
            if town not in Hist_towns:
                Hist_towns[town] = 1
            else:
                Hist_towns[town] += 1
            if sex not in Hist_sex:
                Hist_sex[sex] = 1
            else:
                Hist_sex[sex] += 1
            if cls not in Hist_class:
                Hist_class[cls] = 1
            else:
                Hist_class[cls] += 1
        else:
            Talents[talent_id]['p'][player_id] = None
        Players_talents[player_id] = talent_id
        Player_filter[player_id] = None

    print('Total persons: {}'.format(len(Talents)))
    print('Total player ids: {}'.format(len(Player_filter)))
    print()
    print('Regions distribution ({:3}):'.format(len(Hist_regions)))
    print('-----------------------------')
    for l, v in sorted(Hist_regions.items(), key=(lambda x: x[1]), reverse=True):
        print(l, v)
    print()
    print('Towns distribution:')
    print('-------------------')
    for l, v in sorted(Hist_towns.items(), key = (lambda x: x[1]), reverse=True):
        print(l, v)
    print()
    print('Sex distribution:')
    print('-----------------')
    for l, v in sorted(Hist_sex.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    print('Class distribution:')
    print('------------------')
    for l, v in sorted(Hist_class.items(), key = (lambda x: x[0])):
        print(l, v)
    print()
    
    Players = data.read_players_sessions(DB_FILE, Player_filter, False)

    for player, values in Players.items():        
        _, _, sessions = values
        talent_id = Players_talents[player]
        Talents[talent_id]['p'][player] = sessions

    to_remove = []
    print()
    print('Multi-player persons:')
    print('---------------------')
    for talent_id, t in Talents.items():
        if len(t['p']) > 1:
            print('Talent ID: {} Multiple sessions:'.format(talent_id))
            max_sessions = 0
            max_sessions_player_id = None
            for p in t['p']:
                if t['p'][p] is not None:
                    sessions_num = len(t['p'][p])
                    print('\tPlayer ID: {} Sessions: {}'.format(p, sessions_num))
                    if sessions_num > max_sessions:
                        max_sessions = sessions_num
                        max_sessions_player_id = p
            for p in t['p']:
                if p != max_sessions_player_id:
                    to_remove.append(p)
        elif len(t['p']) == 1:
            p, pvalue = next(iter(t['p'].items()))
            if pvalue is None:
                print('Talent ID: {} No sessions!'.format(talent_id))
                to_remove.append(p)

    print()
    print('Player IDs to remove:')
    print('---------------------')
    for p in sorted(to_remove):
        print(p)

