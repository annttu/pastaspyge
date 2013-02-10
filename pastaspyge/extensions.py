# encoding: utf-8

from jinja2 import nodes
from jinja2.ext import Extension

class LastModifed(Extension):
    """
    "lastmodifed" template tag, gets file last modifed date
    """
    tags = set(['lastmodifed'])
    def __init__(self, environment):
        self.environment = environment

    def parse(self, parser):
        token = parser.stream.next()
        return nodes.Output([self.call_method('_render')]).set_lineno(token.lineno)

    def _render(self):
        return "<!-- asdf -->"

class CountCharsExtension(Extension):
    """
    Counts chars
    """

    tags = set(['countchars'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endcountchars'], drop_needle=True)
        return [
            nodes.Assign(nodes.Name('char_count', 'store'),
                    nodes.Const(unicode(len(body[0].nodes[0].data)))
            ),
            nodes.CallBlock(
                self.call_method('_return', [], [], None, None),
                [], [], body,
            ).set_lineno(lineno)]

    def _return(self, caller=None):
        return caller()



countchars = CountCharsExtension
lastmodifed=LastModifed
