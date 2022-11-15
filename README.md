# Teamwork Timelog Sync
This script will sync timelogs from one Teamwork account to another.

## Installation
The script is written in Python and doesn't require any additional dependencies other than a working Python 3 installation.

## Configuration
Create a config.yml file in the project root and copy the contents from the config_example.yml. 
Set the following values:

- url - this is the base URL for the project;
- username - your Teamwork email;
- password - your Teamwork password;
- task_list_id - this is only needed on the destination account, can be found in the tasklist url eg. https://agiledrop.teamwork.com/#/tasklists/12345678.

## Running

```commandline
python3 timelog_sync.py
```

You can also make the script executable in order not to type python3 every time you run it.
```commandline
chmod +x timelog_sync.py
./timelog_sync.py
```
Currently, the script will sync the timelogs for the same day by default. You can also pass the --yesterday parameter to sync the timelogs for yesterday.

```commandline
./timelog_sync.py --yesterday
```

You can also pass the --date argument in order to specify a specific date. Note the date should be in the YYYY-MM-DD format.
```commandline
./timelog_sync.py --date 2022-11-15
```

TODO: there will also be an option to specify a date range.

## Limitations
Before the first run the tasks in the destination must be assigned to your account.