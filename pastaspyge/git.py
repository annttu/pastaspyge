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


REPO_DIR=os.getcwd()

def not_hook():
    print("This script should be run as post-receive hook")
    print("Unclean exit")
    sys.exit(1)


def run_git(args):
    logging.debug("args: %s" % repr(args))
    a = Popen(args, stdout=PIPE, stderr=PIPE)
    if a.wait() != 0:
        logging.error("%s returncode nonzero" % args[0])
        logging.error(a.communicate()[1])
        return (None, None)
    return a.communicate()

def git_pull():
    run_git(['git','checkout','master'])
    run_git(['git','pull'])

def changed_files(new=None, old=None):
    args = ['git', 'diff','--name-only']
    if new and old:
        args.append("%s...%s" % (old, new))
    retval = []
    (stdout, stderr) = run_git(args)
    if stderr:
        log.error("stderr")
    for f in stdout.splitlines():
        f = f.strip().strip(b'"').decode("unicode_escape")
        retval.append(f.encode("iso-8859-1").decode("utf-8"))
    return retval

def post_receive(repo_dir, path_prefix=''):
    if 'GIT_DIR' not in os.environ:
        not_hook()
    git_dir = os.path.abspath(os.environ['GIT_DIR'])
    a = sys.stdin.readlines()
    if len(a) == 1:
        a = a[0][:-1].split()
        old_commit=a[0]
        new_commit=a[1]
        ref=a[2]
        #print("old: %s, new: %s, ref: %s" % (old_commit, new_commit, ref))
    else:
        not_hook()
    if not os.path.isdir(repo_dir):
        logging.error("Directory %s does not exists" % repo_dir)
        sys.exit(1)
    os.chdir(repo_dir)
    os.environ['GIT_DIR'] = os.path.join(repo_dir, '.git')
    os.environ['GIT_WORK_TREE'] = repo_dir
    git_pull()
    changed = changed_files(new_commit, old_commit)
    pasta = Pasta(root=repo_dir)
    copy = []
    copy_all = False
    for f in changed:
        if f.startswith(os.path.join(path_prefix, 'dynamic/')):
            # dynamic change
            f = f[len('dynamic/'):]
            pasta.generate_file(f, overwrite=True)
            copy.append(os.path.join(path_prefix, 'output', f))
        elif f.startswith(os.path.join(path_prefix, 'static/')):
            copy.append(os.path.join(path_prefix, f))
        elif f.startswith(os.path.join(path_prefix, 'templates/')):
            # template changed, regenerate everything
            pasta.generate_all()
            copy_all = True
            break
    print("Copying files %s" % (copy,))
