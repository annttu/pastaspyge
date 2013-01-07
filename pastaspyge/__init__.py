#!/usr/bin/env python
# encoding: utf-8

import jinja2
import os
import sys
import logging
import codecs
from pastaspyge.config import Config
from pastaspyge.exceptions import NotFound, IsDir, InvalidConfig, AlreadyExists

class Pasta(object):
    def __init__(self, **kwargs):
        self.config = Config(**kwargs)
        self.log = logging.getLogger()
        self.jinjaenv = None
        self.template_loader()


    def template_loader(self):
        """
        Load jinja2 template
        """
        path = [jinja2.loaders.FileSystemLoader(self.config.template_path),
                jinja2.loaders.FileSystemLoader(self.config.dynamic_path)]
        loader = jinja2.loaders.ChoiceLoader(path)
        extensions = []
        self.jinjaenv = jinja2.Environment(loader=loader,extensions=extensions)


    def generate_dynamic(self, template_file):
        """
        Render dynamic page
        """
        fpath = os.path.join(self.config.dynamic_path,
                             template_file.lstrip('/'))
        if not os.path.exists(fpath):
            raise NotFound('File not found: %s' % fpath)
        elif os.path.isdir(fpath):
            raise IsDir('Path is dir: %s' % fpath)
        template = self.jinjaenv.get_template(template_file)
        content = template.render(config=self.config, environ=self.jinjaenv)
        return content

    def find_dynamic_files(self):
        paths = []
        path = self.config.dynamic_path
        for p in os.walk(path):
            for f in p[2]:
                paths.append(os.path.join(p[0], f)[len(path)-1:]) 
        return paths

    def generate_file(self, f, overwrite=True):
        self._write_output(f, self.generate_dynamic(f), overwrite=overwrite)

    def generate_all(self):
        for f in self.find_dynamic_files():
            print("%s"% f)
            self.generate_file(f,overwrite=True)

    def _write_output(self, f, content, overwrite=True):
        fpath = os.path.join(self.config.output_path, f.lstrip('/'))
        if os.path.exists(fpath) and os.path.isfile(fpath) and not overwrite:
            self.log.error('File %s already exist' % fpath)
            AlreadyExists('File %s already exist' % fpath)
        if os.path.exists(fpath) and not os.path.exists(fpath):
            self.log.error('Path %s already exist and is not file!' % fpath)
            raise IsDir('Path %s already exist and is not file!' % fpath)
        try:
            f = codecs.open(fpath, 'w', 'utf-8')
            f.write(content)
            f.close()
        except IOError:
            self.log.error('Cannot write to file %s' % fpath)
            raise
