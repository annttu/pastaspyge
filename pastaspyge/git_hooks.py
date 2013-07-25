# encoding: utf-8

# Git hooks for pastaspyge

from pastaspyge.git import git_pull, changed_files
from pastaspyge import Pasta

import os
import sys
import logging

logger = logging.getLogger()


def not_hook():
    print("This script should be run as post-receive hook")
    print("Unclean exit")
    sys.exit(1)


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
        logging.error("Directory %s does not exists" % git_dir)
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
