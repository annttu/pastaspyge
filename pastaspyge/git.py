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


class GitError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Git(object):
    """
    Git repository instance
    """
    def __init__(self, repository, remote=None):
        self.git_binary = GIT_BINARY
        self.repository = repository
        self.git_dir = os.path.join(self.repository, '.git')
        self.remote = remote

    def _run(self, *args):
        """
        Run git commands listed on *args

        @raise GitError: Raised on git error

        @return: tuple (stdout, stderr)
        """
        env_save = {'GIT_WORK_TREE': None, 'GIT_DIR': None}
        if 'GIT_DIR' in os.environ:
            env_save['GIT_DIR'] = os.environ['GIT_DIR']
        os.environ['GIT_DIR'] = os.path.join(self.repository, '.git')
        if 'GIT_WORK_TREE' in os.environ:
            env_save['GIT_WORK_TREE'] = os.environ['GIT_WORK_TREE']
        os.environ['GIT_WORK_TREE'] = self.repository
        args = [self.git_binary, '--git-dir=%s' % self.git_dir] + list(args)
        a = Popen(args, stdout=PIPE, stderr=PIPE)
        retval = a.wait()
        try:
            ret = a.communicate()
        except:
            ret = (None, None)
        if retval != 0:
            print("Stdout:")
            print(ret[0])
            print("Stderr:")
            print(ret[1])
            raise GitError("%s %s return value %d" % (args[0], args[1],
                                                      retval))
        for i in env_save:
            if env_save[i] is None:
                del os.environ[i]
            else:
                os.environ[i] = env_save[i]
        return ret

    def current_branch(self):
        """
        Get active branch name

        @return: branch name
        @rtype: string

        @raise GitError: Raised on git error
        """
        stdout, stderr = self._run('rev-parse', '--abbrev-ref', 'HEAD')
        if stdout is not None:
            return stdout.strip()
        else:
            raise GitError("Got error %s while reading current branch" %
                           stderr)
        return None

    def checkout(self, branch="master"):
        """
        Git checkout to different branch

        TODO: implement -b (create branch before checkout)

        @param branch: branch to checkout
        @type branch: text

        @raise GitError: after unsuccessful checkout
        """
        (stdout, stderr) = self._run('checkout', branch)
        if not stderr:
            raise GitError('Checkout returned error %s' % stderr)
        return False

    def pull(self, remote="origin", remote_branch="master",
             local_branch="master"):
        """
        Pull changes from remote repository
        @param remote: Remote name
        @type remote: string
        @param remote_branch: Remote branch
        @type remote: string
        @param local_branch: Local branch where to push
        @return: None
        """
        current_branch = self.current_branch()
        if current_branch != local_branch:
            self.checkout(local_branch)
        self._run('pull', remote, remote_branch)
        if current_branch != local_branch:
            # Go back to orginal branch
            self.checkout(current_branch)

    def push(self, remote="origin", remote_branch="master",
             local_branch="master"):
        """
        Push changes to remote repository
        @param remote: Remote name
        @type remote: string
        @param remote_branch: Remote branch
        @type remote: string
        @param local_branch: Local branch where to push
        @type local_branch: string
        @return: None
        """
        (stdout, stderr) = self._run('push', remote, "%s:%s" % (local_branch,
                                                                remote_branch))
        if stderr is None:
            logger.debug("git push output: %s" % stdout)
            return True
        raise GitError("Git push returned error: %s" % stderr)

    def add(self, path):
        """
        Add file to repository. File should exist and locate inside
        git repository.

        @param path: Path to file
        @type path: string

        @raise GitError: If file is outside git repository or does not exists.

        @return: True after successful git add
        """
        abspath = os.path.abspath(path)
        if not abspath.startswith(self.repository):
            raise GitError('File %s is outside git repository!' % path)
        elif os.path.exists(abspath) is False:
            raise GitError('File %s does not exist!' % path)
        (stdout, stderr) = self._run('add', abspath)
        if not stderr:
            logger.debug("git add output: %s" % stdout)
            return True
        raise GitError("git add returns error: %s" % stderr)

    def rm(self, path, cached=False, recursive=False):
        """
        Remove file from repository. File should exist and locate inside
        git repository.

        @param path: Path to file
        @type path: string
        @param cached: if True, removes file only from git index, not from disk.
        @type cached: boolean

        @param recursive: Remove files recursively
        @type recursive: boolean

        @raise GitError: If file is outside git repository or does not exists.

        @return: True after successful git rm
        @rtype: boolean
        """
        abspath = os.path.abspath(path)
        if not abspath.startswith(self.repository):
            raise GitError('File %s is outside git repository!' % path)
        elif os.path.exists(abspath) is False:
            raise GitError('File %s does not exist!' % path)
        elif os.path.isfile(abspath) is False and \
                os.path.isdir(abspath) is True:
            # TODO: check if directory is non empty
            raise GitError('Cannot remove directory without recurse' % path)
        if cached:
            (stdout, stderr) = self._run('rm', '--cached', abspath)
        else:
            (stdout, stderr) = self._run('rm', abspath)
        if not stderr:
            logger.debug("git rm output: %s" % stdout)
            return True
        raise GitError("git rm returs error: %s" % stderr)

    def diff(self, new=None, old=None, name_only=False, diff_filter=None):
        """
        Get diff between new and old branch. If new and old is None, get
        uncommitted changes.

        @param: new: Newest branch to use in compare
        @type new: string
        @param old: Oldedst branch to use in compare
        @type old: string

        @param name_only: Get only names of changed files
        @type name_only: boolean

        @param diff_filter: filter changes, available filters are:
             A              Added
             M              Modifed
             D              Deleted
        @type diff_filter: String
        @return: git output
        @rtype: string

        @raise GitError: Raised if diff returns error
        """
        args = ['diff', '--name-only']
        if old in ['HEAD', '^HEAD']:
                args.append(old)
        elif new and old:
            args.append("%s...%s" % (old, new))
        if diff_filter:
            args.append('--diff-filter=%s' % diff_filter)
        (stdout, stderr) = self._run(*args)
        if not stderr:
            return stdout
        raise GitError("Git diff returns error: %s" % stderr)

    def fetch(self, remote="origin", remote_branch="master",
              local_branch="master"):
        """
        Git fetch content from remote branch to local branch

        @param remote: Remote name
        @type remote: string
        @param remote_branch: Remote branch
        @type remote: string
        @param local_branch: Local branch where to fetch
        @type local_branch: string
        @return: None
        """
        current_branch = self.current_branch()
        if current_branch != local_branch:
            self.checkout(local_branch)
        (stdout, stderr) = self._run('fetch', remote, remote_branch)
        if current_branch != local_branch:
            self.checkout(current_branch)
        logger.debug("git fetch output: %s" % stderr)
        return True

    def reset(self, remote="origin", branch="master", hard=None):
        """
        Git (hard) reset repository to remote/branch

        @param remote: Remote name
        @type remote: string
        @param branch: Remote branch
        @type remote: string
        @param hard: use hard reset
        @type hard: boolean
        @return: True if successfully reseted
        """
        args = ['reset']
        if hard is True:
            args.append('--hard')
        elif hard is False:
            args.append('--soft')
        args.append("%s/%s" % (remote, branch))
        (stdout, stderr) = self._run(*args)
        if not stderr:
            logger.debug("git reset output: %s" % stdout)
            return True
        raise GitError("git reset returs error: %s" % stderr)

    def commit(self, msg):
        """
        Do git commit with message

        @param msg: Commit message
        @type msg: string
        @return: True after successful commit
        """
        (stdout, stderr) = self._run('commit', '-m', msg)
        if not stderr:
            logger.debug("git commit output: %s" % stdout)
            return True
        raise GitError("git commit returs error: %s" % stderr)

    def changed_files(self, new=None, old=None):
        """
        Get changed files between new and old commits

        @param new: Newest branch to use in compare
        @type new: string
        @param old: Oldedst branch to use in compare
        @type old: string

        @return: tuple ([updated or new files], [deleted files])
        """
        added = []
        deleted = []
        # get added files
        stdout = self.diff(new=new, old=old, name_only=True, diff_filter='A,M')
        for f in stdout.splitlines():
            f = f.strip().strip(b'"').decode("unicode_escape")
            added.append(f.encode("iso-8859-1").decode("utf-8"))
        # get deleted files
        stdout = self.diff(new=new, old=old, name_only=True, diff_filter='D')
        for f in stdout.splitlines():
            f = f.strip().strip(b'"').decode("unicode_escape")
            deleted.append(f.encode("iso-8859-1").decode("utf-8"))
        return (added, deleted)

# Map Git functions to global instance
git_instance = Git(REPO_DIR)

changed_files = git_instance.changed_files
add = git_instance.add
rm = git_instance.rm
pull = git_instance.pull
push = git_instance.push
diff = git_instance.diff
fetch = git_instance.fetch
reset = git_instance.reset
checkout = git_instance.checkout
current_branch = git_instance.current_branch
