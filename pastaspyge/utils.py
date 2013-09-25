# encoding: utf-8

import sys
import os

def activate_env(path):
    path = os.path.join(path, 'bin/activate_this.py')
    with open(path) as f:
        global_vars = sys._getframe(1).f_globals
        local_vars = sys._getframe(1).f_locals
        local_vars['__file__'] = path
        code = compile(f.read(), path, 'exec')
        exec(code, global_vars, local_vars)
