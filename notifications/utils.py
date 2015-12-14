# -*- coding: utf-8 -*-

import sys
if sys.version > '3':
    long = int


def slug2id(slug):
    return long(slug) - 110909


def id2slug(id):
    return id + 110909
