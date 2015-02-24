#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

import argparse
import os
import argcomplete
import sqlite3
import datetime


TODO_TXT = os.path.expanduser('~/todo.txt')
TIMETRACKER_DB = os.path.expanduser('~/timetracker.db')


class TimeTrackerDB(object):

    def __init__(self):
        self.db = sqlite3.connect(TIMETRACKER_DB)
        self.init_db()

    def init_db(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS
                time_tracking (task TEXT,
                               project TEXT,
                               start DATETIME,
                               end DATETIME)""")

    def start_task(self, task, project):
        self.db.execute("""
            INSERT INTO
                time_tracking (task, project, start)
            VALUES
                (?, ?, ?)""", (task, project, datetime.datetime.now()))
        self.db.commit()

    def stop_in_progress(self):
        self.db.execute("""
            UPDATE
                time_tracking
            SET
                end = ?
            WHERE
                end IS NULL""", (datetime.datetime.now(),))
        self.db.commit()

    def stop_task(self, task, project):
        self.db.execute("""
            UPDATE
                time_tracking
            SET
                end = ?
            WHERE
                end IS NULL
                task = ? AND
                project = ?""", (datetime.datetime.now(), task, project))
        self.db.commit()


class TodoTxt(object):

    def __init__(self, filename=TODO_TXT, mode='r'):
        self.filename = filename
        self.mode = mode
        self.f = None

    def __enter__(self):
        self.f = open(self.filename, self.mode)
        return self.f

    def __exit__(self, *args, **kwargs):
        self.f.close()


def TaskCompleter(prefix, **kwargs):
    projects = []
    with TodoTxt(mode='r') as t:
        for line in t:
            if line.startswith('x'):
                continue
            tokens = line.split(' ')
            project = []
            for token in tokens:
                if token.startswith('+') or token.startswith('@'):
                    candidate = ' '.join(project)
                    if prefix in candidate:
                        projects.append(candidate)
                    break
                project.append(token)
    return projects


def ProjectCompleter(prefix, **kwargs):
    project_names = []
    with TodoTxt(mode='r') as t:
        for line in t:
            if line.startswith('x'):
                continue
            tokens = line.split(' ')
            for token in tokens:
                if token.startswith('+'):
                    project_name = token[1:]
                    if project_name.startswith(prefix):
                        project_names.append(project_name)
    return project_names


def start_func(args):
    task_db = TimeTrackerDB()
    task_db.stop_in_progress()
    task_db.start_task(args.task, args.project)


def done_funct(args):
    pass


def ls_func(args):
    pass


def parse_args():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    start = subparsers.add_parser('start')
    start.add_argument('task').completer = TaskCompleter
    start.add_argument('-p', '--project').completer = ProjectCompleter
    start.set_defaults(func=start_func)

    finish = subparsers.add_parser('done')
    finish.add_argument('task').completer = TaskCompleter
    finish.set_defaults(func=done_func)

    ls = subparsers.add_parser('ls')
    ls.add_argument('-p', '--project').completer = ProjectCompleter
    ls.set_defaults(func=ls_func)

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
