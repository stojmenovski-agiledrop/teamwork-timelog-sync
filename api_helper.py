#!/usr/bin/python3
import requests
import json

# TEAMWORK API V1 ENDPOINTS
USER_ENDPOINT = '/me.json'
TIMELOG_ENDPOINT = '/time_entries.json'
TASKS_ENDPOINT = '/tasks.json'


def get_user_id(url, user, password):
    person = requests.get(
        url + USER_ENDPOINT,
        auth=(user, password)
    ).json()['person']

    return person['id']


def get_timelogs(url, user, password, user_id, f_date, t_date):
    response = requests.get(
        url + TIMELOG_ENDPOINT + '?fromdate=' + f_date + '&todate=' + t_date + '&userId=' + user_id,
        auth=(user, password)
    ).json()

    if 'STATUS' in response and response['STATUS'] == 'OK':
        return response['time-entries']
    else:
        raise Exception('Unable to retrieve the time logs for user: ' + user)


def get_task_list(url, user, password, user_id):
    response = requests.get(
        url + TASKS_ENDPOINT + '?responsible-party-ids=' + user_id,
        auth=(user, password)
    ).json()

    if 'STATUS' in response and response['STATUS'] == 'OK':
        tasks = {}
        tasks_response = response['todo-items']
        for t in tasks_response:
            key, value = t['content'], t['id']
            tasks[key] = value
        return tasks
    else:
        raise Exception('Unable to retrieve the tasks for user: ' + user)


def create_task(url, tlid, data, user, password):
    response = requests.post(
        url + '/tasklists/' + str(tlid) + TASKS_ENDPOINT,
        data=data,
        auth=(user, password)
    )
    if response.status_code == 201:
        return json.loads(response.content)['id']
    else:
        raise Exception('Unable to create task: ' + str(data['content']))


def log_time(url, tid, data, user, password):
    response = requests.post(
        url + '/tasks/' + str(tid) + TIMELOG_ENDPOINT,
        data=data,
        auth=(user, password)
    )
    if response.status_code == 201:
        return 'OK'
    else:
        raise Exception('Unable to create the time logs for task: ' + str(tid))
