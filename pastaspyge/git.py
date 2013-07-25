#!/usr/bin/env python3

"""
Git related functions
"""

import os
from subprocess import Popen, PIPE
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


REPO_DIR = os.getcwd()
GIT_BINARY = 'git'


def run_git(args):
    args = [GIT_BINARY] + list(args)
    a = Popen(args, stdout=PIPE, stderr=PIPE)
    if a.wait() != 0:
        logging.error("%s returncode nonzero" % args[0])
        logging.error(a.communicate()[1])
        return (None, None)
    return a.communicate()


def git_pull():
    run_git(['checkout', 'master'])
    run_git(['pull'])


def git_add(file_):
    a, b = run_git(['add', str(file_)])
    if a is None and b is None:
        return False
    return True


def git_rm(file_):
    a, b = run_git(['rm', str(file_)])
    if a is None and b is None:
        return False
    return True


def changed_files(new=None, old=None):
    """Get added and deleted files between new and old commits
    returns tuple (added, deleted)"""
    args = ['diff', '--name-only']
    if new and old:
        args.append("%s...%s" % (old, new))
    added = []
    deleted = []
    # get added files
    (stdout, stderr) = run_git(args + ['--diff-filter=A,M'])
    if stderr:
        logger.error("stderr")
    for f in stdout.splitlines():
        f = f.strip().strip(b'"').decode("unicode_escape")
        added.append(f.encode("iso-8859-1").decode("utf-8"))
    # get deleted files
    (stdout, stderr) = run_git(args + ['--diff-filter=D'])
    if stderr:
        logger.error("stderr")
    for f in stdout.splitlines():
        f = f.strip().strip(b'"').decode("unicode_escape")
        deleted.append(f.encode("iso-8859-1").decode("utf-8"))
    return (added, deleted)
