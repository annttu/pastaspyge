#!/usr/bin/env python
# encoding: utf-8

import jinja2
import os
import sys
import logging
import codecs
from datetime import datetime

from pastaspyge.config import Config
from pastaspyge.exceptions import NotFound, IsDir, InvalidConfig, AlreadyExists
from pastaspyge.extensions import LastModifed

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
        extensions = [LastModifed]
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
        modtime = datetime.fromtimestamp(os.path.getmtime(os.path.abspath(fpath)))
        content = template.render(config=self.config, environ=self.jinjaenv,
                                  last_modifed=modtime)
        return content

    def find_dynamic_files(self):
        paths = []
        path = self.config.dynamic_path
        for p in os.walk(path):
            for f in p[2]:
                paths.append(os.path.join(p[0], f)[len(path):]) 
        return paths

    def generate_file(self, f, overwrite=True):
        self._write_output(f, self.generate_dynamic(f), overwrite=overwrite)

    def generate_all(self):
        retval = []
        for f in self.find_dynamic_files():
            retval.append(f)
            self.generate_file(f,overwrite=True)
        return retval

    def _write_output(self, f, content, overwrite=True):
        fpath = os.path.join(self.config.output_path, f.lstrip('/'))
        if os.path.exists(fpath) and os.path.isfile(fpath) and not overwrite:
            self.log.error('File %s already exist' % fpath)
            AlreadyExists('File %s already exist' % fpath)
        if os.path.exists(fpath) and not os.path.isfile(fpath):
            self.log.error('Path %s already exist and is not file!' % fpath)
            raise IsDir('Path %s already exist and is not file!' % fpath)
        try:
            f = codecs.open(fpath, 'w', 'utf-8')
            f.write(content)
            f.close()
        except IOError:
            self.log.error('Cannot write to file %s' % fpath)
            raise

    def copy_files(self, files):
        if not self.config.document_root:
            raise InvalidConfig('To copy files, document_root must be set')
        if not os.path.isdir(self.config.document_root):
            raise InvalidConfig('To copy files, document_root must exist')
        for f in files:
            sourcepath = os.path.abspath(f)
            if not os.path.isfile(sourcepath):
                self.log.error('Path %s does not exist!' % sourcepath)
                raise IsDir('Path %s does not exist!' % sourcepath)
            source = codecs.open(sourcepath, 'r', 'utf-8')
            if f.startswith('static/'):
                f = f[len('static/'):]
            else:
                f = f[len('output/'):]
            destpath = os.path.join(self.config.document_root, f)
            if not os.path.isdir(os.path.dirname(destpath)):
                try:
                    os.mkdir(os.path.dirname(destpath))
                except IOError as e:
                    self.log.exception(e)
                    raise
            if os.path.exists(destpath) and not os.path.isfile(destpath):
                self.log.error('Path %s already exist and is not file!' % destpath)
                raise IsDir('Path %s already exist and is not file!' % destpath)
            dest = codecs.open(destpath, 'w', 'utf-8')
            try:
                dest.write(source.read())
                source.close()
                dest.close()
                self.log.info("Copied %s -> %s" % (sourcepath, destpath))
            except IOError as e:
                self.log.exception(e)

    def delete_files(self, files):
        if not self.config.document_root:
            raise InvalidConfig('To copy files, document_root must be set')
        if not os.path.isdir(self.config.document_root):
            return
        for f in files:
            destpath = os.path.join(self.config.document_root, f)
            try:
                os.remove(destpath)
                self.log.info("Removed file %s" % destpath)
            except OSError:
                os.rmdir(destpath)
                self.log.info("Removed dir %s" % destpath)
