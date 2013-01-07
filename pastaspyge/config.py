#!/usr/bin/env python
# encoding: utf-8

import os
from pastaspyge.exceptions import InvalidConfig

class Config(object):
    def __init__(self, root=None, document_root=None):
        self.document_root = document_root
        if root:
            self.root = os.path.abspath(root)
        else:
            self.root = os.path.abspath('tests/')
        if not os.path.isdir(self.root):
                raise InvalidConfig('Directory %s does not exist!' % (
                                                                self.root,))
        self.template_path = os.path.join(self.root, 'templates/')
        self.static_path = os.path.join(self.root, 'static/')
        self.dynamic_path = os.path.join(self.root, 'dynamic/')
        self.output_path = os.path.join(self.root, 'output/')
        dirs = [self.template_path, self.static_path, 
                 self.dynamic_path, self.output_path]
        for i in dirs:
            if not os.path.isdir(i):
                raise InvalidConfig('Directory %s does not exist!' % i)
        
        self.prefix = ''