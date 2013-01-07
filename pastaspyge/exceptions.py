# encoding: utf-8

class NotFound(Exception):
    pass


class IsDir(Exception):
    pass


class InvalidConfig(Exception):
    pass


class AlreadyExists(Exception):
    pass