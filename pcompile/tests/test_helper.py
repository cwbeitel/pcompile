#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from pcompile.helper import make_dottable_dict, serialize, unserialize, ddiff, to_pint
from pcompile import ureg

class TestMakeDottableDict(unittest.TestCase):

    def test_init(self):

    	d = {'k1':{'find':'me'},
    		 'k2':{'k21':[{'find':'metoo'}],
				   'k22':{}},
    		 'k3':[{'a':'b'}]}

    	d = make_dottable_dict(d)

    	assert d.k1.find == 'me'

    	assert d.k2.k21[0].find == 'metoo'

        assert d.k3[0].a == 'b'


class TestSerialize(unittest.TestCase):

    def setUp(self):

        self.serialize_test_cases = [[{'key':'value'},'key:value'],
                                    [{'key':'value', 'key2':'value2'},'key:value;key2:value2']]

    def test_serialize(self):

        for c in self.serialize_test_cases:

            # Because key:value,key2:value2 == key2:value2,key:value
            assert unserialize(serialize(c[0])) == c[0]

    def test_unserialize(self):

        for c in self.serialize_test_cases:

            assert unserialize(c[1]) == c[0]


class TestDDiff(unittest.TestCase):

    def test_ddiff(self):

        correct = {'key':1*ureg.microliter}

        assert ddiff({'key':1*ureg.microliter},{'key':2*ureg.microliter}) == correct


class TestToPint(unittest.TestCase):

    def test_to_pint(self):

        assert to_pint('1:microliter') == 1*ureg.microliter
        assert to_pint(1*ureg.microliter) == 1*ureg.microliter



if __name__ == '__main__':

    unittest.main()




