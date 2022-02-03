#!/usr/local/bin/python

###############################################################################
#
# Simple Trello Backup python script
#
# Backups all boards and cards you have access to, including closed boards
# Saves out a single json file with all data
# Warns on attachments - does not download them
#
# This is a simple quick dirty script for my own needs, may use too much memory
# and crash if you a lot of data in trello.
#
# Add your key and token into the cfg below, set the backup path
#
# @author David Tatarata
# @date 2016-11-13
#
# Inspired by mattab/trello-backup, btu didn't want a PHP based solution
#
###############################################################################

import os, urllib2, json, datetime

#
# Config
#
cfg = {
    'trello_key'   : '<insert_your_key_here>',
    'trello_token' : '<insert_your_token_here>'
}

backup_path = '/tmp' # <- change this to where you want the backup path to be

#
# URLs
#
boards_url    = 'https://api.trello.com/1/members/me/boards?&key=%(trello_key)s&token=%(trello_token)s' % cfg
org_url       = 'https://api.trello.com/1/members/me/organizations?&key=%(trello_key)s&token=%(trello_token)s' % cfg
org_board_url = 'https://api.trello.com/1/organizations/%(org_id)s/boards?&key=%(trello_key)s&token=%(trello_token)s'
board_url     = 'https://api.trello.com/1/boards/%(board_id)s?actions=all&actions_limit=1000&card_attachment_fields=all&cards=all&lists=all&members=all&member_fields=all&card_attachment_fields=all&checklists=all&fields=all&key=%(trello_key)s&token=%(trello_token)s'

#
# Code
#
trello_data = {
    'boards' : json.loads(urllib2.urlopen(boards_url).read()),
    'orgs'   : json.loads(urllib2.urlopen(org_url).read()),
    'org_name_lookup' : {},
    'boards_by_org' : {},
    'boards_by_id' : {},
    'board_content_by_id' : {}
}

for org in trello_data['orgs']:
    trello_data['org_name_lookup'][org.get('id')] = org.get('name')

for org_id in trello_data['org_name_lookup']:
    cfg['org_id'] = org_id # Nasty quick hack
    url = org_board_url % cfg
    trello_data['boards_by_org'][org_id] = json.loads(urllib2.urlopen(url).read())

for board in trello_data['boards']:
    board_id = board.get('id')
    trello_data['boards_by_id'][board_id] = board

for org in trello_data['boards_by_org']:
    boards = trello_data['boards_by_org'][org]
    for board in boards:
        board_id = board.get('id')
        trello_data['boards_by_id'][board_id] = board

#
# Backup the board cards
#
board_ids_to_backup = trello_data['boards_by_id'].keys()
count = 1

for board_id in board_ids_to_backup:
    print ' * Backing up [ %s/%s ] %s' % (count, len(board_ids_to_backup), trello_data['boards_by_id'][board_id].get('name'))
    count += 1
    cfg['board_id'] = board_id # Nasty quick hack
    url = board_url % cfg
    trello_data['board_content_by_id'][board_id] = json.loads(urllib2.urlopen(url).read())

    board_action = trello_data['board_content_by_id'][board_id]['actions']
    for action in board_action:
        if 'attachment' in action['data'] and 'url' in action['data']['attachment']:
            print ' |- Not backing up attachment %s in "%s" (%s)' % (action['data']['attachment']['name'], action['data']['card']['name'], action['data']['attachment'].get('url'))

#
# Save the file
#
filenamepath = os.path.join(backup_path, 'trello_backup_%s.json' % datetime.datetime.now().strftime("%Y%m%d_%H%M"))
json.dump(trello_data, open(filenamepath, 'wb'), indent=1)
print 'Saved to ', filenamepath