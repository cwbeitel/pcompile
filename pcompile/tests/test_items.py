#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pcompile.items import NameRegistry, Items, min_container_type
from pcompile.tests.test_context import TestContext
from pcompile import ureg
import json
from pcompile.solution import Solution


class TestNameRegistry(unittest.TestCase):

    def test_init(self):
        nr = NameRegistry()

    def test_generate_name(self):
        name = NameRegistry().generate()

    def test_new(self):
        name = NameRegistry().new()


class TestItems(unittest.TestCase):

    def test_init(self):
        items = Items()

    def test_find(self):

        tc = TestContext()

        items = Items()
        well = items.allocate(tc.env, '96-pcr')
        assert isinstance(well, dict)

        # When more than 96 wells are allocated, a second plate is allocated,
        # but not before.
        for i in range(1,97):
            items.allocate(tc.env, '96-pcr')
        assert len(items.containers) == 2

        # Check that the objects were reffed in the process of being
        # allocated.
        assert len(tc.env.protocol.as_dict()['refs'].keys()) == 2

class TestHelpers(unittest.TestCase):

    def test_min_container_type(self):

        assert min_container_type(1*ureg.microliter) == "96-pcr"
        assert min_container_type(1000*ureg.microliter) == "micro-1.5"



'''
from pcompile.solution import Component
from pcompile.items import ContainerPool, Container

class TestContainer(unittest.TestCase):

    def test_something(self):

        ct1 = Container(name='happy', ctype='96-pcr')
        ct2 = Container(name='lucky', ctype='384-pcr')
        ct3 = Container(name='sparkles', ctype='1.5-micro')

        cp = ContainerPool(containers=[ct1, ct2, ct3])

        assert cp.find('sparkles').ctype == '1.5-micro'

'''

if __name__ == '__main__':

    unittest.main()




