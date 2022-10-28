#!/usr/bin/python3
import sys
import json
import yaml
from datetime import datetime, timedelta
import api_helper as api

CONFIG_FILE = 'config.yml'

with open(CONFIG_FILE, 'r') as stream:
    config_file = yaml.load(stream, Loader=yaml.Loader)

source = config_file['source_account']
destination = config_file['destination_account']


def parse_config(config, name):
    url = config['url']
    user = config['username']
    password = config['password']
    task_list_id = None
    # task_list_id is optional
    if 'task_list_id' in config:
        task_list_id = config['task_list_id']
    return url, user, password, task_list_id


# By default, we sync the timelogs for today
today = datetime.today().strftime('%Y-%m-%d')
yesterday = (datetime.today() - timedelta(1)).strftime('%Y-%m-%d')

# TODO: also add a custom date range.
from_date, to_date = today, today
if len(sys.argv) > 1:
    if sys.argv[1] == '--yesterday':
        from_date, to_date = yesterday, yesterday

print('[INFO] Syncing timelogs from ' + from_date + ' to ' + to_date)
# Source
source_name = list(source.keys())[0]
source_url, source_user, source_pass, _ = parse_config(source, source_name)
source_user_id = api.get_user_id(source_url, source_user, source_pass)
source_timelogs = api.get_timelogs(source_url, source_user, source_pass, source_user_id, from_date, to_date)

# Destination
dest_name = list(destination.keys())[0]
dest_url, dest_user, dest_pass, dest_tlid = parse_config(destination, dest_name)
dest_user_id = api.get_user_id(dest_url, dest_user, dest_pass)
dest_timelogs = api.get_timelogs(dest_url, dest_user, dest_pass, dest_user_id, from_date, to_date)

dest_task_list = api.get_task_list(dest_url, dest_user, dest_pass, dest_user_id)

logs_count = 0
for st in source_timelogs:
    timelog_exists = False
    source_task_name = st['todo-item-name']

    # First check if the timelog already exists in the destination
    for dt in dest_timelogs:
        if (dt['todo-item-name'] == source_task_name
                and dt['date'] == st['date']
                and dt['hours'] == st['hours']
                and dt['minutes'] == st['minutes']):
            timelog_exists = True

    if not timelog_exists:
        # The date should be in the YYYYMMDD, and time in HH:MM format,
        # parse them from the datetime string.
        task_id = dest_task_list.get(source_task_name)
        date_time = st['dateUserPerspective'].replace('-', '')
        datetime_split = date_time.split('T')
        date = datetime_split[0]
        time = datetime_split[1][:-4]

        to_time = datetime.strptime(time, '%H:%M') + timedelta(hours=(int(st['hours'])), minutes=(int(st['minutes'])))
        to_time_str = str(to_time.hour) + ':' + str(to_time.minute)

        timelog_post_data = json.dumps({
            'time-entry': {
                'description': st['description'],
                'person-id': dest_user_id,
                'date': date,
                'time': time,
                'hours': st['hours'],
                'minutes': st['minutes'],
                'isbillable': True
            }
        })

        # If the task exists in the destination add the timelog, else create the task and add the timelog then
        if dest_task_list.get(source_task_name) is not None:
            if api.log_time(dest_url, task_id, timelog_post_data, dest_user, dest_pass) == 'OK':
                logs_count += 1
                print('Copied timelog for task: ' + source_task_name + ' [' + time + ' - ' + to_time_str + ']')
        else:
            # Create the new task and log the time for it
            task_post_data = json.dumps({
                'todo-item': {
                    'content': source_task_name,
                    'creator-id': dest_user_id,
                    'responsible-party-id': dest_user_id,
                }
            })
            new_task_id = api.create_task(dest_url, dest_tlid, task_post_data, dest_user, dest_pass)
            if new_task_id is not None:
                # Add the new task to the task list
                dest_task_list[source_task_name] = new_task_id
                print('Created new task: ' + source_task_name)
                if api.log_time(dest_url, new_task_id, timelog_post_data, dest_user, dest_pass) == 'OK':
                    logs_count += 1
                    print('Copied timelog for task: ' + source_task_name + ' [' + time + ' - ' + to_time_str + ']')

# Print report
if len(source_timelogs) == 0:
    print('[WARNING]: No timelogs in the source yet.')
if logs_count == 0:
    print('[INFO] All timelogs are up to date!')
