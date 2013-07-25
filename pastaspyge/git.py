#!/usr/bin/env python3

"""
Git related functions
"""

import os
import sys
from subprocess import Popen, PIPE
import logging
from pastaspyge import Pasta

logging.basicConfig()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


REPO_DIR = os.getcwd()
GIT_BINARY = 'git'


def not_hook():
    print("This script should be run as post-receive hook")
    print("Unclean exit")
    sys.exit(1)


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


def post_receive(repo_dir, document_root, path_prefix=''):
    if 'GIT_DIR' not in os.environ:
        not_hook()
    git_dir = os.path.abspath(os.environ['GIT_DIR'])
    a = sys.stdin.readlines()
    if len(a) == 1:
        a = a[0][:-1].split()
        old_commit = a[0]
        new_commit = a[1]
    else:
        not_hook()
    if not os.path.isdir(repo_dir):
        logging.error("Directory %s does not exists" % repo_dir)
        sys.exit(1)
    os.chdir(repo_dir)
    os.environ['GIT_DIR'] = os.path.join(repo_dir, '.git')
    os.environ['GIT_WORK_TREE'] = repo_dir
    git_pull()
    changed, delete = changed_files(new_commit, old_commit)
    remove = []
    for d in delete:
        if d.startswith(os.path.join(path_prefix, 'dynamic/')):
            d = d[len(os.path.join(path_prefix, 'dynamic/'))-1:]
            remove.append(d)
        elif d.startswith(os.path.join(path_prefix, 'static/')):
            d = d[len(os.path.join(path_prefix, 'static/'))-1:]
            remove.append(d)
    delete = remove
    del remove
    pasta = Pasta(root=repo_dir, document_root=document_root)
    copy = []
    for f in changed:
        if f.startswith(os.path.join(path_prefix, 'dynamic/')):
            # dynamic change
            f = f[len(os.path.join(path_prefix, 'dynamic/')):]
            pasta.generate_file(f, overwrite=True)
            copy.append(os.path.join(path_prefix, 'output', f))
        elif f.startswith(os.path.join(path_prefix, 'static/')):
            copy.append(os.path.join(path_prefix, f))
        elif f.startswith(os.path.join(path_prefix, 'templates/')):
            # template changed, regenerate everything
            for t in pasta.generate_all():
                copy.append(os.path.join(path_prefix, 'output', t))
            break
    print("Copying files %s" % (copy,))
    pasta.copy_files(copy)
    print("Deleting files %s" % (delete,))
    pasta.delete_files(delete)
